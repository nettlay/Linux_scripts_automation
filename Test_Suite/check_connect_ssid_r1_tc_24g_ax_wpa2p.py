# case name: check connectivity with the SSID R1-TC-2.4G_ax_WPA2P by Systray Icon
# Author: nick.lu
import time
from Test_Script.ts_common.common import CaseFlowControl, search_file_from_usb, run_command
from Common.exception import CaseRunningError, PicNotFoundError
from Common.common_function import reboot_command, SwitchThinProMode
from Test_Script.ts_network.network import Network, ping, WirelessStatistics,\
    CertificateUtil, SSIDPanel
from Test_Script.ts_network.network_setting import Wireless
from Common.log import log


class CheckR1TC24GaxWPA2PBySystray(CaseFlowControl):
    password = "neoware1234"

    def __init__(self, script_name, case_name, exception=(CaseRunningError,)):
        super().__init__(script_name=script_name, case_name=case_name, exception=exception)
        self.network = Network.create_object()
        self.ssid_panel = SSIDPanel.create_object()
        self.cert_util = CertificateUtil.create_object()

    def set_wireless(self):
        """
        Index: 0
        """
        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg',
                                'close_ssid_windows'])
        SwitchThinProMode("admin")
        Network.wired_wireless_switch_off()
        Network.disabled_wired()
        time.sleep(5)
        disconnected_wireless = self.network.wireless_tray_disconnected
        disconnected_wireless.click()
        self.network.scan_ap.click()
        disconnected_wireless.click()
        self.network.R1TC24GaxWPA2P.click()
        time.sleep(5)
        self.ssid_panel.password.send_keys(self.password)
        self.ssid_panel.ssid_ok.click()

    def __ping_method(self, target_ip="15.83.240.98", expectation=True):
        ping_result = ping(target_ip, count=15)
        if ping_result is expectation:
            log.info(f"Ping {target_ip} Success! Expect: {expectation} Actual: {ping_result}")
        else:
            raise CaseRunningError(f"Ping {target_ip} Fail! Expect: {expectation} Actual: {ping_result}")

    def check_network_with_ping(self):
        """
        Index: 1
        """
        self.set_callback_success(['reboot'])
        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg'])
        self.network.wait_until_wireless_connected()
        self.__ping_method()
        self.create_list_index_file_and_suspend(index=2)

    def ping_after_reboot(self):
        """
        Index: 2
        """
        SwitchThinProMode("admin")

        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg'])
        self.network.wait_until_wireless_connected()
        self.__ping_method()

    def disconnect_ssid(self):
        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg'])
        connected_wireless = self.network.wireless_connected
        connected_wireless.click()
        self.network.R1TC24GaxWPA2P.click()
        time.sleep(5)

    def check_network_with_ping_after_reboot(self):
        self.set_callback_success(['enable_wired',
                                   'del_wireless_profile_from_reg'])
        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg'])
        self.network.wait_until_network_disconnected()
        self.__ping_method(expectation=False)

    def reboot(self):
        reboot_command()

    def close_ssid_windows(self):
        self.ssid_panel.close()

    def del_wireless_profile_from_reg(self):
        Wireless.del_wireless_profile_from_reg()

    def enable_wired(self):
        Network.wired_wireless_switch_on()
        Network.enable_wired()

    def end_and_reboot(self):
        self.end_flow()
        reboot_command()

    def set_method_list(self) -> list:
        return [
            'set_wireless',
            'check_network_with_ping',
            'ping_after_reboot',
            'disconnect_ssid',
            'check_network_with_ping_after_reboot'
        ]

    def start(self):
        if super().start() is False:
            return False
        return True


def start(case_name, **kwargs):
    v = CheckR1TC24GaxWPA2PBySystray(script_name=CheckR1TC24GaxWPA2PBySystray.__name__, case_name=case_name)
    v.start()
