import subprocess
import pyautogui
import traceback
import re
from Common import tool
from Common import common_function as cf
from Common.file_operator import YamlOperator
from Common.picture_operator import wait_element
from Common.log import *


class NetworkCommon:

    @staticmethod
    def common_pic(picture):
        return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "common", picture)

    @staticmethod
    def network_profile():
        return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "network_profile_info.yml")

    @staticmethod
    def gateway():
        try:
            gateway_ip = subprocess.getoutput("ip route | grep -i 'default'").split()[2]
            return gateway_ip
        except:
            log.error(traceback.format_exc())
            return None

    def apply(self):
        pyautogui.click(wait_element(self.common_pic("_apply"), offset=(20, 10))[0], interval=0.5)

    @staticmethod
    def get_mask(p):
        try:
            # mask = subprocess.getoutput("ifconfig {} | grep -i mask".format(p)).strip().split(":")[-1]
            res = subprocess.getoutput("ifconfig | grep {} -A 1 | grep -i 'inet'".format(p))
            result = re.search(r"(?i)(?:mask)[: ]([\\.\d]+)", res)
            assert result, "Get Mask Fail"
            return result.group(1)
        except:
            return "255.255.255.192"

    @staticmethod
    def open_network():
        cf.open_window("network")

    def close_control_panel(self, option='discard'):
        os.system("wmctrl -c 'Control Panel'")
        time.sleep(1)
        dialog = wait_element(self.common_pic("_network_dialog"))
        if dialog:
            log.info("found network dialog")
            if option.lower() == "apply":
                pyautogui.click(dialog[0][0]+277, dialog[0][1]+125)
            elif option.lower() == "discard":
                pyautogui.click(dialog[0][0]+120, dialog[0][1]+125)
        w = subprocess.getoutput("wmctrl -lx | grep -i 'control panel'")
        if not w:
            log.info("close control success")
            return True
        else:
            log.error("close control fail")
            return False

    @staticmethod
    def set_wired_and_wireless_simultaneously(status="0"):
        """
        set wired network and wireless network can work simultaneously
        :return:
        """
        log.info("set wired network and wireless network can work simultaneously")
        os.system("mclient --quiet set root/Network/WiredWirelessSwitch {}".format(status))
        os.system("mclient commit")

    @staticmethod
    def set_wired_connection_priority():
        """
        set wired will take priority of wireless network, if wired network can not get connected then wireless
         network will be used if configured.
        :return:
        """
        log.info("set wired take priority of wireless network")
        os.system("mclient --quiet set root/Network/WiredWirelessSwitch 1")
        os.system("mclient commit")


