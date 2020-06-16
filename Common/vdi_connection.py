import os
import subprocess
import time
import yaml
import shutil
import pyautogui
from Common import common_function
import datetime
from Common import picture_operator
import re
from Common.exception import *
import traceback
from Common.log import Logger
from Common.socket_client import *
import socket

log = Logger()
config = os.path.join(os.getcwd(), 'Test_Data', 'td_multiple_display', 'vdi_server_config.yml')
with open(config, 'r') as f:
    vdi_config = yaml.safe_load(f)


class VDIConnection:
    def __init__(self, user, domain='sh', password="Shanghai2010", **kwargs):
        self.domain = domain
        self.user = user
        self.password = password
        self.cert = vdi_config['cert']
        self.vdi = None
        self.set_dic = {}
        self.grep = None
        self.domain_list = []

    def import_cert(self):
        time.sleep(1)
        log.info("start import certificate")
        rootca_pem_1 = os.path.exists("/etc/ssl/certs/ROOTCA.pem")
        if rootca_pem_1:
            log.info("certificate is already exist")
            return True
        else:
            log.info("certificate not exist, start install cert")
            shutil.copy(os.path.join(os.getcwd(), 'Test_Utility', 'ROOTCA.pem'),
                        '/usr/local/share/ca-certificates/ROOTCA.pem')
            time.sleep(0.2)
            c = os.path.exists("/usr/local/share/ca-certificates/{}".format(self.cert))
            if not c:
                log.error('copy cert fail')
                return False
            log.info('copy cert success')
            subprocess.getstatusoutput("/usr/bin/hptc-cert-mgr --apply")
            time.sleep(4)
            rootca_pem_2 = os.path.exists("/etc/ssl/certs/ROOTCA.pem")
            if not rootca_pem_2:
                log.error('install certificates fail')
                return False
            else:
                log.info('install certificates success')
                time.sleep(1)
                return True

    @staticmethod
    def vdi_connection_id(vdi):
        """
        :return: ['{05065368-9f7b-42c5-be2c-89a40ce0a78c}']
        """
        vdi_id = subprocess.getoutput("mclient --quiet get root/ConnectionType/{}/connections".format(vdi)).splitlines()
        id_list = []
        for i in vdi_id:
            id_list.append(i.split('/')[-1])
        return id_list

    @staticmethod
    def check_vdi_server_connection(vdi_server):
        log.info("start ping '{}', about need 15s".format(vdi_server))
        try:
            d = subprocess.getoutput("ping {} -c 4".format(vdi_server))
            if 'received' in d:
                log.info("ping '{}' successful".format(vdi_server))
                return True
            else:
                log.error("ping '{}' fail".format(vdi_server))
                return False
        except:
            log.error("the network or VDI server error.")
            return False

    @staticmethod
    def delete_vdi(vdi):
        log.info("start delete {} uuid".format(vdi))
        citrix_id = VDIConnection.vdi_connection_id(vdi)
        if len(citrix_id) > 0:
            for c_id in citrix_id:
                os.system("mclient --quiet delete root/ConnectionType/{}/connections/{}".format(vdi, c_id))
                os.system("mclient commit")
                time.sleep(0.2)
            if len(VDIConnection.vdi_connection_id('vdi')) == 0:
                log.info("delete {} uuid success".format(vdi))
        else:
            log.info("not exist {}, not need to delete".format(vdi))
            pass

    @staticmethod
    def create_vdi(vdi):
        log.info("start create {} uuid".format(vdi))
        time.sleep(1)
        os.system("connection-launcher --create {}".format(vdi))
        time.sleep(1)

    @staticmethod
    def domains_to_ip_list(domains):
        ip_list = []
        for domain in domains:
            try:
                ip_list.append(socket.getaddrinfo(domain, None)[0][4][0])
            except:
                traceback.print_exc()
        return ip_list

    @staticmethod
    def generate_socket(ip, port):
        return SocketClient(ip, port)

    @staticmethod
    def check_vdi_logon_status(pic):
        status = picture_operator.get_position_by_pic(pic)
        if status:
            log.info("logon vdi desktop success, check by picture")
            return True
        else:
            log.error("logon vdi desktop fail, check by picture")
            return False

    def set_vdi(self, vdi_id, settings, **kwargs):
        command = "mclient --quiet set root/ConnectionType/"
        if settings:
            for k, v in settings.items():
                cmd = command + "{}/connections/{}/{} {}".format(self.vdi, vdi_id, k, v)
                os.system(cmd)
        os.system("mclient commit")

    def connect_vdi(self, vdi_id):
        log.info("connect {} desktop".format(self.vdi))
        time.sleep(2)
        os.popen("connection-mgr start {}".format(vdi_id))


    def close_windows(self, windows, **kwargs):
        '''
        :param windows: list from func:get_windows
        :param kwargs:
                case: int,default 1, 0(close all windows);1(close error windows);2(diy close windows)
                filter: list, you should set case=2 and choose window you want to close
        '''
        case = kwargs.get("case", 1)
        cmd = "wmctrl -c '{}'"
        if windows:
            if 1 == case:
                window = windows[-1]
                if window.upper() not in self.grep.upper():
                    print(cmd)
                    os.system(cmd.format(window))
                    return self.close_windows(windows[:-1], **kwargs)
            elif 0 == case:
                window = windows[-1]
                os.system(cmd.format(window))
                return self.close_windows(windows[:-1], **kwargs)
            elif 2 == case:
                windows_set = set(windows)
                fil = kwargs.get("filter", [])
                if not fil and set(fil) < windows_set:
                    return self.close_windows(fil[-1], case=0)
        return True

    def get_windows(self, grep="", inherit=True):
        '''
        :param inherit: bool, whether use default grep
        :param grep: str, global research regular expression
        :return: list: list of opened window name which cotains 'vdi'
                such as ['rdp client error',]
        '''
        res = subprocess.getoutput("wmctrl -lx")
        windows = re.findall(r"{} +.*? ([a-z,A-Z ]*)".format(self.vdi), res, re.S)
        windows.extend(re.findall(r"(?i)([%s]{3,8} Client Error)" % self.vdi, res, re.S))
        if grep and inherit:
            windows.extend(re.findall(r"%s" % grep, res, re.S))
        elif grep and not inherit:
            windows = re.findall(r"%s" % grep, res, re.S)
        print(windows)
        return windows

    def exception_trace(self):
        return

    def check_logon(self):
        log.info("checking logon {} desktop".format(self.vdi))
        time.sleep(90)
        res = subprocess.getoutput("wmctrl -lx | grep -i '{}'".format(self.grep))
        windows = self.get_windows()
        if res:
            if windows:
                self.close_windows(windows)
            log.info("logon {} desktop auto success".format(self.vdi))
        else:
            log.error("logon {} desktop auto fail".format(self.vdi))
            self.exception_trace()
        return True

    def logon(self, session):
        VDIConnection.delete_vdi(self.vdi)
        VDIConnection.create_vdi(self.vdi)
        connection_id_list = VDIConnection.vdi_connection_id(self.vdi)
        if len(connection_id_list) == 1:
            print(connection_id_list[0])
            self.set_vdi(connection_id_list[0], self.set_dic)
            self.connect_vdi(connection_id_list[0])
        elif len(connection_id_list) > 1:
            raise DeleteVDIError
        else:
            raise CreateVDIError
        # try:
        self.check_logon()
        # except:
        #     windows = self.get_windows()
        # self.delete_error_windows(windows)
        # traceback.print_exc()
        # return False
        return True

    @staticmethod
    def error_snapshot(pic_name):
        pic = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S') + '_' + pic_name + '.jpg'
        name = os.path.join(os.getcwd(), 'Test_Report', pic)
        pyautogui.screenshot(name)

    def logoff(self):
        ip_list = self.domains_to_ip_list(self.domain_list)
        for ip in ip_list:
            soc = VDIConnection.generate_socket(ip, 9011)
            time.sleep(1)
            res = soc.request("get_user")
            if res and str(res).upper() == self.user.upper():
                time.sleep(1)
                soc.request("logoff")
                break
            else:
                raise GetuserError
        else:
            traceback.print_exc()
            raise Exception
        return True


