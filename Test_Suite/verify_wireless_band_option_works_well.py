import time
from Test_Script.ts_common.common import CaseFlowControl
from Common.exception import CaseRunningError, PicNotFoundError
from Common.common_function import reboot_command, SwitchThinProMode
from Test_Script.ts_network.network import Network, ping, WirelessStatistics
from Test_Script.ts_network.network_setting import Wireless
from Common.log import log


class VerifyWirelessBandOption(CaseFlowControl):
    password = "neoware1234"

    def __init__(self, script_name, case_name, exception=(CaseRunningError, )):
        super().__init__(script_name=script_name, case_name=case_name, exception=exception)
        self.network = Network.create_object()
        self.wireless_statistics = WirelessStatistics.create_object()
        self.__initial_frequency = 2.4

    def set_wireless(self):

        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg',
                                'close_wireless_callback'])
        SwitchThinProMode("admin")

        Network.wired_wireless_switch_off()
        Network.disabled_wired()
        self.network.close()
        self.network.open()
        self.network.wireless.click()
        self.network.add.click()
        self.network.scan_ap.click()
        ap = self.__wait_until_ap_appear()
        ap.click()
        self.network.R1_Linux_Roaming.click()
        self.network.wireless_band.click()
        self.network.GHZ24.click()
        self.network.security.click()
        self.network.authentication.click()
        self.network.wpa2_psk.click()
        self.network.preshared_key.send_keys(self.password)
        self.network.wireless_apply.click()
        self.network.wireless_ok.click()

        self.network.apply.click()

    def __ping_method(self, target_ip="15.83.240.98", expectation=True):
        ping_result = ping(target_ip, count=15)
        if ping_result is expectation:
            log.info(f"Ping {target_ip} Success! Expect: {expectation} Actual: {ping_result}")
        else:
            raise CaseRunningError(f"Ping {target_ip} Fail! Expect: {expectation} Actual: {ping_result}")

    def __wait_until_ap_appear(self, time_out=60, interval=5):
        while time_out:
            try:
                return self.network.signal
            except PicNotFoundError:
                time_out -= interval
                log.info("Waiting AP Appear")
                time.sleep(interval)
        raise CaseRunningError(f"Click Scan AP, But Waiting AP Appear Fail")

    def check_frequency_and_ping(self):
        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg',
                                'close_wireless_callback'])
        self.network.wait_until_wireless_connected()
        self.__ping_method()
        self.network.check_frequency(self.__initial_frequency)

    def edit_settings_to_5g(self):
        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg',
                                'close_wireless_callback'])
        self.__initial_frequency = 5
        self.network.created_item.click()
        self.network.edit.click()
        self.network.wireless_band.click()
        self.network.GHZ5.click()
        self.network.security.click()
        self.network.wireless_apply.click()
        self.network.wireless_ok.click()

        self.network.apply.click()

    def check_frequency_and_ping_after_set_5g(self):
        self.check_frequency_and_ping()

    def edit_settings_to_auto(self):
        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg',
                                'close_wireless_callback',
                                'close_wireless_statistics'])
        self.network.created_item.click()
        self.network.edit.click()
        self.network.wireless_band.click()
        self.network.auto.click()
        self.network.security.click()
        self.network.wireless_apply.click()
        self.network.wireless_ok.click()

        self.network.apply.click()

        self.wireless_statistics.open()
        self.wireless_statistics.fresh.click()
        time.sleep(10)

    def ping_after_set_auto(self):
        self.set_callback_success(['enable_wired',
                                   'del_wireless_profile_from_reg',
                                   'close_wireless_callback',
                                   'close_wireless_statistics'])
        self.set_callback_fail(['enable_wired',
                                'del_wireless_profile_from_reg',
                                'close_wireless_callback',
                                'close_wireless_statistics'])
        self.network.wait_until_wireless_connected()
        self.__ping_method()

    def close_wireless_statistics(self):
        self.wireless_statistics.close()

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
            'check_frequency_and_ping',
            'edit_settings_to_5g',
            'check_frequency_and_ping_after_set_5g',
            'edit_settings_to_auto',
            'ping_after_set_auto'
            ]

    def start(self):
        if super().start() is False:
            return False
        return True


def start(case_name, **kwargs):
    v = VerifyWirelessBandOption(script_name=VerifyWirelessBandOption.__name__, case_name=case_name)
    v.start()
