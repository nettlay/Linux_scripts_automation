import time
from Test_Script.ts_common.common import CaseFlowControl, run_command, create_count, read_count
from Common.exception import CaseRunningError
from Common.common_function import get_current_dir, reboot_command, SwitchThinProMode
from Test_Script.ts_network.network import Network, Usb, StaticIpUtils
from Common.file_operator import YamlOperator


class VerifyUserLockKey(CaseFlowControl):

    def __init__(self, script_name, case_name, exception=(CaseRunningError, )):
        super().__init__(script_name=script_name, case_name=case_name, exception=exception)
        self.temp_yaml = get_current_dir('Test_Report/wired_temp.yaml')
        self.usb_fail_count_file = get_current_dir('Test_Report/count_temp.txt')
        self.network = Network.create_object()
        self.usb = Usb.create_object()
        self.__usb_fail_max_count = 10

    def __save_temp_data(self, **data):
        yaml_obj = YamlOperator(self.temp_yaml)
        yaml_obj.write(data)

    def __read_temp_data(self):
        return YamlOperator(self.temp_yaml).read()

    def __check_data(self, data_source, **data):
        for key, actual_value in data.items():
            except_value = data_source.get(key, "")
            if actual_value != except_value:
                raise CaseRunningError(f"Check {key} Status Fail! Expect: {except_value} Actual: {actual_value}")

    def set_wired(self):
        """
        Index: 0
        """
        info = StaticIpUtils.read_info_from_yaml()
        format_connection_method = "Static"
        format_ip = info["ip"]
        format_mask = info["mask"]
        format_gateway = info["gateway"]
        hostname = f'HP{"".join(format_ip.split("."))}'

        self.set_callback_fail(['set_wired_callback_fail',
                                'restore_automatic_callback'])
        SwitchThinProMode("admin")

        self.network.close()
        self.network.open()
        self.network.connection_method.click()
        self.network.static.click()
        self.network.ip_address.send_keys(format_ip)
        self.network.mask.send_keys(format_mask)
        self.network.gateway.send_keys(format_gateway)
        self.network.dns.click()
        self.network.hostname.send_keys(hostname)
        self.network.apply.click()
        self.network.close()
        self.__save_temp_data(method=format_connection_method,
                              ip=format_ip,
                              mask=format_mask,
                              gateway=format_gateway,
                              hostname=hostname)

    def set_profile_to_1(self):
        """
        Index: 1
        """
        profile_name = "SetTo1.xml"
        self.set_callback_fail(['set_profile_callback_fail',
                                'restore_automatic_callback'])

        SwitchThinProMode("admin")
        if not self.usb.install(profile_name):
            current_count = read_count(self.usb_fail_count_file)
            if current_count > self.__usb_fail_max_count:
                raise CaseRunningError(f"USB Workaround Fail Times > {self.__usb_fail_max_count}")
            create_count(self.usb_fail_count_file, current_count+1)
            self.create_list_index_file_and_suspend(index=1)
            reboot_command()
        self.create_list_index_file_and_suspend(index=2)
        self.usb.restore_config.click()
        time.sleep(30)
        raise CaseRunningError("Restore Configuration has been click, but UUT not reboot!")

    def set_wired_callback_fail(self):
        self.network.close()

    def restore_automatic_callback(self):
        Network.set_connection_mode_automatic_with_command()

    def set_profile_callback_fail(self):
        self.usb.close()

    def end_and_reboot(self):
        self.end_flow()
        reboot_command()

    def check_set_profile_to_1(self):
        """
        Index: 2
        """
        self.set_callback_fail(['restore_automatic_callback', 'end_and_reboot'])

        method = run_command("mclient --quiet get root/Network/Wired/Method").strip()
        ip = run_command("mclient --quiet get root/Network/Wired/IPAddress").strip()
        gateway = run_command("mclient --quiet get root/Network/Wired/DefaultGateway").strip()
        mask = run_command("mclient --quiet get root/Network/Wired/SubnetMask").strip()
        hostname = run_command("mclient --quiet get root/Network/Hostname").strip()
        data_source = self.__read_temp_data()
        self.__check_data(method=method,
                          ip=ip,
                          mask=mask,
                          gateway=gateway,
                          hostname=hostname,
                          data_source=data_source)

    def set_profile_to_0(self):
        """
        Index: 3
        """
        profile_name = "SetTo0.xml"
        self.set_callback_fail(['set_profile_callback_fail',
                                'restore_automatic_callback',
                                'end_and_reboot'])

        SwitchThinProMode("admin")
        if not self.usb.install(profile_name):
            current_count = read_count(self.usb_fail_count_file)
            if current_count > self.__usb_fail_max_count:
                raise CaseRunningError(f"USB Workaround Fail Times > {self.__usb_fail_max_count}")
            create_count(self.usb_fail_count_file, current_count+1)
            self.create_list_index_file_and_suspend(index=3)
            reboot_command()
        self.create_list_index_file_and_suspend(index=4)
        self.usb.restore_config.click()
        time.sleep(30)
        raise CaseRunningError("Restore Configuration has been click, but UUT not reboot!")

    def check_set_profile_to_0(self):
        """
        Index: 4
        """
        self.set_callback_fail(['restore_automatic_callback', 'end_and_reboot'])

        method = run_command("mclient --quiet get root/Network/Wired/Method").strip()
        ip = run_command("mclient --quiet get root/Network/Wired/IPAddress").strip()
        gateway = run_command("mclient --quiet get root/Network/Wired/DefaultGateway").strip()
        mask = run_command("mclient --quiet get root/Network/Wired/SubnetMask").strip()
        hostname = run_command("mclient --quiet get root/Network/Hostname").strip()
        data_source = {'method': 'Automatic',
                       'hostname': 'SetTo0'
                       }
        self.__check_data(method=method,
                          ip=ip,
                          mask=mask,
                          gateway=gateway,
                          hostname=hostname,
                          data_source=data_source)

    def set_method_list(self) -> list:
        return [
            'set_wired',
            'set_profile_to_1',
            'check_set_profile_to_1',
            'set_profile_to_0',
            'check_set_profile_to_0',
            ]

    def start(self):
        if super().start() is False:
            return False
        return True


def start(case_name, **kwargs):
    v = VerifyUserLockKey(script_name=VerifyUserLockKey.__name__, case_name=case_name)
    v.start()