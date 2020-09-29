import os
import subprocess
import yaml
import shutil

os.environ['DISPLAY'] = ':0'
import datetime
import re
import traceback
from Common import common_function as cf
from Common.exception import *
from Common.log import Logger
from Common.socket_client import *
import socket
from Common.file_operator import YamlOperator
from Common.file_transfer import FTPUtils
from Common.picture_operator import capture_screen, compare_pic_similarity
from Common.picture_operator import wait_element
import functools
from Test_Data.td_multiple_display.settings import *
import pymouse
import pyautogui

config = os.path.join(cf.get_current_dir(), 'Test_Data', 'td_common', 'vdi_server_config.yml')
with open(config, 'r') as f:
    vdi_config = yaml.safe_load(f)
mouse = pymouse.PyMouse()
log=Logger()


def white_list_filter():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except LogonError:
                traceback.print_exc()
                white_list = None
                cs = ""
                if args:
                    vdi = args[0].__class__.__name__.lower()
                    if "rdp" in vdi:
                        white_list = white_list_rdp
                    elif "view" in vdi:
                        white_list = white_list_view
                    elif "citrix" in vdi:
                        white_list = white_list_citrix
                    except_pic_path = "{}/Test_Report".format(cf.get_current_dir())
                    if not os.path.exists(except_pic_path):
                        os.makedirs(except_pic_path)
                    cs = capture_screen(except_pic_path + "/{}_exception.png".format(vdi))
                flag = False
                if white_list:
                    self = args[0]
                    for k, v in white_list.items():
                        if v and k.lower() == "pic":
                            flag = self.check_picture(v, cs)
                if flag:
                    raise Continue
                else:
                    raise LogonError

        return wrapper

    return decorator


def check_user():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if args:
                self = args[0]
                if self.user and self.domain_list and self.domain_list[0]:
                    print(self.user, self.domain_list)
                    return func(*args, **kwargs)
                else:
                    return "Continue"

        return wrapper

    return decorator


