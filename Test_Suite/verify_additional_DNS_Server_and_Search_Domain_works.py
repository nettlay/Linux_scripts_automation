import time
from Test_Script.ts_common.common import CaseFlowControl, run_command
from Common.exception import CaseRunningError, PicNotFoundError
from Test_Script.ts_network.network import Network, EasyRDP
from Common.log import log
from Common.common_function import SwitchThinProMode, reboot_command


class VerifyAdditionalDNS(CaseFlowControl):
    format_dns_server = "15.83.244.81"
    format_search_domains = "tcqa.hp"
    format_rdp_server = "auto-update.tcqa.hp"
    format_user = "testadmin"
    format_password = "Shanghai2010"
    format_domain = "tcqa"

    def __init__(self, script_name, case_name, exception=(CaseRunningError, )):
        super().__init__(script_name=script_name, case_name=case_name, exception=exception)
        self.network = Network.create_object()
        self.rdp = EasyRDP.create_object()

    def set_dns(self):
        """
        Index: 0
        """
        self.set_callback_success(['reboot'])
        self.set_callback_fail(['close_network_panel_callback'])

        SwitchThinProMode("admin")
        self.network.close()
        self.network.open()
        self.network.dns.click()
        self.network.dns_server.send_keys(self.format_dns_server)
        self.network.search_domains.send_keys(self.format_search_domains)
        self.network.apply.click()
        self.network.close()
        self.create_list_index_file_and_suspend(index=1)

    def check_dns_info_after_reboot(self):
        """
        Index: 1
        """
        domains = run_command("mclient --quiet get root/Network/SearchDomains").strip()
        servers = run_command("mclient --quiet get root/Network/DNSServers").strip()
        if domains != self.format_search_domains:
            raise CaseRunningError(f"Chcek SearchDomains Fail! Expect: {self.format_search_domains} Actual: {domains}")
        if servers != self.format_dns_server:
            raise CaseRunningError(f"Chcek DNSServers Fail! Expect: {self.format_dns_server} Actual: {servers}")

    def logon_rdp_and_check_logon(self):
        """
        Index: 2
        """
        SwitchThinProMode("admin")

        self.set_callback_success(['close_rdp_callback',
                                   'restore_dns_callback',
                                   'end_and_reboot'])
        self.set_callback_fail(['close_rdp_callback',
                                'restore_dns_callback'])
        default_settings = {"credentialsType": "password",
                            "domain": 'tcqa',
                            'tlsVersion': 'auto',
                            'address': 'auto-update.tcqa.hp',
                            "password": 'Shanghai2010',
                            "username": 'testadmin',
                            "securityLevel": "0",
                            "windowType": "full",
                            }
        self.rdp.add_settings(settings=default_settings)
        self.rdp.logon()
        time.sleep(5)
        self.__wait_until_rdp_logon()

    def __wait_until_rdp_logon(self, time_out=60, interval=5):
        while time_out:
            try:
                if self.rdp.into_rdp:
                    return True
            except PicNotFoundError:
                time_out -= interval
                log.info("Waiting RDP Logon")
                time.sleep(interval)
        raise CaseRunningError(f"VDI Logon Fail VDI_ID {self.rdp.vdi_id}")

    def reboot(self):
        reboot_command()

    def end_and_reboot(self):
        self.end_flow()
        reboot_command()

    def close_network_panel_callback(self):
        self.network.close()

    def close_rdp_callback(self):
        self.rdp.logoff()
        self.rdp.close()

    def restore_dns_callback(self):
        run_command("mclient --quiet set root/Network/SearchDomains '' && "
                    "mclient --quiet set root/Network/DNSServers '' && "
                    "mclient commit")

    def set_method_list(self) -> list:

        return ['set_dns',
                'check_dns_info_after_reboot',
                'logon_rdp_and_check_logon',
                ]

    def start(self):
        if super().start() is False:
            return False
        return True


def start(case_name, **kwargs):
    v = VerifyAdditionalDNS(script_name=VerifyAdditionalDNS.__name__, case_name=case_name)
    v.start()