class CitrixLinux(VDIConnection):
    def __init__(self, user, connection_mode='workspace'):
        super().__init__(user)
        """
        domain='sh', 
        user='autotest1', 
        password='Shanghai2010', 
        url='https://sfnsvr.sh.dto/citrix/newstore/discovery'
        """
        self.domain_list = vdi_config['citrix']['win10']['host_list']
        self.connection_mode = connection_mode
        self.url = vdi_config['citrix']['url']
        self.citrix_server = vdi_config['citrix']['server']

        if self.connection_mode.lower() == 'storefront':
            self.connectionMode = 'store'
        elif self.connection_mode.lower() == 'pnagent':
            self.connectionMode = 'pnagent'
        else:
            self.connectionMode = 'workspace'

    def edit_citrix_connection(self, citrix_id):
        log.info("edit citrix connection, import url, domain, connectionMode, username, password")

        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/address {}".format(citrix_id, self.url))
        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/domain {}".format(citrix_id, self.domain))
        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/connectionMode {}".format(citrix_id, self.connectionMode))
        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/credentialsType 'password'".format(citrix_id))
        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/password {}".format(citrix_id, self.password))
        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/username {}".format(citrix_id, self.user))
        os.system("mclient commit")

    @staticmethod
    def set_citrix_full_screen():
        log.info("set citrix full screen")
        os.system("mclient --quiet set root/ConnectionType/xen/general/TWIMode 'Force Seamless Off'")
        os.system("mclient --quiet set root/ConnectionType/xen/general/windowSize 'Full Screen'")
        os.system("mclient commit")

    def connect_citrix_VDI(self, citrix_id, session):
        log.info("connect citrix VDI desktop")

        time.sleep(1)
        os.popen("connection-mgr start {}".format(citrix_id))
        time.sleep(30)

        citrix_workspace = subprocess.getoutput("wmctrl -lx | grep -i 'citrix workspace'")
        if not citrix_workspace:
            log.error("logon citrix workspace dashboard fail, check use 'wmctrl' script.")
            self.error_snapshot('open citrix workspace error')
            citrix_error = subprocess.getoutput("wmctrl -lx | grep -i 'citrix server error'")
            if citrix_error:
                log.error("logon citrix workspace dashboard error")
                self.error_snapshot('HP - Citrix Server Error')
                os.system("wmctrl -c 'HP - Citrix Server Error'")
            os.system("wmctrl -c 'Citrix Workspace'")
            return False

        log.info("logon citrix workspace dashboard success, check use 'wmctrl' script.")

        time.sleep(2)
        citrix_desktop_1 = subprocess.getoutput("wmctrl -lx | grep -i '{}'".format(session))
        if citrix_desktop_1:
            log.info("logon citrix desktop auto success, check use 'wmctrl' script.")
            pyautogui.click(pyautogui.size()[0] - 3, pyautogui.size()[1] / 2)
            time.sleep(1)
            pyautogui.click(pyautogui.size()[0] - 3, pyautogui.size()[1] - 10)
            return True

        d = subprocess.getoutput(
            "ls /tmp/citrix/{}/dtopfiles/CitrixApps | grep -i '{}'".format(citrix_id, session[:15]))
        desktop_name = d.split('.')[1]                                     # 'Win10 Automatio $A118-17-92F83E3F-0001'
        desktop_id = 'Controller.{}'.format(desktop_name)

        log.info("start logon desktop")
        os.system("/usr/bin/xen-launch '{}' '{}'".format(citrix_id, desktop_id))
        time.sleep(20)
        citrix_desktop_2 = subprocess.getoutput("wmctrl -lx | grep -i '{}'".format(session))
        if citrix_desktop_2:
            log.info("logon citrix desktop success, check use 'wmctrl' script.")
            return True
        else:
            log.error("logon citrix desktop fail, check use 'wmctrl' script.")
            self.error_snapshot('logon citrix desktop fail')
            citrix_error_2 = subprocess.getoutput("wmctrl -lx | grep -i 'citrix server error'")
            if citrix_error_2:
                log.error("logon citrix workspace desktop error")
                self.error_snapshot('HP - Citrix Server Error')
                os.system("wmctrl -c 'HP - Citrix Server Error'")
            os.system("wmctrl -c 'Citrix Workspace'")
            return False

    def logon(self, session='win10'):
        session = vdi_config['citrix'][session.lower()]['name']
        if not self.check_vdi_server_connection(self.citrix_server):
            log.error("the network or citrix server error.")
            return False
        if not self.import_cert():
            log.error("thinpro import rootca Fail")
            return False
        self.delete_vdi('xen')
        self.create_vdi('xen')
        time.sleep(1)
        if len(self.vdi_connection_id('xen')) == 1:
            citrix_id = self.vdi_connection_id('xen')[0]
        else:
            log.error("not found citrix uuid")
            return False
        self.edit_citrix_connection(citrix_id)
        self.set_citrix_full_screen()
        if not self.connect_citrix_VDI(citrix_id, session):
            return False

        time.sleep(30)
        pyautogui.click(pyautogui.size()[0] - 3, pyautogui.size()[1] - 10)
        time.sleep(2)
        pic_path = os.path.join(os.getcwd(), 'Test_Data', 'td_multiple_display', 'citrix_pic')
        pyautogui.screenshot(os.path.join(pic_path, 'test_vdi_logon.png'))
        time.sleep(1)
        if not self.check_vdi_logon_status(os.path.join(pic_path, 'test_vdi_logon.png')):
            self.error_snapshot('citrix remote desktop error')
            os.system("wmctrl -c '{}".format(session))
            time.sleep(2)
            os.system("wmctrl -c 'Citrix Workspace'")
            return False
        else:
            return True

    def logoff(self):
        super().logoff()
        time.sleep(15)
        log.info("sart logoff citrix desktop pool")
        os.system("wmctrl -c 'citrix workspace'")
        time.sleep(5)
        c = subprocess.getstatusoutput("wmctrl -lx | grep -i citrix")
        if not c[1]:
            log.info("logoff citrix success")
            return True
        else:
            log.error("logoff citrix fail")
            return False