class VDIConnection:
    def __init__(self, user, **kwargs):
        self.domain = vdi_config['domain']
        self.user = user
        self.password = vdi_config['password']
        self.cert = vdi_config['cert']
        self.vdi = None
        self.set_dic = {}
        self.grep = None
        self.parameters = kwargs.get("parameters")
        self.flag = False
        self.domain_list = []
        self.settings = None
        self.set_dic = None
        self.registry_file = os.path.join(cf.get_current_dir(), "Test_Data", "td_common", "thinpro_registry.yml")

    def import_cert(self):
        if cf.import_cert(cert=self.cert):
            return True
        return False

    @staticmethod
    def check_picture(path, cs):
        print(cs)
        file_path = "/".join(os.path.realpath(path).split("\\"))
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_list = os.listdir(file_path)
        for p in file_list:
            if "png" in p or "jpg" in p:
                pic_name = file_path + "/{}".format(p)
                if compare_pic_similarity(pic_name, cs):
                    return True
        return False

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
        """
        :param windows: list from func:get_windows
        :param kwargs:
                case: int,default 1, 0(close all windows);1(close error windows);2(diy close windows)
                filter: list, you should set case=2 and choose window you want to close
        """
        case = kwargs.get("case", 1)
        cmd = "wmctrl -c '{}'"
        if windows and windows[0]:
            if 1 == case:
                window = windows[-1]
                if window.upper() not in self.grep.upper():
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
        """
        :param inherit: bool, whether use default grep
        :param grep: str, global research regular expression
        :return: list: list of opened window name which cotains 'vdi'
                such as ['rdp client error',]
        """
        res = subprocess.getoutput("wmctrl -lx")
        windows = re.findall(r"{} +.*? ([a-z,A-Z\- ]*)".format(self.vdi), res, re.S)
        windows.extend(re.findall(r"(?i)([%s]{3,8} Client Error)" % self.vdi, res, re.S))
        if grep and inherit:
            windows.extend(re.findall(r"%s" % grep, res, re.S))
        elif grep and not inherit:
            windows = re.findall(r"%s" % grep, res, re.S)
        return windows

    def exception_trace(self):
        return

    def check_logon(self):
        log.info("checking logon {} desktop".format(self.vdi))
        time.sleep(100)
        res = subprocess.getoutput("wmctrl -lx | grep -i '{}'".format(self.grep))
        windows = self.get_windows()
        if res:
            if windows:
                self.close_windows(windows)
            log.info("logon {} desktop auto success".format(self.vdi))
            self.flag = True
        else:
            log.debug("&".join(windows))
            log.error("logon {} desktop auto fail {}".format(self.vdi, self.grep))
            self.exception_trace()
            return False
        return True

    def logon(self, session):
        VDIConnection.delete_vdi(self.vdi)
        VDIConnection.create_vdi(self.vdi)
        connection_id_list = VDIConnection.vdi_connection_id(self.vdi)
        if len(connection_id_list) == 1:
            log.info("start launching {}".format(connection_id_list[0]))
            # self.set_vdi(connection_id_list[0], self.set_dic)
            self.set_vdi_from_yml(connection_id_list[0], settings=self.settings, set_dic=self.set_dic)
            self.connect_vdi(connection_id_list[0])
        elif len(connection_id_list) > 1:
            raise DeleteVDIError
        else:
            raise CreateVDIError
        return self.check_logon()

    @staticmethod
    def error_snapshot(pic_name):
        pic = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S') + '_' + pic_name + '.jpg'
        name = os.path.join(cf.get_current_dir(), 'Test_Report', pic)
        capture_screen(name)

    def logoff(self):
        ip_list = self.domains_to_ip_list(self.domain_list)
        log.info("connecting to socket")
        time.sleep(30)
        try:
            for ip in ip_list:
                soc = VDIConnection.generate_socket(ip, 9011)
                time.sleep(1)
                res = soc.request("get_user")
                if res and str(res).upper() == self.user.upper():
                    time.sleep(1)
                    soc.request("logoff")
                    break
            else:
                traceback.print_exc()
                raise ConnectionRefused
            t = 25
            time.sleep(t)
            windows = self.get_windows()
            if windows and self.vdi in ["Selfservice", "view"]:
                log.info("try to close all {} windows".format(self.vdi))
                self.close_windows(windows, case=0)
            elif windows:
                raise LogoffTimeout("Timeout {} seconds".format(t))
        except LogoffError:
            traceback.print_exc()
            windows = self.get_windows()
            log.info("try to close all {} windows".format(self.vdi))
            self.close_windows(windows, case=0)
        return True

    @staticmethod
    def common_pic(pic):
        return os.path.join(cf.get_current_dir(), "Test_Data", "td_vdi", "common", "{}".format(pic))

    def new_vdi_ui(self, vdi, vdi_option_picture):
        log.info("start new {} by right click desktop".format(vdi))
        pyautogui.rightClick(1, 1)
        time.sleep(1)

        create = wait_element(self.common_pic("_create"))
        if not create:
            log.error("not found 'create' option")
            return False
        pyautogui.click(create[0])
        time.sleep(0.5)
        vdi_option = wait_element(vdi_option_picture)
        if vdi_option:
            pyautogui.click(vdi_option[0])
            time.sleep(1)
        else:
            other = wait_element(self.common_pic("_other"))
            if not other:
                log.error("not found 'other' option")
                return False
            pyautogui.click(other[0])
            time.sleep(0.5)
            vdi_option_1 = wait_element(vdi_option_picture)
            if not vdi_option_1:
                log.error("not found {} option".format(vdi))
                return False
            pyautogui.click(vdi_option_1[0])
            time.sleep(1)

        vdi_id = self.vdi_connection_id(vdi)
        if vdi_id:
            log.info("new {} success".format(vdi))
            return True
        else:
            log.error("new {} fail".format(vdi))
            return False

    def open_edit_vdi_window_ui(self, vdi, vdi_picture):
        log.info("start edit {} by right click desktop".format(vdi))
        time.sleep(1)
        telnet_icon = wait_element(vdi_picture)
        if not telnet_icon:
            log.error("not found telnet desktop icon")
            return False
        pyautogui.moveTo(telnet_icon[0])
        pyautogui.rightClick(telnet_icon[0])
        time.sleep(1)
        edit = wait_element(self.common_pic("_edit_option"))
        if not edit:
            log.error("not found 'edit' option")
            return False
        pyautogui.moveTo(edit[0])
        pyautogui.click(edit[0])
        time.sleep(2)
        window = subprocess.getoutput("wmctrl -lx | grep -i '{}'".format(vdi))
        if window:
            log.info("open {} edit window success".format(vdi))
            return True
        else:
            log.error("open {} edit window fail".format(vdi))
            return False

    @staticmethod
    def set_vdi_from_yml(vdi_id, settings, set_dic):
        for key, value in settings.items():
            if "address" in key:
                os.system("mclient --quiet set {} '{}'".format(str(key).format(vdi_id),
                                                               str(value).format(set_dic.get("address"))))
                continue
            if "domain" in key:
                os.system("mclient --quiet set {} '{}'".format(str(key).format(vdi_id),
                                                               str(value).format(set_dic.get("domain"))))
                continue
            if "connectionMode" in key:
                os.system("mclient --quiet set {} '{}'".format(str(key).format(vdi_id),
                                                               str(value).format(set_dic.get("connectionMode"))))
                continue
            if "password" in key:
                os.system("mclient --quiet set {} '{}'".format(str(key).format(vdi_id),
                                                               str(value).format(set_dic.get("password"))))
                continue
            if "username" in key:
                os.system("mclient --quiet set {} '{}'".format(str(key).format(vdi_id),
                                                               str(value).format(set_dic.get("username"))))
                continue
            if "server" in key:
                os.system("mclient --quiet set {} '{}'".format(str(key).format(vdi_id),
                                                               str(value).format(set_dic.get("server"))))
                continue
            if "preferredProtocol" in key:
                os.system("mclient --quiet set {} '{}'".format(str(key).format(vdi_id),
                                                               str(value).format(set_dic.get("preferredProtocol"))))
                continue
            if "desktop" in key:
                os.system("mclient --quiet set {} '{}'".format(str(key).format(vdi_id),
                                                               str(value).format(set_dic.get("desktop"))))
                continue
            if "{}" in key and "{}" not in value:
                os.system("mclient --quiet set {} '{}'".format(str(key).format(vdi_id), value))
                continue
            else:
                os.system("mclient --quiet set {} '{}'".format(key, value))
        os.system("mclient commit")