class Wired(NetworkCommon):
    """
    thinpro control panel -> network -> wired
    """
    def __init__(self):
        self.log = log
        self.path = cf.get_current_dir()
        self.report_path = self.path + '/Test_Report'
        self.img_path = self.report_path + '/img/'
        try:
            if not os.path.exists(self.report_path):
                os.mkdir(self.report_path)
            if not os.path.exists(self.img_path):
                os.mkdir(self.img_path)
        except Exception as e:
            self.log.error(e)

    @staticmethod
    def __clear():
        pyautogui.keyDown("backspace")
        time.sleep(2)
        pyautogui.keyUp("backspace")
        pyautogui.keyDown("delete")
        time.sleep(2)
        pyautogui.keyUp("delete")

    def delete_certs(self):
        # /etc/ssl/certs/802.1X.pfx
        # /etc/ssl/certs/ROOTCA.*
        pass

    def wait_pictures(self, pic_folder_name):
        '''
        Wait a desired picture. If exists, return its coordinate.
        :param pic_folder_name: folder name of pictures. e.g. 'right_down_corner'
        :return: tuple of coordinate. e.g. ()
        '''
        pic_folder = self.path + '/Test_Data/td_network/wired/{}'.format(pic_folder_name)
        result = wait_element(pic_folder, rate=0.97)
        if result:
            return result[0], result[1]
        else:
            self.log.info('Not found {} picture.'.format(pic_folder_name))
            return False

    def __click_picture(self, pic_folder_name, offset=False):
        pic_pos = self.wait_pictures(pic_folder_name)
        if not pic_pos:
            self.log.debug('Fail to find {}.'.format(pic_folder_name), self.img_path + '{}.png'.format(pic_folder_name))
            return False
        if offset is True:
            click_pos = pic_pos[0][0] + pic_pos[1][1], pic_pos[0][1]
        else:
            click_pos = pic_pos[0]
        pyautogui.click(click_pos)
        time.sleep(1)
        return True

    def close_control_panel(self, option='Discard'):
        """
        Close control panel with Apply or Discard option.
        :param option: options for save or discard. e.g. 'Discard'
        :return: none
        """
        subprocess.getoutput("wmctrl -c 'Control Panel'")
        time.sleep(1)
        if option.upper() == 'DISCARD':
            btn_discard = self.wait_pictures('discard')
            if btn_discard:
                pyautogui.click(btn_discard[0])
                time.sleep(1)
        else:
            pyautogui.hotkey('enter')
            time.sleep(1)

    def open_network_wired_dialog(self):
        self.close_control_panel()
        pyautogui.hotkey('ctrl', 'alt', 's')
        time.sleep(1)
        pyautogui.typewrite('network', interval=0.25)
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(1)
        result = self.wait_pictures('wired_tab')
        if result:
            pyautogui.click(result[0])
            self.log.info('open_network_wired_dialog successfully.')
            return True
        else:
            return False

    def set_enable_ipv6(self, option):
        '''
        Enable or disable ipv6 option for Wired.
        :param option: ipv6 option. e.g. 'enable'
        :return: None
        '''
        if self.wait_pictures('ipv6_checked'):
            current = 'enable'
        elif self.wait_pictures('ipv6_unchecked'):
            current = 'disable'
        else:
            return False
        if current.upper() == option.upper():
            self.log.info('Current is {}d'.format(option))
        else:
            self.__click_picture('enable_ipv6', offset=True)
            time.sleep(1)

    def set_ethernet_speed(self, speed):
        """
        Set ethernet speed for Wired.
        :param speed: ethernet speed. e.g. '1000/Full'
        :return: bool value. e.g. True
        """
        if not self.wait_pictures('wired_tab'):
            self.log.debug('Fail to find wired_tab picture.', self.img_path + 'find_wired_tab.png')
            return False
        if not self.__click_picture('ethernet_speed'):
            return False
        if not self.__click_picture('automatic'):
            return False
        if speed.upper() == 'AUTOMATIC':
            self.log.info('Ethernet speed {} is set successfully.'.format(speed))
            return True
        else:
            if not self.__click_picture('ethernet_speed'):
                return False
            if speed.upper() == '1000/FULL':
                click_result = self.__click_picture('1000_full')
            elif speed.upper() == '100/FULL':
                click_result = self.__click_picture('100_full')
            elif speed.upper() == '10/FULL':
                click_result = self.__click_picture('10_full')
            elif speed.upper() == '100/HALF':
                click_result = self.__click_picture('100_half')
            elif speed.upper() == '10/HALF':
                click_result = self.__click_picture('10_half')
            else:
                self.log.info('Invalid speed parameter {}.'.format(speed))
                click_result = False
            if click_result:
                self.log.info('Set Ethernet speed {} successfully.'.format(speed))
            else:
                self.log.info('Set Ethernet speed {} failed.'.format(speed))
            return click_result

    def set_connection_method(self, method):
        """
        Set connection method for Wired.
        :param method: connection method. e.g. 'Static'
        :return: bool value. e.g. True
        """
        if not self.wait_pictures('wired_tab'):
            self.log.debug('Fail to find wired_tab picture.', self.img_path + 'find_wired_tab_in_set_connection_method.png')
            return False
        if not self.__click_picture('connection_method'):
            return False
        if not self.__click_picture('automatic'):
            return False
        if method.upper() == 'AUTOMATIC':
            self.log.info('Connection Method {} is set successfully.'.format(method))
            return True
        else:
            if not self.__click_picture('connection_method'):
                return False
            if method.upper() == 'STATIC':
                click_result = self.__click_picture('static')
            else:
                self.log.info('Invalid method parameter {}.'.format(method))
                click_result = False
            if click_result:
                self.log.info('Set Connection Method {} successfully.'.format(method))
            else:
                self.log.info('Set Connection Method {} failed.'.format(method))
            return click_result

    def set_dynamic_ip(self):
        if not self.set_connection_method('Automatic'):
            self.log.info('Fail to set dynamic ip.')
            return False
        self.close_control_panel('Apply')

    def set_static_ip(self, ip_address, subnet_mask, default_gateway):
        """
        Set static ip for Wired.
        :param ip_address: ip address. e.g. '15.83.247.127'
               subnet_mask: subnet mask. e.g. '255.255.255.192'
               default_gateway: default gateway. e.g. '15.83.0.1'
        :return: None
        """
        if not self.set_connection_method('static'):
            return False
        if not self.__click_picture('ip_address', offset=True):
            return False
        self.__clear()
        pyautogui.typewrite(ip_address, interval=0.2)
        if not self.__click_picture('subnet_mask', offset=True):
            return False
        self.__clear()
        pyautogui.typewrite(subnet_mask, interval=0.2)
        if not self.__click_picture('default_gateway', offset=True):
            return False
        self.__clear()
        pyautogui.typewrite(default_gateway, interval=0.2)
        self.close_control_panel('Apply')

    def __set_authentication(self, authentication):
        pass

    def set_security_settings(self, authentication):
        '''
        Set security settings for Wired.
        :param authentication: authentication type for security settings. e.g. '802.1X-TTLS'
        :return: none
        '''
        if not self.__click_picture('security_settings'):
            return False
        if not self.wait_pictures('advanced_security'):
            self.log.info('Fail to find Advanced Security dialog for security settings.')
            return False
        if not self.__click_picture('authentication', offset=True):
            return False
        if not self.__click_picture('none'):
            return False
        if authentication.upper() == 'NONE':
            if not self.__click_picture('ok'):
                return False
            self.log.info('Security Settings {} is set successfully.'.format(authentication))
            return True
        else:
            if not self.__click_picture('authentication', offset=True):
                return False
            if authentication.upper() == '802.1X-TTLS':
                if not self.__click_picture('802.1X-TTLS'):
                    self.__set_authentication('802.1X-TTLS')
            elif authentication.upper() == '802.1X-PEAP':
                if not self.__click_picture('802.1X-PEAP'):
                    self.__set_authentication('802.1X-PEAP')
            elif authentication.upper() == '802.1X-TLS':
                if not self.__click_picture('802.1X-TLS'):
                    self.__set_authentication('802.1X-TLS')
            else:
                self.log.info('Invalid authentication parameter {}.'.format(authentication))
            return True

    @staticmethod
    def check_wired_is_connected():
        network_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/eth0/IPv4/status")
        if network_status == "1":
            return True
        else:
            return False

    @staticmethod
    def disable_eth0():
        try:
            os.popen("/usr/lib/hptc-network-mgr/common/netmgr_wired --down eth0")
            log.info("disable eth0")
        except Exception as e:
            log.error(e)

    @staticmethod
    def enable_eth0():
        try:
            os.popen("/usr/lib/hptc-network-mgr/common/netmgr_wired --up eth0")
            log.info("enable eth0")
        except Exception as e:
            log.error(e)


