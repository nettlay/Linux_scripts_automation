from Test_Script.ts_common.common import CaseFlowControl
from Common.exception import CaseRunningError
from Test_Script.ts_network.network import Network, ping, StaticIpUtils
from Common.log import log
from Common.common_function import SwitchThinProMode, reboot_command


class VerifyStaticIp(CaseFlowControl):

    def __init__(self, script_name, case_name, exception=(CaseRunningError, )):
        super().__init__(script_name=script_name, case_name=case_name, exception=exception)
        self.network = Network.create_object()

    def set_wired(self):
        """
        Index: 0
        """
        self.set_callback_fail(['close_network_panel_callback'])
        info = StaticIpUtils.read_info_from_yaml()
        format_ip = info["ip"]
        format_mask = info["mask"]
        format_gateway = info["gateway"]

        SwitchThinProMode("admin")
        self.network.close()
        self.network.open()
        self.network.connection_method.click()
        self.network.static.click()
        self.network.ip_address.send_keys(format_ip)
        self.network.mask.send_keys(format_mask)
        self.network.gateway.send_keys(format_gateway)
        self.network.apply.click()
        self.network.wait_until_network_connected()

    def __ping_method(self, target_ip="15.83.240.98", expectation=True):
        ping_result = ping(target_ip, count=15)
        if ping_result is expectation:
            log.info(f"Ping {target_ip} Success! Expect: {expectation} Actual: {ping_result}")
        else:
            raise CaseRunningError(f"Ping {target_ip} Fail! Expect: {expectation} Actual: {ping_result}")

    def check_set_wired_success_with_ping(self):
        """
        Index: 1
        """
        self.set_callback_success(['reboot'])
        self.set_callback_fail(['close_network_panel_callback',
                                'enable_wired_callback',
                                'restore_automatic_callback',
                                'end_and_reboot'])
        self.__ping_method(expectation=True)
        self.create_list_index_file_and_suspend(index=2)

    def reboot(self):
        reboot_command()

    def end_and_reboot(self):
        self.end_flow()
        reboot_command()

    def ping_after_reboot(self):
        """
        Index: 2
        """
        self.set_callback_success(['restore_automatic_callback',
                                   'end_and_reboot'])
        self.set_callback_fail(['enable_wired_callback',
                                'restore_automatic_callback',
                                'end_and_reboot'])
        self.network.wait_until_network_connected()
        self.__ping_method(expectation=True)

    def close_network_panel_callback(self):
        self.network.close()

    def enable_wired_callback(self):
        Network.enable_wired()

    def restore_automatic_callback(self):
        Network.set_connection_mode_automatic_with_command()

    def set_method_list(self) -> list:

        return ['set_wired',
                'check_set_wired_success_with_ping',
                'ping_after_reboot',
                ]

    def start(self):
        if super().start() is False:
            return False
        return True


def start(case_name, **kwargs):
    v = VerifyStaticIp(script_name=VerifyStaticIp.__name__, case_name=case_name)
    v.start()