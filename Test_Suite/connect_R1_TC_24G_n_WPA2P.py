# Author: nick.lu
# Time: 2020-3-20
# Function: use thinpro or smart zero connect R1-TC-2.4G_n_WPA2P wireless


from time import sleep
from Test_Script.ts_precheck import network_function as nf, precheck_function as cfn
from Common import common_function

log = common_function.log()


def start(case_name, **kwargs):
    cfn.SwitchThinProMode(switch_to="admin")
    log.info("-"*60)
    log.info("case name:" + case_name)
    report_file = nf.system_ip() + '.yaml'
    cfn.new_cases_result(report_file, case_name)  # new report
    sleep(0.2)

    if not nf.check_wireless_card():    # check if there is a wireless card
        step1 = {'step_name': 'step1',
                  'result': 'Fail',
                  'expect': 'have wireless card',
                  'actual': 'not found the wireless card',
                  'note': 'null'}
        cfn.update_cases_result(report_file, case_name, step1)
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    if not nf.scan_wireless(SSID="R1-TC_2.4G_n_WPA2P"):
        step1 = {'step_name': 'step1',
                 'result': 'Fail',
                 'expect': 'found the R1-TC_2.4G_n_WPA2P in environment',
                 'actual': 'not can found the R1-TC_2.4G_n_WPA2P in environment, '
                           'or the R1-TC_2.4G_n_WPA2P is weak signal',
                 'note': 'null'}
        cfn.update_cases_result(report_file, case_name, step1)
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    nf.del_wireless_profile_from_reg()

    if nf.check_eth0_connect():  # check if the wired network is connected
        nf.disable_eth0()  # disable eth0
        sleep(5)

    if not nf.connect_wireless_wpa2_psk(ssid="R1-TC_2.4G_n_WPA2P"):  # check if connect R1_TC_24G_n_WPA2P
        log.info("connect ap R1_TC_24G_n_WPA2P fail")
        nf.del_wireless_profile_from_reg()
        nf.enable_eth0()

        step2 = {'step_name': 'step2',
                 'result': 'Fail',
                 'expect': 'connect ap R1_TC_24G_n_WPA2P success',
                 'actual': 'connect ap R1_TC_24G_n_WPA2P fail',
                 'note': 'null'}
        cfn.update_cases_result(report_file, case_name, step2)
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    sleep(30)

    if nf.now_connected_wireless() == "R1-TC_2.4G_n_WPA2P":
        log.info('connect wireless R1-TC_2.4G_n_WPA2P success')
        step2 = {'step_name': 'step2',
                 'result': 'pass',
                 'expect': 'connect ap R1_TC_24G_n_WPA2P success',
                 'actual': 'connect ap R1_TC_24G_n_WPA2P success',
                 'note': 'null'}
        cfn.update_cases_result(report_file, case_name, step2)

        nf.del_wireless_profile_from_reg()
        sleep(7)
        nf.enable_eth0()
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return True

    else:
        log.error("connect ap R1_TC_24G_n_WPA2P fail")
        step2 = {'step_name': 'step2',
                 'result': 'Fail',
                 'expect': 'connect ap R1_TC_24G_n_WPA2P success',
                 'actual': 'connect ap R1_TC_24G_n_WPA2P fail',
                 'note': 'null'}
        cfn.update_cases_result(report_file, case_name, step2)

        nf.del_wireless_profile_from_reg()
        sleep(7)
        nf.enable_eth0()
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False