class Wireless(NetworkCommon):
    """
    ThinPro control panel -> network -> wireless
    """

    __mask = ""
    __gateway = ""

    # def __init__(self):
    #     self.get_wlan_mask()
    #     self.get_wlan_gateway()

    @staticmethod
    def pic(picture):
        return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "wireless", picture)

    @classmethod
    def get_wlan_mask(cls):
        if not cls.__mask:
            res = subprocess.getoutput("ifconfig | grep eth0 -A 1 | grep -i 'inet'")
            result = re.search(r"(?i)(?:mask)[: ]([\\.\d]+)", res)
            assert result, "Get Mask Fail"
            cls.__mask = result.group(1)
        return cls.__mask

    @classmethod
    def get_wlan_gateway(cls):
        if not cls.__gateway:
            cls.__gateway = subprocess.getoutput("ip route | grep -i 'default'").split()[2]
        return cls.__gateway

    @staticmethod
    def check_wireless_card():
        """
        check the ThinPro has wireless card
        :return: True / Flse
        """
        wc = subprocess.getoutput("iwconfig | grep -i wlan")
        print(wc)
        if "wlan" not in wc:
            return False
        else:
            return True

    def switch_to_wireless_tab(self):
        w = wait_element(self.pic("_wireless_tab"), offset=(20, 10))
        pyautogui.click(w[0])

    def enable_wireless(self):
        enable = wait_element(self.pic("_enable_wireless"), rate=0.99)
        if enable:
            log.info("wireless has enabled")
            return True
        disable = wait_element(self.pic("_disable_wireless"), rate=0.99)
        if disable:
            pyautogui.click(disable[0][0]+97, disable[0][1])
            enable_1 = wait_element(self.pic("_enable_wireless"), rate=0.99)
            if enable_1:
                log.info("enable wireless success")
                return True
            else:
                log.error("enable wireless fail")
                return False

    def disable_wireless(self):
        disable = wait_element(self.pic("_disable_wireless"), rate=0.95)
        if disable:
            log.info("wireless has disabled")
            return True
        enable = wait_element(self.pic("_enable_wireless"), rate=0.99)
        if enable:
            pyautogui.click(enable[0][0] + 97, enable[0][1])
            disable_1 = wait_element(self.pic("_disable_wireless"), rate=0.99)
            if disable_1:
                log.info("disable wireless success")
                return True
            else:
                log.error("disable wireless fail")
                return False

    @staticmethod
    def __clear():
        pyautogui.keyDown("backspace")
        time.sleep(2)
        pyautogui.keyUp("backspace")
        pyautogui.keyDown("delete")
        time.sleep(2)
        pyautogui.keyUp("delete")

    def __choose_cert_from_usb_disk(self, cert):
        pyautogui.click(wait_element(self.pic("_auth_ca_cert_USB_Disk"))[0])
        pyautogui.click(wait_element(self.pic("_auth_USB_Disk"))[0], interval=1)
        # pyautogui.click(wait_element(self.pic("_auth_USB_Disk_certs"))[0], interval=1)
        pyautogui.click(wait_element(self.pic("_auth_USB_Disk_certs_{}".format(cert)))[0], interval=1)
        pyautogui.click(wait_element(self.pic("_auth_PEAP_ca_cert_open"))[0], interval=1)

    def set_ipv4_static(self, ip, subnet_mask, gateway):
        pyautogui.click(wait_element(self.pic("_ipv4_tab"), offset=(20, 10))[0], interval=0.5)
        pyautogui.click(wait_element(self.pic("_ipv4_ipv4_method"), offset=(300, 10))[0], interval=0.5)
        pyautogui.click(wait_element(self.pic("_ipv4_ipv4_method_static"), offset=(10, 10))[0], interval=0.5)
        pyautogui.click(wait_element(self.pic("_ipv4_ipv4_address"), offset=(200, 10))[0])
        self.__clear()
        pyautogui.write(ip, interval=0.1)
        pyautogui.click(wait_element(self.pic("_ipv4_subnet_mask"), offset=(200, 10))[0])
        self.__clear()
        pyautogui.write(subnet_mask, interval=0.1)
        pyautogui.click(wait_element(self.pic("_ipv4_default_gateway"), offset=(200, 10))[0])
        self.__clear()
        pyautogui.write(gateway, interval=0.1)

    def apply_and_ok(self):
        pyautogui.click(wait_element(self.pic("_apply"), offset=(20, 10))[0], interval=1)
        pyautogui.click(wait_element(self.pic("_ok"), offset=(20, 10))[0], interval=1)

    def set_wireless_profile(self, profiles, click=False):

        if "ssid" in profiles:
            if click:
                for _ in range(3):
                    pyautogui.click(wait_element(self.pic("scan_ap"))[0], clicks=2, interval=1)
                    time.sleep(15)
                    pyautogui.click(wait_element(self.pic("scan_ap"), offset=(200, 5))[0])
                    time.sleep(5)
                    ap_loc = wait_element(self.pic(f"_{profiles['ssid']}_add"))
                    if ap_loc:
                        pyautogui.click(ap_loc[0])
                        break
                else:
                    os.popen("wmctrl -c 'HP Wireless Profile Setting'")
                    return f"not found {profiles['ssid']}"
            else:
                pyautogui.click(wait_element(self.pic("_ssid"), offset=(200, 5))[0])
                self.__clear()
                pyautogui.write(profiles["ssid"], interval=0.1)
        if "wireless band" in profiles:
            pyautogui.click(wait_element(self.pic("_wireless_band"), offset=(200, 5))[0])
            band_option = wait_element(self.pic("_band_{}".format(profiles["wireless band"])))
            pyautogui.click(band_option[0])
        if "ssid hidden" in profiles:
            hidden_position = wait_element(self.pic("_ssid_hidden"), offset=(160, 8))
            pyautogui.click(hidden_position[0])

        if "authentication" in profiles:
            pyautogui.click(wait_element(self.pic("_security"))[0])                  # switch to security tab

            authentication = wait_element(self.pic("_authentication"), offset=(200, 8))
            pyautogui.click(authentication[0])
            if "/" in profiles["authentication"]:
                auth = str(profiles["authentication"]).split("/")[1]
            else:
                auth = profiles["authentication"]
            pyautogui.click(wait_element(self.pic("_auth_{}".format(auth)))[0])

            if profiles["authentication"] == "WPA/WPA2-PSK":
                pre_position = wait_element(self.pic("_auth_WPA2-PSK_preshared_key"), offset=(200, 10))
                pyautogui.click(pre_position[0])
                self.__clear()

                if "use hexdecimal psk" in profiles:
                    tool.type_string(profiles["password"][:-1])
                    pyautogui.click(wait_element(self.pic("_auth_WPA2-PSK_hex"), offset=(122, 10))[0])
                    time.sleep(0.5)
                    pyautogui.click(pre_position[0])
                    pyautogui.keyDown("right")
                    time.sleep(7)
                    pyautogui.keyUp("right")
                    tool.type_string(profiles["password"][-1])
                else:
                    tool.type_string(profiles["password"])

            if profiles["authentication"] == "WPA/WPA2 Enterprise-PEAP":
                if "peap version" in profiles and profiles["peap version"] != "Automatic":
                    pass
                if "inner authentication" in profiles and profiles["inner authentication"] != "MSCHAPV2":
                    pass
                if "cert" in profiles:
                    cert_position = wait_element(self.pic("_auth_PEAP_ca_cert"), offset=(330, 10))
                    pyautogui.click(cert_position[0], interval=1)
                    store = wait_element(self.pic("_auth_PEAP_ca_cert_{}".format(profiles["cert select from"])))
                    pyautogui.click(store[0], interval=1)
                    if profiles["cert select from"] == "ThinPro Store":
                        rootca = wait_element(self.pic("_auth_PEAP_ca_cert_rootca"))
                        pyautogui.click(rootca[0])
                        open_position = wait_element(self.pic("_auth_PEAP_ca_cert_open"))
                        pyautogui.click(open_position[0])
                    if profiles["cert select from"] == "SSL Store":
                        pyautogui.click(store[0][0]-100, store[0][1]+200, interval=1)
                        pyautogui.write(profiles["cert"])
                        pyautogui.click(wait_element(self.pic("_auth_PEAP_ca_cert_ssl_rootca"))[0], interval=1)
                        open_position = wait_element(self.pic("_auth_PEAP_ca_cert_open"))
                        pyautogui.click(open_position[0])
                if "anonymous identity" in profiles:
                    anonymous = wait_element(self.pic("_auth_PEAP_anonymous"), offset=(270, 8))
                    pyautogui.click(anonymous[0])
                    self.__clear()
                    pyautogui.write(profiles["anonymous identity"], interval=0.1)
                if "username" in profiles:
                    username = wait_element(self.pic("_auth_username"), offset=(270, 8))
                    pyautogui.click(username[0])
                    self.__clear()
                    pyautogui.write(profiles["username"], interval=0.1)
                if "password" in profiles:
                    password = wait_element(self.pic("_auth_password"), offset=(270, 8))
                    pyautogui.click(password[0])
                    self.__clear()
                    tool.type_string(profiles["password"])

            if profiles["authentication"] == "WPA/WPA2 Enterprise-TLS":
                if profiles["cert select from"] == "USB Disk":
                    pyautogui.click(wait_element(self.pic("_auth_PEAP_ca_cert"), offset=(330, 10))[0])    # ca certificate
                    self.__choose_cert_from_usb_disk(cert=profiles["ca certificate"])

                    pyautogui.click(wait_element(self.pic("_auth_TLS_user_cert"), offset=(330, 10))[0])  # user certificate
                    self.__choose_cert_from_usb_disk(cert=profiles["user certificate"])

                    pyautogui.click(wait_element(self.pic("_auth_TLS_private_key"), offset=(330, 10))[0])  # private_key
                    self.__choose_cert_from_usb_disk(cert=profiles["private key"])

                if "identity" in profiles:
                    pyautogui.click(wait_element(self.pic("_auth_TLS_identity"), offset=(200, 10))[0])
                    self.__clear()
                    pyautogui.write(profiles["identity"], interval=0.1)

                    if "password" in profiles:
                        pyautogui.click(wait_element(self.pic("_auth_TLS_password"), offset=(200, 10))[0])
                        self.__clear()
                        pyautogui.write(profiles["password"], interval=0.1)

            if profiles["authentication"] == "EAP-FAST":
                if "anonymous identity" in profiles:
                    pyautogui.click(wait_element(self.pic("_auth_PEAP_anonymous"), offset=(200, 10))[0])
                    self.__clear()
                    pyautogui.write(profiles["anonymous identity"], interval=0.1)
                if "username" in profiles:
                    pyautogui.click(wait_element(self.pic("_auth_username"), offset=(200, 10))[0])
                    self.__clear()
                    pyautogui.write(profiles["username"], interval=0.1)
                if "password" in profiles:
                    pyautogui.click(wait_element(self.pic("_auth_password"), offset=(200, 10))[0])
                    self.__clear()
                    pyautogui.write(profiles["password"], interval=0.1)
                if "fast provisioning" in profiles:
                    pyautogui.click(wait_element(self.pic("_auth_EAP_FAST_Fast_Provisioning"), offset=(200, 10))[0],
                                    interval=1)
                    pyautogui.click(wait_element(self.pic("_auth_EAP_FAST_Fast_Provisioning_{}"
                                                          .format(profiles["fast provisioning"])), offset=(30, 10))[0],
                                    interval=1)

    def add(self, ssid, **kwargs):
        ip = '15.83.252.100'
        mask = '255.255.255.192'
        gateway = '15.83.252.65'
        log.info("add '{}' wireless profile".format(ssid))
        profile = YamlOperator(self.network_profile()).read()[ssid]
        log.info("click add button")
        pyautogui.click(wait_element(self.pic("_add"))[0], interval=2)          # click add
        click = kwargs.get('click', '')
        if click:
            res = self.set_wireless_profile(profile, click=True)
            if res:
                return res
        else:
            self.set_wireless_profile(profile)
        static_ip = kwargs.get("static_ip", "")
        if static_ip:
            self.set_ipv4_static(ip=ip, subnet_mask=mask, gateway=gateway)

    def edit(self, ssid, edit_value_dict):
        """
            edit_value_dict like : {"ssid": "R1-TC_5G_n", "password": "neoware1234", ...  ,
            "static_ip": [ip, subnet_mask, gateway]}
        """
        log.info("edit '{}' wireless profile".format(ssid))
        icon = wait_element(self.pic("_move_mouse"), offset=(0, 10))[0]
        tool.click(icon[0], icon[1], num=2)
        if wait_element(self.pic("_{}".format(ssid))):
            pyautogui.click(wait_element(self.pic("_{}".format(ssid)))[0], interval=2)
            pyautogui.click(wait_element(self.pic("_edit"))[0], interval=2)
        else:
            down_menu = wait_element(self.pic("_down_menu"))[0]
            if down_menu:
                tool.click(down_menu[0], down_menu[1], num=10)
                if wait_element(self.pic("_{}".format(ssid))):
                    pyautogui.click(wait_element(self.pic("_{}".format(ssid)))[0], interval=2)
                    pyautogui.click(wait_element(self.pic("_edit"))[0], interval=2)
                else:
                    log.info('{} wireless not exists'.format(ssid))
                    return False
            else:
                log.info('{} wireless not exists'.format(ssid))
                return False
        self.set_wireless_profile(edit_value_dict)
        if "static_ip" in edit_value_dict.keys():
            self.set_ipv4_static(ip=edit_value_dict["static_ip"][0], subnet_mask=edit_value_dict["static_ip"][1],
                                 gateway=edit_value_dict["static_ip"][2])
        self.apply_and_ok()

    def delete(self, ssid=""):
        icon = wait_element(self.pic("_move_mouse"), offset=(0, 10))[0]
        tool.click(icon[0], icon[1], num=2)
        if ssid:
            log.info("delete '{}' wireless ".format(ssid))
            if wait_element(self.pic("_{}".format(ssid))):
                pyautogui.click(wait_element(self.pic("_{}".format(ssid)))[0], interval=2)
                pyautogui.press(keys='tab', presses=3)
                pyautogui.press(keys='space')
                pyautogui.press(keys='space')
            else:
                down_menu = wait_element(self.pic("_down_menu"))
                if down_menu:
                    tool.click(down_menu[0][0], down_menu[0][1], num=10)
                    if wait_element(self.pic("_{}".format(ssid))):
                        pyautogui.click(wait_element(self.pic("_{}".format(ssid)))[0], interval=2)
                        pyautogui.press(keys='tab', presses=3)
                        pyautogui.press(keys='space')
                        pyautogui.press(keys='space')
                    else:
                        log.info('{} wireless not exists'.format(ssid))
                        return False
                else:
                    log.info('{} wireless not exists'.format(ssid))
                    return False
        else:
            log.info("delete the first wireless ".format(ssid))
            ssid_title = wait_element(self.pic("_ssid_title".format(ssid)), offset=(20, 30))[0]
            tool.click(ssid_title[0], ssid_title[1])
            pyautogui.click(wait_element(self.pic("_delete"))[0], interval=2)
            pyautogui.click(wait_element(self.pic("_yes"))[0], interval=2)

    def wl_set_apply(self):
        apply = wait_element(self.common_pic("_apply"))
        if apply:
            pyautogui.click(apply[0], interval=2)
            time.sleep(2)

    @staticmethod
    def check_wireless_connected():
        wireless_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/wlan0/IPv4/status")
        if wireless_status == "1":
            return True
        else:
            return False

    @staticmethod
    def scanning_ap():
        essid = subprocess.getoutput("iwlist wlan0 scanning | grep -i essid")
        ssid_list = []
        for i in essid.split():
            ssid = re.findall('"(.*)"', i)
            ssid_list.append(ssid[0])
        return ssid_list

    def connected_wireless_info(self):
        """
        :return: {'ssid': 'R1-TC_5G_n', 'ip': '15.83.252.84', 'network mask': '255.255.255.192',
                  'gatewary': '15.83.252.65', 'channel': '161'}
        """
        info = dict()
        s = subprocess.getoutput("iwconfig wlan0 | grep SSID")
        ssid = re.findall('"(.*)"', s)
        if ssid:
            info["ssid"] = ssid[0]
            info["ip"] = cf.get_ip()
            info["network mask"] = self.get_wlan_mask()
            info["gatewary"] = self.gateway()
            w = subprocess.getoutput("iwconfig wlan0 | grep -i 'access point'")
            mac = w.split("Access Point:")[-1].strip()
            command = "iwlist wlan0 scan | grep '{}' -A 2 | grep Channel".format(mac)
            chan = subprocess.getoutput(command)
            channel = chan.strip().split(":")[1].split("\n")[0]
            info["channel"] = channel
            return info
        else:
            return None

    @staticmethod
    def get_saved_ssid():
        """
        ['R1-TC_5G_ax_WPA2P', 'R1-TC_5G_n']
        :return:
        """
        ssid_list = []
        ssid_id = subprocess.getoutput("mclient --quiet get root/Network/Wireless/Profiles")
        for s in ssid_id.split():
            ssid = subprocess.getoutput("mclient --quiet get {}/SSID".format(s))
            ssid_list.append(ssid)
        return ssid_list

    @staticmethod
    def scan_wireless(SSID):
        c = 0
        scan_times = 5
        for i in range(scan_times):
            time.sleep(1)
            all_ssid = subprocess.getoutput("iwlist wlan0 scan | grep ESSID")
            if SSID in all_ssid:
                c += 1
        if c == scan_times:
            log.info("Found {} in environment and signal stable. Scan {} times found {} times.".format(SSID, scan_times, c))
            return True
        elif c == 0:
            log.info("Can't find {} in environment, scan {} times found {} times.".format(SSID, scan_times, c))
            return False
        else:
            log.info("Found {} in environment but signal not stable. Scan {} times found {} times.".format(SSID, scan_times, c))
            return True

    @staticmethod
    def wired_wireless_switch(enable):
        if enable.upper() == 'ON':
            subprocess.getoutput("mclient set root/Network/WiredWirelessSwitch 1 && mclient commit")
        elif enable.upper() == 'OFF':
            subprocess.getoutput("mclient set root/Network/WiredWirelessSwitch 0 && mclient commit")
        else:
            log.info('Invalid parameter: {}'.format(enable))
        curr_value = subprocess.getoutput('mclient --quiet get root/Network/WiredWirelessSwitch')
        if all([enable.upper() == 'ON', curr_value == '1']) or all([enable.upper() == 'OFF', curr_value == '0']):
            log.info('WiredWirelessSwitch set successfully. Value is {}.'.format(curr_value))
        else:
            log.info('Fail to set WiredWirelessSwitch.')

    @staticmethod
    def now_connected_wireless():
        count = 0
        for i in range(60):
            time.sleep(1)
            count += 1
            s = subprocess.getoutput("iwconfig wlan0 | grep SSID")
            pattern = re.compile('"(.*)"')
            ssid_list = pattern.findall(s)
            if len(ssid_list) == 1:
                ssid = ssid_list[0]
                return ssid
            else:
                continue
        if count == 60:
            log.info('Fail to connect to wireless after {} seconds.'.format(count))
            return 'timeout'

    @staticmethod
    def del_wireless_profile_from_reg():
        profiles = subprocess.getoutput("mclient --quiet get root/Network/Wireless/Profiles").splitlines()
        if profiles:
            log.info('found wireless profiles')
            for profile in profiles:
                profile_name = profile.split('/')[-1].strip()
                os.system('mclient delete root/Network/Wireless/Profiles/{}'.format(profile_name))
                os.system('mclient commit root/Network/Wireless')

            if not subprocess.getoutput("mclient --quiet get root/Network/Wireless/Profiles").splitlines():
                log.info("delete all wireless profiles success")
                return True
            else:
                log.error("delete all wireless profiles fail")
                return False
        else:
            log.info('Currently no wireless profiles')
            return True

    @staticmethod
    def __wireless_channel_list_query(start, end, exp_status='active'):
        flag = False
        output_list = os.popen("iw list | grep \'MHz\' | sed -n '{}, {}p'".format(start, end)).readlines()
        if not output_list:
            log.info('No result for querying specific wireless channel.')
            return flag
        if exp_status.upper() == 'ACTIVE':
            func = lambda x: '.0 dBm)' in x
        elif exp_status.upper() == 'DISABLED':
            func = lambda x: '(disabled)' in x
        else:
            log.info('Invalid expected status.')
            return flag
        for item in output_list:
            if not func(item):
                return flag
        flag = True
        return flag

    def indo_wireless_channels_5g_check(self):
        start_5g = subprocess.getoutput("iw list | grep \'MHz\' | grep -n '\[36\]' | awk -F: '{print $1}'")
        end_5g = subprocess.getoutput("iw list | grep \'MHz\' | grep -n '\[165\]' | awk -F: '{print $1}'")
        start_indo = subprocess.getoutput("iw list | grep \'MHz\' | grep -n '\[149\]' | awk -F: '{print $1}'")
        end_indo = subprocess.getoutput("iw list | grep \'MHz\' | grep -n '\[161\]' | awk -F: '{print $1}'")
        check_indo = self.__wireless_channel_list_query(start_indo, end_indo)
        check_prior = self.__wireless_channel_list_query(start_5g, str(int(start_indo) - 1), exp_status='disabled')
        check_post = self.__wireless_channel_list_query(str(int(end_indo) + 1), end_5g, exp_status='disabled')
        if all([check_indo, check_prior, check_post]):
            log.info('Check wireless channel 5g for indo is successful.')
            return True
        else:
            log.info('Check wireless channel 5g for indo is failed.')
            return False

    def restore_wireless(self):
        self.open_network()
        self.switch_to_wireless_tab()
        self.enable_wireless()
        self.apply()
        self.close_control_panel()