class ViewLinux(VDIConnection):
    def __init__(self, user, domain='sh', password="Shanghai2010", **kwargs):
        super().__init__(user, domain, password, **kwargs)
        self.vdi = "view"
        self.set_dic = {
            "credentialsType": "password",
            "domain": domain,
            "desktopSize": "FullScreen",
            "username": user,
            "password": password,
            "viewSecurityLevel": "Allowallconnections",
        }

    def exception_trace(self):
        windows = self.get_windows()
        if windows:
            raise VDILogonError("UnexpectedError occurred!Logon Fail!")

    def logon(self, session):
        view_config = vdi_config.get(self.vdi.lower())
        server = view_config.get("server", "")
        protocol = session.split(" ")[0].upper()
        desktop = view_config.get(session.lower(), {}).get("name")
        self.grep = desktop
        self.set_dic.update({"server": server})
        self.set_dic.update({"preferredProtocol": protocol})
        self.set_dic.update({"desktop": desktop})
        self.domain_list = view_config.get(session.lower(), {}).get("ip_list")
        return super().logon(None)


class RDPLinux(VDIConnection):
    def __init__(self, user, domain='sh', password="Shanghai2010", **kwargs):
        super().__init__(user, domain, password, **kwargs)
        self.vdi = "freerdp"
        self.set_dic = {
            "credentialsType": "password",
            "domain": domain,
            "password": password,
            "username": user,
            "securityLevel": "0",
            "windowType": "full"
        }
        self.grep = "{}: {}".format(self.vdi, self.set_dic.get("address"))
        self.hosts = self.set_dic.get("address")
        self.domain_list.append(self.hosts)

    def exception_trace(self):
        res = self.get_windows()
        if res:
            res = os.popen("ps -aefx |grep  '/tmp/.*-outerr.*.log'").read()
            res = re.findall(r"-f (/tmp/.*?-outerr.*?\.log)", res, re.S)
            if res:
                res = os.popen("cat {}".format(res[0])).read()
                if "Failed to check the initial destination server" in res:
                    raise ServerNotExitError
                elif "Authentication failure, check credentials" in res:
                    raise AuthenticationError
                elif "unable to get local issuer certificate" in res:
                    raise CertificationError
            raise ClientSeverError
        else:
            raise VDILogonError("UnexpectedError occurred!")

    def logon(self, session):
        server_list = vdi_config.get('rdp' if self.vdi.lower() == 'freerdp' else self.vdi).get(session.lower())
        for server in server_list:
            self.set_dic.update({"address": server})
            self.grep = "{}: {}".format(self.vdi, self.set_dic.get("address"))
            self.domain_list = [].append(server)
            if super().logon(None):
                return True
        return False