class CitrixLinux(VDIConnection):
    def __init__(self, user, **kwargs):
        super().__init__(user, **kwargs)
        """
        domain='sh', 
        user='autotest1', 
        password='Shanghai2010', 
        url='https://sfnsvr.sh.dto/citrix/newstore/discovery'
        """
        self.domain_list = vdi_config.get(self.parameters.get('vdi').lower(), {}).get(self.parameters.get(
            'session').lower(), {}).get("ip_list")
        # self.domain_list = ['Autotest-C01.sh.dto']
        self.connection_mode = kwargs.get("connection_mode", "workspace")
        self.url = vdi_config['citrix']['url']
        self.citrix_server = vdi_config['citrix']['server']
        self.vdi = "Selfservice"
        self.grep = "Citrix Workspace"
        self.settings = kwargs.get("setting",
                                   YamlOperator(self.registry_file).read()["set"]["citrix"]["multiple_display"])
        self.set_dic = {"address": self.url,
                        "domain": self.domain,
                        "connectionMode": self.connection_mode,
                        "password": self.password,
                        "username": self.user
                        }

    def set_citrix_connection_from_yml(self, citrix_id):

        # self.set_vdi_from_yml(citrix_id, settings=self.settings, url=self.url, domain=self.domain,
        #                       connectionMode=self.connection_mode, password=self.password, user=self.user)
        self.set_vdi_from_yml(citrix_id, settings=self.settings, set_dic=self.set_dic)

    def edit_citrix_connection(self, citrix_id):
        log.info("edit citrix connection, import url, domain, connectionMode, username, password")
        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/address {}".format(citrix_id, self.url))
        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/domain {}".format(citrix_id, self.domain))
        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/connectionMode {}".format(citrix_id,
                                                                                                        self.connectionMode))
        os.system(
            "mclient --quiet set root/ConnectionType/xen/connections/{}/credentialsType 'password'".format(citrix_id))
        os.system(
            "mclient --quiet set root/ConnectionType/xen/connections/{}/password {}".format(citrix_id, self.password))
        os.system("mclient --quiet set root/ConnectionType/xen/connections/{}/username {}".format(citrix_id, self.user))
        os.system("mclient --quiet set root/ConnectionType/xen/general/TWIMode 'Force Seamless Off'")
        os.system("mclient --quiet set root/ConnectionType/xen/general/windowSize 'Full Screen'")
        os.system("mclient commit")

    def connect_citrix_VDI(self, citrix_id, session):
        white_list_path = os.path.join(cf.get_current_dir(), "Test_Data", "td_multiple_display", "white_list",
                                       "_citrix")
        log.info("connect citrix VDI desktop")
        time.sleep(1)
        os.popen("connection-mgr start {}".format(citrix_id))
        time.sleep(30)

        citrix_error_1 = subprocess.getoutput("wmctrl -lx | grep -i 'citrix error'")
        if citrix_error_1:
            self.error_snapshot('Citrix Error')
            log.warning("found citrix error")
            pyautogui.press("enter")
            time.sleep(10)

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
        if citrix_workspace and 'selfservice.Selfservice' not in citrix_workspace:
            log.error("logon citrix workspace dashboard fail")
            self.error_snapshot('open citrix workspace error')
            os.system("wmctrl -c 'Citrix Workspace'")
            time.sleep(0.2)
            os.system("wmctrl -c 'Citrix Workspace'")
            return False
        log.info("logon citrix workspace dashboard success, check use 'wmctrl' script.")

        time.sleep(2)
        citrix_desktop_1 = subprocess.getoutput("wmctrl -lx | grep -i '{}'".format(session))
        if citrix_desktop_1:
            log.info("logon citrix desktop auto success, check use 'wmctrl' script.")
            time.sleep(3)
            mouse.click(1, 1)  # click on the top right corner of the screen
            return True

        d = subprocess.getoutput(
            "ls /tmp/citrix/{}/dtopfiles/CitrixApps | grep -i '{}'".format(citrix_id, session[:15]))
        desktop_name = d.split('.')[1]  # 'Win10 Automatio $A118-17-92F83E3F-0001'
        desktop_id = 'Controller.{}'.format(desktop_name)

        log.info("start logon desktop")
        os.system("/usr/bin/xen-launch '{}' '{}' &".format(citrix_id, desktop_id))
        log.info("run command to launch vdi connection")

        time.sleep(10)
        if wait_element(white_list_path, rate=0.98):
            log.info("found log on error")
            pyautogui.press("enter")
            time.sleep(1)
            # os.system("wmctrl -c 'Citrix Workspace'")
            os.system("wmctrl -c 'Citrix Workspace'")
            return "Continue"
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
            time.sleep(0.2)
            os.system("wmctrl -c 'Citrix Workspace'")
            return False

    @check_user()
    def logon(self, session='win10'):
        session = vdi_config['citrix'][session.lower()]['name']
        # if not self.check_vdi_server_connection(self.citrix_server):
        #     log.error("the network or citrix server error.")
        #     return "Continue"
        if not self.import_cert():
            log.error("thinpro import rootca Fail")
            return "Continue"
        self.delete_vdi('xen')
        self.create_vdi('xen')
        time.sleep(1)
        if len(self.vdi_connection_id('xen')) == 1:
            citrix_id = self.vdi_connection_id('xen')[0]
        else:
            log.error("not found citrix uuid")
            return "Continue"
        self.set_citrix_connection_from_yml(citrix_id)
        connect = self.connect_citrix_VDI(citrix_id, session)
        if connect is False:
            return False
        elif connect is "Continue":
            return "Continue"
        # if not self.connect_citrix_VDI(citrix_id, session):
        #     return "Continue"
        else:
            time.sleep(60)
            return True

    def logoff(self):
        super().logoff()
        time.sleep(2)
        desktop = subprocess.getoutput("wmctrl -lx | grep -i Autotest")
        if desktop:
            os.system("wmctrl -c 'Autotest Win10'")
            os.system("wmctrl -c 'Autotest W2016'")
            time.sleep(2)
            pyautogui.press("tab", presses=2, interval=0.3)
            pyautogui.press("enter")
        os.system("wmctrl -c 'citrix workspace'")
        time.sleep(1)
        c = subprocess.getstatusoutput("wmctrl -lx | grep -i citrix")
        if not c[1]:
            log.info("logoff citrix success")
            return True
        else:
            log.error("logoff citrix fail")
            return False