class DNS(NetworkCommon):
    """
    thinpro control panel -> network -> DNS
    """
    @staticmethod
    def dns_pic(name):
        return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "dns", "{}.png".format(name))

    def open_dns(self):
        log.info('Open NetWork DNS from Control Panel')
        for i in range(2):
            self.open_network()
            time.sleep(5)
            icon_location = wait_element(self.dns_pic("dns"), offset=(10, 10))
            if not icon_location:
                log.info('not find position {}'.format(self.dns_pic("dns")))
                continue
            tool.click(icon_location[0][0], icon_location[0][1], 1)
            break
        return True

    def __set_value(self, name, text):
        icon_location = wait_element(self.dns_pic(name), offset=(200, 10))
        if icon_location:
            tool.click(icon_location[0][0], icon_location[0][1], 3)
            time.sleep(0.5)
            pyautogui.press('backspace')
        else:
            log.info('not find position {}'.format(self.dns_pic(name)))
            return
        time.sleep(1)
        pyautogui.typewrite(text)
        return True

    def set_value(self, name, text):
        log.info('set DNS {} Proxy: {}'.format(name, text))
        return self.__set_value(name, text)

    def dns_set_hostname(self, text):
        log.info('set DNS Hostname {}'.format(text))
        return self.__set_value('hostname', text)

    def dns_set_server(self, text):
        log.info('set DNS Servers {}'.format(text))
        return self.__set_value('server', text)

    def dns_set_domain(self, text):
        log.info('set DNS Search Domains {}'.format(text))
        return self.__set_value('domains', text)

    def dns_set_http_proxy(self, text):
        log.info('set DNS HTTP Proxy {}'.format(text))
        return self.__set_value('http', text)

    def dns_set_ftp_proxy(self, text):
        log.info('set DNS FTP Proxy {}'.format(text))
        return self.__set_value('ftp', text)

    def dns_set_https_proxy(self, text):
        log.info('set DNS HTTPs Proxy {}'.format(text))
        return self.__set_value('https', text)

    def dns_set_no_proxy(self, text):
        log.info('set DNS No Proxy {}'.format(text))
        return self.__set_value('noproxy', text)

    def close_dns(self):
        log.info('Close NetWork DNS')
        return self.close_control_panel(option='apply')

    def clear_text(self, name):
        log.info('clear {} proxy info'.format(name))
        icon_location = wait_element(self.dns_pic(name), offset=(200, 10))
        if icon_location:
            tool.click(icon_location[0][0], icon_location[0][1], 3)
        else:
            return
        time.sleep(1)
        pyautogui.press('backspace')
        time.sleep(0.5)
        return True


