from Test_Script.ts_common.common import CaseFlowControl
from Common.exception import CaseRunningError
from Test_Script.ts_network.network import Network, ping
from Common.log import log
from Common.common_function import SwitchThinProMode


class VerifyDynamicIp(CaseFlowControl):

    def __init__(self, script_name, case_name, exception=(CaseRunningError, )):
        super().__init__(script_name=script_name, case_name=case_name, exception=exception)
        self.network = Network.create_object()

    def set_wired(self):
        self.set_callback_fail(['close_network_panel_callback'])

        SwitchThinProMode("admin")
        self.network.close()
        self.network.open()
        self.network.connection_method.click()
        self.network.automatic.click()
        self.network.apply.click()
        self.network.wait_until_network_connected()

    def __ping_method(self, target_ip="15.83.240.98", expectation=True):
        ping_result = ping(target_ip, count=15)
        if ping_result is expectation:
            log.info(f"Ping {target_ip} Success! Expect: {expectation} Actual: {ping_result}")
        else:
            raise CaseRunningError(f"Ping {target_ip} Fail! Expect: {expectation} Actual: {ping_result}")

    def check_set_wired_success_with_ping(self):
        self.set_callback_fail(['close_network_panel_callback'])
        self.__ping_method(expectation=True)

    def disable_wired_and_ping(self):
        self.set_callback_fail(['close_network_panel_callback', 'enable_wired_callback'])
        Network.disabled_wired()
        self.network.wait_until_network_disconnected()
        self.__ping_method(expectation=False)

    def enable_wired_and_ping(self):
        self.set_callback_success(['close_network_panel_callback', ])
        self.set_callback_fail(['close_network_panel_callback', 'enable_wired_callback'])
        Network.enable_wired()
        self.network.wait_until_network_connected()
        self.__ping_method(expectation=True)

    def close_network_panel_callback(self):
        self.network.close()

    def enable_wired_callback(self):
        Network.enable_wired()

    def set_method_list(self) -> list:

        return ['set_wired',
                'check_set_wired_success_with_ping',
                'disable_wired_and_ping',
                'enable_wired_and_ping'
                ]

    def start(self):
        if super().start() is False:
            return False
        return True


def start(case_name, **kwargs):
    v = VerifyDynamicIp(script_name=VerifyDynamicIp.__name__, case_name=case_name)
    v.start()