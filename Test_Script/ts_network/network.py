import shutil

from Common.common_function import Run_App, get_current_dir
from Common.log import log
import subprocess
import time
import re
from Test_Script.ts_common.common import PicObjectModel, Window, check_window, run_command
from Test_Script.ts_network.network_pic_settings import NETWORK_SETTINGS, USB_SETTINGS, RDP_SETTINGS,\
    WIRELESS_STATISTICS_SETTINGS, CERTIFICATE_WINDOW_SETTINGS, SSIDPANEL_SETTINGS
from Common.exception import PicNotFoundError, NoAvailableStaticIP, TimeOutError, CaseRunningError
import pyautogui
from Common.file_operator import YamlOperator
import os


def disable_lan_filber(device_name):
    try:
        subprocess.run("/usr/lib/hptc-network-mgr/common/netmgr_wired --down {}".format(device_name),shell=True)
        log.info("disable {}".format(device_name))
    except Exception as e:
        log.error(e)
        # pass


def enable_lan_filber(device_name):
    try:
        subprocess.Popen("/usr/lib/hptc-network-mgr/common/netmgr_wired --up {}".format(device_name),shell=True)
        log.info("enable {}".format(device_name))
    except Exception as e:
        log.error(e)


def disable_wlan(device_name):
    try:
        subprocess.run("/usr/lib/hptc-network-mgr/wireless/hptc-wireless-manager --down {}".format(device_name),shell=True)
        log.info("disable {}".format(device_name))
    except Exception as e:
        log.error(e)


def enable_wlan(device_name):
    try:
        subprocess.run("/usr/lib/hptc-network-mgr/wireless/hptc-wireless-manager --up {}".format(device_name),shell=True)
        log.info("enable {}".format(device_name))
    except Exception as e:
        log.error(e)