class VPN(NetworkCommon):
    """
    thinpro control panel -> network -> VPN
    """
    @staticmethod
    def vpn_pic(picture):
        return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "vpn", picture)

    def switch_to_vpn_tab(self):
        pyautogui.click(wait_element(self.vpn_pic("_vpn_tab"), offset=(20, 10))[0])

    @staticmethod
    def __clear():
        pyautogui.keyDown("backspace")
        time.sleep(2)
        pyautogui.keyUp("backspace")
        pyautogui.keyDown("delete")
        time.sleep(2)
        pyautogui.keyUp("delete")

    def enable_auto_start(self):
        log.info("start enable auto start")
        enable = wait_element(self.vpn_pic("_auto_start_enable"), rate=0.99)
        if enable:
            log.info("auto start has enabled")
            return True
        else:
            pyautogui.click(wait_element(self.vpn_pic("_auto_start_disable"), rate=0.99, offset=(320, 10))[0])
            log.info("enable auto start complate")
            return True

    def disable_auto_start(self):
        disable = wait_element(self.vpn_pic("_auto_start_disable"), rate=0.99)
        if disable:
            log.info("auto start has disabled")
            return True
        else:
            pyautogui.click(wait_element(self.vpn_pic("_auto_start_enable"), rate=0.99, offset=(320, 10))[0])
            log.info("disable auto start complate")
            return True

    def set_vpn(self, type, profile="profile_1", **kwargs):
        log.info("start set vpn")
        if type.lower() not in ["cisco", "pptp", "none"]:
            log.error("vpn type error")
            return False
        pyautogui.click(wait_element(self.vpn_pic("_connection_type"), offset=(400, 10))[0], interval=1)
        pyautogui.click(wait_element(self.vpn_pic("_type_{}".format(type.lower())))[0], interval=1)
        if type.lower() == "none":
            pass
        else:
            profile_data = YamlOperator(self.network_profile()).read()["vpn"][type.lower()][profile]
            print(profile_data)
            for key, value in profile_data.items():
                pic_name = "_{}".format("_".join(key.split()))
                pyautogui.click(wait_element(self.vpn_pic(pic_name), offset=(200, 10))[0], interval=0.2)
                self.__clear()
                pyautogui.write(value, interval=0.1)
        auto_start = kwargs.get("auto_start", "null")
        if auto_start.lower() == "enable":
            self.enable_auto_start()
        elif auto_start.lower() == "disable":
            self.disable_auto_start()
        else:
            pass
        log.info("set vpn complete")
        return True

    @staticmethod
    def get_vpn_ip(vpn_type):
        protocol = ''
        if vpn_type.upper() == 'CISCO':
            protocol = 'tun0'
        elif vpn_type.upper() == 'PPTP':
            protocol = 'ppp0'
        else:
            log.info('Invalid type ')
        timeout = 0
        for i in range(30):
            time.sleep(1)
            result = subprocess.getoutput("ifconfig | grep {} -A 1 | grep -i 'inet'".format(protocol))
            sys_ip = re.search(r"(?i)(?:inet|inet addr)[: ]([\\.\d]+)", result)
            if sys_ip:
                return sys_ip.group(1)
            else:
                timeout += 1
        if timeout == 30:
            log.info('Fail to get {} ip after timeout {}.'.format(protocol, timeout))
            return False

    @staticmethod
    def trace_route():
        first_route = subprocess.getoutput('traceroute 15.83.240.98 | sed -n 2p | awk \'{print $2}\'')
        if first_route:
            if first_route.strip() == '15.83.240.141':
                log.info('Traceroute successfully.')
                return True
            else:
                log.info('Traceroute failed.')
                return False
        else:
            log.info('Fail to traceroute.')
            return False

    @staticmethod
    def clear_vpn():
        subprocess.getoutput('mclient --quiet set root/Network/VPN/Type None && mclient commit && mclient --quiet '
                             'set root/Network/VPN/AutoStart 0 && mclient commit')
        vpn_type = subprocess.getoutput('mclient --quiet get root/Network/VPN/Type')
        auto_start = subprocess.getoutput('mclient --quiet get root/Network/VPN/AutoStart')
        if vpn_type.strip() == 'None' and auto_start.strip() == '0':
            log.info('Clear vpn successfully.')
            return True
        else:
            log.info('Fail to clear vpn.')
            return False


if __name__ == '__main__':
    # from Test_Script.ts_network import network_setting

    # wireless = network_setting.Wireless()

    # wireless.add(ssid="R1-Linux-TKIP")
    # wireless.add(ssid="R1-TC_2.4G_n_WPA2P")
    # wireless.add(ssid="R1-TC_5G_ac_WPA2P")
    # wireless.add(ssid="R1-TC_5G_n")
    # wireless.add(ssid="R1-Linux-5N_thinpro_store")
    # wireless.add(ssid="R1-Linux-5N_ssl_store")
    # wireless.add(ssid="R1-Linux-EAP")
    # wireless.add(ssid="R1-TC_2.4G_n_WPA2P", static_ip=True)  # use static ip

    # wireless.apply_and_ok()

    # vpn = network_setting.VPN()
    # vpn.open_network()
    # vpn.switch_to_vpn_tab()
    # vpn.enable_auto_start()
    # vpn.disable_auto_start()
    # vpn.set_vpn(type="cisco", profile="profile_1", auto_start="enable")
    # vpn.set_vpn(type="pptp", auto_start="disable")
    # vpn.set_vpn(type="none", auto_start="disable")
    pass