class ViewLinux(VDIConnection):
    def __init__(self, user, **kwargs):
        super().__init__(user, **kwargs)
        self.vdi = "view"
        self.set_dic = {
            "credentialsType": "password",
            "domain": self.domain,
            "desktopSize": '"All Monitors"',
            "username": user,
            "password": self.password,
            "viewSecurityLevel": '"Allow all connections"',
        }
        self.domain_list = vdi_config.get(self.parameters.get('vdi').lower(), {}).get(self.parameters.get(
            'session').lower(), {}).get("ip_list")
        self.settings = kwargs.get("setting",
                                   YamlOperator(self.registry_file).read()["set"]["view"]["multiple_display"])

    @white_list_filter()
    def exception_trace(self):
        windows = self.get_windows()
        if windows:
            raise VDILogonError("UnexpectedError occurred!Logon Fail!")

    @check_user()
    def logon(self, session):
        view_config = vdi_config.get(self.vdi.lower())
        server = view_config.get("server", "")
        protocol = session.split(" ")[0].upper()
        desktop = view_config.get(session.lower(), {}).get("name")
        self.grep = desktop
        self.set_dic.update({"server": server})
        self.set_dic.update({"preferredProtocol": protocol})
        self.set_dic.update({"desktop": desktop})
        try:
            return super().logon(None)
        except DeleteVDIError:
            return "Continue"
        except CreateVDIError:
            return "Continue"
        except Continue:
            return "Continue"
        except LogonError:
            return False
        finally:
            if not self.flag:
                windows = self.get_windows()
                self.close_windows(windows)

    def logoff(self):
        super().logoff()
        result = os.popen("ps -aux |grep '/usr/lib/vmware/view/bin/vmware-view'").read()
        res = re.findall(r"root *?([0-9]{3,6}) .*? /usr/lib/vmware/view/bin/vmware-view", result, re.S)
        res.extend(re.findall(r"user *?([0-9]{3,6}) .*? /usr/lib/vmware/view/bin/vmware-view", result, re.S))
        if res:
            for i in res:
                os.popen("kill -s 9 '{}'".format(i))
        return True


