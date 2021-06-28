# case name: check connectivity with the SSID R1-Linux-AC by Control Panel
# Author: nick.lu

from Test_Script.ts_common.common import CaseFlowControl, search_file_from_usb, run_command
from Common.exception import CaseRunningError, PicNotFoundError
from Common.common_function import reboot_command, SwitchThinProMode
from Test_Script.ts_network.network import Network, ping, WirelessStatistics, CertificateUtil
from Test_Script.ts_network.network_setting import Wireless
from Common.log import log


class CheckSSIDR1LinuxAC(CaseFlowControl):
    ap_name = "R1-Linux-AC"
    username = r"spcpass5"
    password = "+=_,-?<>~"
    cert_name = 'ROOTCA.cer'

    def __init__(self, script_name, case_name, exception=(CaseRunningError, )):
        super().__init__(script_name=script_name, case_name=case_name, exception=exception)
        self.network = Network.create_object()
        self.wireless_statistics = WirelessStatistics.create_object()
        self.cert_util = CertificateUtil.create_object()

    def set_wireless(self):
        """
        Index: 0
        """
        self.set_callback_fail(['close_Cert_Window',
                                'enable_wired',
                                'del_wireless_profile_from_reg',
                                'close_wireless_callback'])
        SwitchThinProMode("admin")

        cert_path = search_file_from_usb(self.cert_name)
        self.cert_util.import_cert(file_path=cert_path)
        Network.wired_wireless_switch_off()
        Network.disabled_wired()
        self.network.close()
        self.network.open()
        self.network.wireless.click()
        self.network.add.click()
        self.network.ssid.send_keys(self.ap_name)
        self.network.security.click()
        self.network.authentication.click()
        self.network.wpa2_peap.click()
        cert_row = self.network.wpa2_peap_ca_cert
        cert_row.wpa2_peap_ca_cert_open.click()
        self.network.wpa2_peap_cert_thinpro_store.click()
        self.network.wpa2_cert_rootca_pem.click()
        self.network.wpa2_peap_cert_open.click()
        self.network.wpa2_username.send_keys(self.username)
        self.network.wpa2_password.send_keys(self.password)

        self.network.wireless_apply.click()
        self.network.wireless_ok.click()

        self.network.apply.click()

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
                                'del_wireless_profile_from_reg',
                                'close_wireless_callback'])
        self.network.wait_until_wireless_connected()
        self.__ping_method()
        self.create_list_index_file_and_suspend(index=2)

    def ping_after_reboot(self):
        """
        Index: 2
        """
        SwitchThinProMode("admin")

        self.set_callback_success(['enable_wired',
                                   'del_wireless_profile_from_reg'])
        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg'])
        self.network.wait_until_wireless_connected()
        self.__ping_method()

    def reboot(self):
        reboot_command()

    def close_Cert_Window(self):
        run_command("wmctrl -c 'Certificate Authority Certificate' ")

    def close_wireless_callback(self):
        self.network.close()

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
            'ping_after_reboot'
            ]

    def start(self):
        if super().start() is False:
            return False
        return True


def start(case_name, **kwargs):
    v = CheckSSIDR1LinuxAC(script_name=CheckSSIDR1LinuxAC.__name__, case_name=case_name)
    v.start()
