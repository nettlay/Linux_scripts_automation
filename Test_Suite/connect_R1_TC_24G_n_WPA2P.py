# Author: nick.lu
# Time: 2020-3-20
# Function: use thinpro or smart zero connect R1-TC-2.4G_n_WPA2P wireless


from time import sleep
from Test_Script.ts_precheck import network_function as nf, precheck_function as cfn
from Common import common_function
from Common.tool import get_root_path

log = common_function.log


def start(case_name, **kwargs):
    cfn.SwitchThinProMode(switch_to="admin")
    log.info("-"*60)
    log.info("case name:" + case_name)
    # report_file = nf.system_ip() + '.yaml'
    ip = common_function.check_ip_yaml()
    report_file = get_root_path("Test_Report/{}.yaml".format(ip))
    common_function.new_cases_result(report_file, case_name)  # new report

    if not nf.check_wireless_card():    # check if there is a wireless card
        step1 = {'step_name': 'step1',
                 'result': 'Fail',
                 'expect': 'have wireless card',
                 'actual': 'it has no wireless card',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step1)
        log.info("{:+^70}".format("this case test over"))
        # return False
        return True

    if not nf.scan_wireless(SSID="R1-TC_2.4G_n_WPA2P"):
        step2 = {'step_name': 'step2',
                 'result': 'Fail',
                 'expect': 'found the R1-TC_2.4G_n_WPA2P in environment',
                 'actual': 'not found the R1-TC_2.4G_n_WPA2P in environment. ',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step2)
        log.info("{:+^70}".format("this case test over"))
        # sleep(1)
        return False

    nf.del_wireless_profile_from_reg()

    # if nf.check_eth0_connect():  # check if the wired network is connected
    #     nf.disable_eth0()  # disable eth0
    #     sleep(5)

    # Set WiredWirelessSwitch value to 0 in registry to ensure eth0 and wlan0 to connect at same time.
    nf.wired_wireless_switch('off')
    sleep(1)

    if not nf.connect_wireless_wpa2_psk(ssid="R1-TC_2.4G_n_WPA2P"):  # configure R1_TC_24G_n_WPA2P in Control Panel
        log.info("configure ap R1_TC_24G_n_WPA2P in Control Panel fail")
        nf.del_wireless_profile_from_reg()
        # nf.enable_eth0()

        step3 = {'step_name': 'step3',
                 'result': 'Fail',
                 'expect': 'configure ap R1_TC_24G_n_WPA2P in Control Panel success',
                 'actual': 'configure ap R1_TC_24G_n_WPA2P in Control Panel fail',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step3)
        log.info("{:+^70}".format("this case test over"))
        # sleep(1)
        return False

    # sleep(30)
    conn_result = nf.now_connected_wireless()
    if conn_result == "R1-TC_2.4G_n_WPA2P":
        log.info('connect wireless R1-TC_2.4G_n_WPA2P success')
        step4 = {'step_name': 'step4',
                 'result': 'pass',
                 'expect': 'connect ap R1_TC_24G_n_WPA2P success',
                 'actual': 'connect ap R1_TC_24G_n_WPA2P success',
                 'note': 'null'}
    else:
        log.error("connect ap R1_TC_24G_n_WPA2P fail")
        step4 = {'step_name': 'step4',
                 'result': 'Fail',
                 'expect': 'connect ap R1_TC_24G_n_WPA2P success',
                 'actual': 'connect ap R1_TC_24G_n_WPA2P fail',
                 'note': 'null'}
    common_function.update_cases_result(report_file, case_name, step4)

    nf.del_wireless_profile_from_reg()
    sleep(7)
    # nf.enable_eth0()

    # Restore WiredWirelessSwitch value to default 1 in registry
    nf.wired_wireless_switch('on')
    log.info("{:+^70}".format("this case test over"))