class RDPLinux(VDIConnection):
    def __init__(self, user, **kwargs):
        super().__init__(user, **kwargs)
        self.vdi = "freerdp"
        self.domain = kwargs.get("domain", self.domain)
        self.set_dic = {
            "credentialsType": "password",
            "domain": self.domain,
            "password": self.password,
            "username": user,
            "securityLevel": "0",
            "windowType": "full",
        }
        self.server = kwargs.get("rdp_server", "")
        self.domain_list = [self.server]
        self.settings = kwargs.get("setting", YamlOperator(self.registry_file).read()["set"]["RDP"]["multiple_display"])

    @white_list_filter()
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

    @check_user()
    def logon(self, session):
        if self.server:
            self.set_dic.update({"address": self.server})
            self.grep = "{}: {}".format(self.vdi, self.set_dic.get("address"))
        try:
            return super().logon(None)
        except DeleteVDIError:
            return "Continue"
        except CreateVDIError:
            return "Continue"
        except Continue:
            return "Continue"
        except LogonError:
            return False
        finally:
            if not self.flag:
                windows = self.get_windows()
                self.close_windows(windows)


class MultiUserManger:
    def __init__(self):
        self.download_base_file = 'download_temp.txt'
        self.file_path = get_current_dir("Test_Data/common/{}".format(self.download_base_file))
        self.config_base_file = get_current_dir('Test_Data/common/multi_user.yml')

    @property
    def config_args(self):
        yaml_obj = YamlOperator(self.config_base_file)
        content = yaml_obj.read()
        return content

    @property
    def remote_base_file(self):
        path = self.config_args['path']
        tree = path.split('/')
        remote_file = '/'.join(tree[4:])
        return remote_file

    @property
    def ftp(self):
        ip = self.config_args['ip']
        user = self.config_args['user']
        pwd = self.config_args['pwd']
        ftp_obj = FTPUtils(ip, user, pwd)
        return ftp_obj

    def get_a_available_key(self, key="user"):
        self.ftp.download_file(self.remote_base_file, self.file_path)
        time.sleep(2)
        yaml_obj = YamlOperator(self.file_path)
        total_users = yaml_obj.read().get(key, {})
        for k, v in total_users.items():
            if v in 'available':
                dic_key = k
                break
        else:
            dic_key = ''
        if dic_key:
            self.lock_key(dic_key, key)
        else:
            print('no available user could be assigned')
        return dic_key

    def change_key_state(self, user_name, state, key="user"):
        self.ftp.download_file(self.remote_base_file, self.file_path)
        time.sleep(2)
        yaml_obj = YamlOperator(self.file_path)
        total_users = yaml_obj.read()
        value = total_users.get(key).get(user_name)
        if value:
            total_users[key][user_name] = state
            yaml_obj.write(total_users)
            self.ftp.upload_file(self.file_path, self.remote_base_file)
        else:
            print('invalid user')

    def reset_key(self, user_name, key="user"):
        self.change_key_state(user_name, 'available', key)

    def lock_key(self, user_name, key="user"):
        self.change_key_state(user_name, 'busy', key)