# ping server to verify the wireless
def ping_server(ip="15.83.240.98"):
    log.info("start ping " + ip)
    s = subprocess.Popen("ping {} -c 50 | grep -i received".format(ip), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = s.communicate(timeout=60)
    out = out.decode()
    out_list = out.split(',')
    try:
        s.kill()
        res = re.search(r"(\d+)", out_list[2])
        result = res.group(1)
        if int(result) <= 25:
            log.info("ping " + ip + " success")
            return True
        # if out_list[2] == ' 0% packet loss':
        #     log.info("ping " + ip + " success")
        #     return True
        else:
            log.error("ping " + ip + " fail")
            log.error(f'ping {ip} result: {out}')
            return False
    except Exception as e:
        log.error(e)
        log.error("ping " + ip + " fail")
        return False


class NetWorkDisableEnable():
    def __init__(self):
        self.fiber_lan = []
        self.wlan = []

    def linux_cmd_data_format(self,raw_data):
        data_list=[]
        for i in raw_data.split('\n'):
            temp=i.strip()
            if temp:
                data_list.append(temp)
        return data_list

    def get_nics(self):
        app=Run_App('ifconfig')
        app.start()
        r=app.get_stdout().decode()
        r_list=self.linux_cmd_data_format(r)
        nics=[]
        for i in r_list:
            if 'hwaddr' in i.lower():
                single_nic=[]
                single_nic_pure=[]
                single_nic.extend(i.split('  '))
                single_nic.extend(r_list[r_list.index(i)+1].split('  '))
                for j in single_nic:
                    if j:
                        single_nic_pure.append(j)
                nics.append(single_nic_pure)
        return nics

    def update_nic_status(self):
        nics = self.get_nics()
        for nic in nics:
            if nic[0].startswith('eth'):
                self.fiber_lan.append(nic)
            elif nic[0].startswith('wlan'):
                self.wlan.append(nic)

    def get_lan(self):
        if len(self.fiber_lan):
            return self.fiber_lan[0]

    def disable_lan(self):
        lan=self.get_lan()
        if lan:
            disable_lan_filber(lan[0])
        else:
            log.info("Not found lan")

    def enable_lan(self):
        lan = self.get_lan()
        if lan:
            enable_lan_filber(lan[0])
        else:
            log.info("Not found lan")

    def get_wlan(self):
        if self.wlan:
            return self.wlan[0]

    def disable_wlan(self):
        wlan=self.get_wlan()
        if wlan:
            disable_wlan(wlan[0])
        log.info("Not found wlan")

    def enable_wlan(self):
        wlan = self.get_wlan()
        if wlan:
            enable_wlan(wlan[0])
        else:
            log.info("Not found wlan")

    def get_fiber(self):
        if len(self.fiber_lan)>1:
            return self.fiber_lan[1]

    def disable_fiber(self):
        fiber=self.get_fiber()
        if fiber:
            disable_lan_filber(fiber[0])
        else:
            log.info("Not found fiber")

    def enable_fiber(self):
        fiber = self.get_fiber()
        if fiber:
            enable_lan_filber(fiber[0])
        else:
            log.info("Not found fiber")


class Network(PicObjectModel, Window):
    pic_settings = NETWORK_SETTINGS
    open_window_name = 'Network'
    close_windows_name = 'HP Wireless', 'Control Panel',

    def check_window_has_opened(self):
        if self.close_windows_name and isinstance(self.close_windows_name, tuple):
            window = self.close_windows_name[-1]
            result = check_window(window)
            if not result:
                log.warning("Start WorkAround Using Pic instead of 'CTRL+ALT+S'")
                menu = self.menu
                menu.click()
                time.sleep(6)
                pyautogui.typewrite(self.name.replace("_", " "))
                time.sleep(2)
                pyautogui.press('enter')
                time.sleep(3)
                log.info("end")
            else:
                log.info(f"Check Window: {window} Exist")
        else:
            log.warning("No window name")

    def wait_until_network_connected(self, time_out=55, interval=5):
        time.sleep(interval)
        while True:
            try:
                if self.wired_connected:
                    time.sleep(interval)
                    return True
            except PicNotFoundError as e:
                time_out -= interval
                if not time_out:
                    raise TimeOutError(f"Time out for waiting Network Connected! {str(e)}")
                log.info("Waiting Util Network connected")
                time.sleep(interval)

    def wait_until_network_disconnected(self, time_out=55, interval=5):
        time.sleep(interval)
        while True:
            try:
                if self.wired_disconnected:
                    time.sleep(interval)
                    return True
            except PicNotFoundError as e:
                time_out -= interval
                if not time_out:
                    raise TimeOutError(f"Time out for waiting Network Disconnected! {str(e)}")
                log.info("Waiting Util Network Disconnected")
                time.sleep(interval)

    def wait_until_wireless_connected(self, time_out=60, interval=5):
        while time_out:
            try:
                connected = self.wireless_connected
                return
            except PicNotFoundError:
                time_out -= interval
                log.info("Waiting Wireless Connect")
                time.sleep(interval)
        raise CaseRunningError(f"Wireless Connect Fail")

    @staticmethod
    def enable_wired():
        run_command("sudo /usr/lib/hptc-network-mgr/common/netmgr_wired --up eth0 && ifconfig eth0 up")

    @staticmethod
    def disabled_wired():
        run_command("sudo /usr/lib/hptc-network-mgr/common/netmgr_wired --down eth0 && ifconfig eth0 down")

    @staticmethod
    def wired_wireless_switch_on():
        run_command("mclient set root/Network/WiredWirelessSwitch 1 && mclient commit")

    @staticmethod
    def wired_wireless_switch_off():
        run_command("mclient set root/Network/WiredWirelessSwitch 0 && mclient commit")

    @staticmethod
    def set_connection_mode_automatic_with_command():
        run_command("mclient --quiet set root/Network/Wired/Method 'Automatic' &&"
                    "mclient --quiet set root/Network/Wired/IPAddress '' &&"
                    "mclient --quiet set root/Network/Wired/DefaultGateway '' &&"
                    "mclient --quiet set root/Network/Wired/SubnetMask '' &&"
                    "mclient commit")

    @staticmethod
    def check_frequency(freq=2.4):
        response = run_command("sudo iwlist wlan0 channel")
        result = re.search(r"(?i)Current Frequency.*?([\d\.]+).*?GHZ.*?", response)
        if result:
            frequency = float(result.group(1))
            if abs(frequency-freq) < 1:
                return
            raise CaseRunningError(f"Check Frequency Fail! Current: {frequency} Expect: {freq}")
        raise CaseRunningError("Wireless Connect Fail")


class WirelessStatistics(PicObjectModel, Window):
    open_window_name = "Wireless Statistics"
    pic_settings = WIRELESS_STATISTICS_SETTINGS
    close_windows_name = "Wireless Statistics",


class Usb(PicObjectModel, Window):
    pic_settings = USB_SETTINGS
    open_window_name = 'hptc-usb-update'
    close_windows_name = 'Restore Configuration', 'hptc-usb-update', 'USB Update',

    def open(self):
        log.info(f'open window {self.open_window_name}')
        subprocess.Popen(f'{self.open_window_name}', shell=True)
        time.sleep(4)

    def usb_is_ready(self, time_out=4, interval=2):
        while time_out:
            try:
                if self.usb_ready:
                    return True
            except PicNotFoundError:
                time_out -= interval
                log.info("Waiting USB Ready")
                time.sleep(interval)
        return False

    def install(self, file_name: str) -> bool:
        self.close()
        self.open()
        usb_update = self.usb_update
        usb_update.click()
        if not self.usb_is_ready():
            return False
        search = usb_update.search
        search.send_keys(f"{file_name}")
        usb_update.select_box.click()
        usb_update.install_button.click()
        time.sleep(3)
        return True


def ping(ip, count=10):
    result = run_command(f"ping {ip} -c {count}", timeout=30)
    fail_rate = re.search(r",.*?(\d+)% packet loss", result)
    if fail_rate and int(fail_rate.group(1)) < 99:
        return True
    return False


class NetWorkUtils:
    temp_net_info_file = get_current_dir("Test_Report/network_info.yaml")
    network_information = {}

    @classmethod
    def get_network_info(cls) -> dict:
        net_info = subprocess.getoutput("ifconfig | grep eth0 -A 2")
        g_ip = re.search(r"(?i)(?:inet|inet addr)[: ]([\\.\d]+)", net_info)
        g_mac = re.search(r"(?i)(?:ether|hwaddr)[: ]([:\w]+)", net_info)
        g_mask = re.search(r"(?i)(?:netmask|mask)[: ]([\\.\d]+)", net_info)
        g_broadcast = re.search(r"(?i)(?:broadcast|bcast)[: ]([\\.\d]+)", net_info)
        assert g_ip, 'Get IP Fail'
        assert g_mac, 'Get mac Fail'
        assert g_mask, 'Get mask Fail'
        assert g_broadcast, 'Get broadcast Fail'
        ip, mac, mask, broadcast = g_ip.group(1), g_mac.group(1), g_mask.group(1), g_broadcast.group(1)

        def calculate_gateway() -> str:
            l_ip = int(ip.split(".")[-1])
            l_mask = int(mask.split(".")[-1])
            l_gateway = (l_ip & l_mask) + 1
            g_way = f'{".".join(ip.split(".")[:-1])}.{l_gateway}'
            return g_way
        gateway = calculate_gateway()
        cls.__save(ip=ip,
                   mac=mac,
                   mask=mask,
                   broadcast=broadcast,
                   gateway=gateway)
        return cls.network_information

    @classmethod
    def __save(cls, **data):
        cls.network_information = data

    @classmethod
    def save_info_to_yaml(cls) -> dict:
        if not cls.network_information:
            cls.get_network_info()
        log.info(f"StaticIpUtils Save: {cls.network_information}")
        file_oper = YamlOperator(cls.temp_net_info_file)
        file_oper.write(cls.network_information)
        return cls.network_information

    @classmethod
    def read_info_from_yaml(cls, *wants) -> dict:
        if not os.path.exists(cls.temp_net_info_file):
            network_information = cls.save_info_to_yaml()
        else:
            network_information = YamlOperator(cls.temp_net_info_file).read()
        if not wants:
            return network_information
        return dict(([(key, network_information.get(key, "")) for key in wants]))


class StaticIpUtils:
    temp_static_info_file = get_current_dir("Test_Report/static_info.yaml")

    @classmethod
    def get_available_static_info(cls) -> tuple:
        """
        :return tuple, (available_ip, mask, gateway)
        """
        info_dict = NetWorkUtils.read_info_from_yaml("broadcast", "mask", "gateway", )
        broadcast, mask, gateway = info_dict.values()
        ip_1_3 = '.'.join(broadcast.split(".")[:-1])
        broadcast_4 = int(broadcast.split(".")[-1])
        for ip_4 in range(broadcast_4-3, broadcast_4)[::-1]:
            available_ip = f"{ip_1_3}.{ip_4}"
            ping_result = ping(available_ip, count=15)
            if not ping_result:
                return available_ip, mask, gateway
        raise NoAvailableStaticIP(f"IP from {ip_1_3}.{broadcast_4-3}-{ip_1_3}.{broadcast_4-1} is Not Available")

    @classmethod
    def __save(cls, **data) -> dict:
        log.info(f"StaticIpUtils Save: {data}")
        file_oper = YamlOperator(cls.temp_static_info_file)
        file_oper.write(data)
        return data

    @classmethod
    def get_and_save_info_to_yaml(cls) -> dict:
        ip, mask, gateway = cls.get_available_static_info()
        return cls.__save(ip=ip,
                          mask=mask,
                          gateway=gateway)

    @classmethod
    def read_info_from_yaml(cls) -> dict:
        """
        :return {ip:'ip',
                 mask:'mask',
                 gateway:'gateway'
                }
        """
        if not os.path.exists(cls.temp_static_info_file):
            return cls.get_and_save_info_to_yaml()
        return YamlOperator(cls.temp_static_info_file).read()


class EasyRDP(PicObjectModel, Window):
    vdi = "freerdp"
    pic_settings = RDP_SETTINGS
    close_windows_name = 'RDP Client Error', 'FreeRDP'

    def __init__(self, loc, name, pic_path):
        super().__init__(loc, name, pic_path)
        self.vdi_id = ""
        self.settings = {}

    def add_settings(self, settings: dict):
        self.settings = settings

    def __set_vdi(self):
        front_command = "mclient --quiet set root/ConnectionType/"
        command = ""
        if not self.vdi_id:
            raise CaseRunningError("No VDI Select")
        if self.settings:
            for key, values in self.settings.items():
                joined_command = front_command + "{}/connections/{}/{} '{}' && ".format(self.vdi, self.vdi_id, key, values)
                command += joined_command
        command += "mclient commit"
        run_command(commands=command, timeout=30)

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

    @classmethod
    def delete_vdi(cls, vdi):
        log.info("start delete {} uuid".format(vdi))
        citrix_id = cls.vdi_connection_id(vdi)
        if len(citrix_id) > 0:
            for c_id in citrix_id:
                run_command("mclient --quiet delete root/ConnectionType/{}/connections/{} && "
                            "mclient commit".format(vdi, c_id))
                time.sleep(0.2)
            if len(cls.vdi_connection_id('vdi')) == 0:
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

    def logon(self):
        EasyRDP.delete_vdi(self.vdi)
        EasyRDP.create_vdi(self.vdi)
        connection_id_list = EasyRDP.vdi_connection_id(self.vdi)
        if len(connection_id_list) == 1:
            self.vdi_id = connection_id_list[0]
            log.info(f"start launching {self.vdi_id}")
            self.__set_vdi()
            self.open()
            time.sleep(10)
            if not self.is_active():
                self.open()
        elif len(connection_id_list) > 1:
            raise CaseRunningError("Delete RDP Fail")
        else:
            raise CaseRunningError("Create RDP Fail")

    def open(self):
        self.rdp_icon.double_click()

    def is_active(self):
        command_list_active = f'connection-mgr listActive'
        response = run_command(command_list_active)
        if self.vdi_id not in response:
           return False
        return True

    def logoff(self):
        command = f'sudo connection-mgr stop {self.vdi_id}'
        run_command(command)
        time.sleep(5)
        if self.is_active():
            self.force_logoff()

    def force_logoff(self):
        command = f'sudo connection-mgr kill {self.vdi_id}'
        run_command(command)


class CertificateUtil(PicObjectModel, Window):
    pic_settings = CERTIFICATE_WINDOW_SETTINGS
    close_windows_name = 'Input password', 'hptc-cert-mgr'
    _cert_password = 'Shanghai2010'
    _certs = []

    def import_cert(self, file_path):
        dst = f"/etc/ThinProCertificates/{os.path.basename(file_path)}"
        shutil.copy(file_path, dst)
        file_name = os.path.basename(file_path).replace(".cer", ".pem")
        source = f"/etc/ssl/certs/{file_name}"
        dist = f"/etc/ThinProCertificates/{file_name}"
        if file_path in self._certs:
            log.warning(f'Cert: {file_path} has imported !')
            return
        log.info(f"Start Import Cert {file_path}")
        CertificateUtil._certs.append(file_path)
        pipe = os.popen(f'hptc-cert-mgr --non-interactive -i {file_path}')
        if '802' not in file_path:
            pipe.read()
            shutil.copy(source, dist)
            return
        try:
            time.sleep(3)
            input_window = self.cert_password
            input_window.cert_blank.send_keys(self._cert_password)
            self.cert_ok.click()
            time.sleep(10)
            log.info(f"Import Cert {file_path} Success!")
        except PicNotFoundError as e:
            raise CaseRunningError(f"Import Cert Fail! {str(e)}")
        finally:
            self.close()


class SSIDPanel(PicObjectModel, Window):
    close_windows_name = 'SSID',
    pic_settings = SSIDPANEL_SETTINGS


if __name__ == '__main__':
    print(StaticIpUtils.read_info_from_yaml())