class TelnetLinux(VDIConnection):

    def __init__(self, user=vdi_config["user"][8], **kwargs):
        super().__init__(user, **kwargs)
        self.password = vdi_config["password"]

    def logon(self, session="address"):
        address = vdi_config["telnet"][session]
        self.delete_vdi("telnet")
        self.create_vdi("telnet")
        telnet_id = self.vdi_connection_id("telnet")[0]
        os.system(
            "mclient --quiet set root/ConnectionType/telnet/connections/{}/address {}".format(telnet_id, address))
        os.system("mclient commit")
        time.sleep(1)
        log.info("start connect telnet")
        os.system("connection-mgr start {} &".format(telnet_id))
        time.sleep(15)

        connection_manager = subprocess.getoutput("wmctrl -lx | grep -i 'connection manager'")
        if connection_manager:
            log.error("found the error 'connection could not be started'")
            subprocess.call("wmctrl -c 'Connection Manager'", shell=True)
            return False
        pyautogui.typewrite(self.user, interval=0.1)
        pyautogui.press("enter")
        time.sleep(2)
        pyautogui.typewrite(self.password)
        pyautogui.press("enter")

        time.sleep(3)
        win_title = subprocess.getoutput("wmctrl -lx | grep '{}@localhost'".format(self.user))
        if win_title:
            log.info("logon telnet connection success")
            return True
        else:
            log.error("logon telnet connection fail")
            os.system("wmctrl -c 'Telnet'")
            time.sleep(1)
            self.delete_vdi('telnet')
            return False

    def logoff(self):
        log.info("start logoff telnet connection")
        time.sleep(1)
        pyautogui.typewrite("exit", interval=0.1)
        pyautogui.press("enter")
        time.sleep(2)
        win_title = subprocess.getoutput("wmctrl -lx | grep '{}@localhost'".format(self.user))
        if win_title:
            log.error("logoff telnet connection fail")
            time.sleep(1)
            self.delete_vdi("telnet")
            return False
        else:
            log.info("logoff telnet connection success")
            time.sleep(1)
            self.delete_vdi("telnet")
            return True

    @staticmethod
    def pic(picture):
        return os.path.join(cf.get_current_dir(), "Test_Data", "td_vdi", "telnet", "{}".format(picture))

    def new_telnet_ui(self):
        if self.new_vdi_ui(vdi="telnet", vdi_option_picture=self.pic("_telnet_option")):
            return True
        else:
            return False

    def edit_telnet_ui(self, address):
        if not self.open_edit_vdi_window_ui(vdi="telnet", vdi_picture=self.pic("_telnet_desktop_icon")):
            return False
        addr = wait_element(self.pic("_address"))
        if not addr:
            log.error("not found 'address'")
            os.system("wmctrl -c 'Telnet Connection Manager'")
            return False
        pyautogui.click(addr[0][0] + 60, addr[0][1])
        pyautogui.typewrite(address, interval=0.1)
        ok_button = wait_element(self.common_pic("_ok"))
        if not ok_button:
            log.error("not found 'ok' button")
            os.system("wmctrl -c 'Telnet Connection Manager'")
            return False
        pyautogui.click(ok_button[0])
        telnet_title = subprocess.getoutput("wmctrl -lx | grep -i 'telnet'")
        if not telnet_title:
            log.info("close telnet connection manager window success")
            return True
        else:
            log.error("close telnet connection manager window fail")
            os.system("wmctrl -c 'Telnet Connection Manager'")
            return False

    def logon_ui(self, session="address"):
        address = vdi_config["telnet"][session]
        self.delete_vdi("telnet")
        if not self.new_telnet_ui():
            return False
        if not self.edit_telnet_ui(address):
            return False

        telnet = wait_element(self.pic("_telnet_desktop_icon"), offset=[20, 20])
        if not telnet:
            log.error("not found telnet icon on desktop")
            return False
        pyautogui.click(telnet[0])
        time.sleep(0.1)
        pyautogui.doubleClick(telnet[0])
        time.sleep(5)

        connection_manager = subprocess.getoutput("wmctrl -lx | grep -i 'connection manager'")
        if connection_manager:
            log.error("found the error 'connection could not be started'")
            subprocess.call("wmctrl -c 'Connection Manager'", shell=True)
            return False

        telnet_title = subprocess.getoutput("wmctrl -lx | grep -i 'telnet'")
        if not telnet_title:
            log.error("open telnet fail")
            return False
        log.info("open telnet success")
        time.sleep(15)
        pyautogui.typewrite(self.user, interval=0.1)
        pyautogui.press("enter")
        time.sleep(2)
        pyautogui.typewrite(self.password)
        pyautogui.press("enter")
        time.sleep(5)
        win_title = subprocess.getoutput("wmctrl -lx | grep '{}@localhost'".format(self.user))
        if win_title:
            log.info("logon telnet connection success")
            return True
        else:
            log.error("logon telnet connection fail")
            os.system("wmctrl -c 'Telnet'")
            time.sleep(1)
            self.delete_vdi('telnet')
            return False

    def logoff_ui(self):
        self.logoff()
