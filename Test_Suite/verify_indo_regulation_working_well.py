# Author: nick.lu
# Time: 2020-4-1
# Function: use verify indo regulation working well after dash indo image

from time import sleep
from Test_Script.ts_precheck import network_function as nf, precheck_function as cfn
from Test_Script.ts_precheck import thinpro_system_function as tsf
from Common import log, common_function
from Common.tool import get_root_path

log = log.log


def start(case_name, **kwargs):
    cfn.SwitchThinProMode(switch_to="admin")
    log.info("-" * 60)
    log.info("case name:" + case_name)
    # report_file = nf.system_ip() + '.yaml'
    ip = common_function.check_ip_yaml()
    report_file = get_root_path("Test_Report/{}.yaml".format(ip))
    common_function.new_cases_result(report_file, case_name)  # new report
    sleep(0.2)

    if tsf.sys_build_id() == "AR6":
        log.info("this is a indonesia image")

        if not nf.check_wireless_card():    # check if there is a wireless card
            pre_check = {'step_name': 'pre_check',
                     'result': 'Fail',
                     'expect': 'have wireless card',
                     'actual': 'not found the wireless card',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, pre_check)
            log.info("{:+^70}".format("this case test over"))
            sleep(1)
            return False

        if not nf.check_indo_wireless_channal_disable():
            step3 = {'step_name': 'step3',
                     'result': 'Fail',
                     'expect': 'channel 149, 153, 157, 161 is enable, and channel 165 is disabled',
                     'actual': 'indonesia wireless channel disable not correct',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step3)
            log.info("{:+^70}".format("this case test over"))
            sleep(1)
            return False
        else:
            step3 = {'step_name': 'step3',
                     'result': 'pass',
                     'expect': 'channel 149, 153, 157, 161 is enable, and channel 165 is disabled',
                     'actual': 'channel 149, 153, 157, 161 is enable, and channel 165 is disabled',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step3)

        if not nf.scan_wireless(SSID="R1-Linux-roaming"):
            step4 = {'step_name': 'step1',
                     'result': 'Fail',
                     'expect': 'found the R1-Linux-roaming in environment',
                     'actual': 'not can found the R1-Linux-roaming in environment, '
                               'or the R1-Linux-roaming is weak signal',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step4)
            log.info("{:+^70}".format("this case test over"))
            sleep(1)
            return False

        nf.del_wireless_profile_from_reg()

        if nf.check_eth0_connect():  # check if the wired network is connected
            nf.disable_eth0()  # disable eth0
            sleep(5)

        if not nf.connect_wireless_wpa2_psk_5g_band(ssid="R1-Linux-roaming"):  # check if connect R1_Linux_153
            nf.del_wireless_profile_from_reg()
            nf.enable_eth0()
            step4 = {'step_name': 'step4',
                     'result': 'Fail',
                     'expect': 'connect ap R1-Linux-roaming success',
                     'actual': 'connect ap R1-Linux-roaming fail',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step4)
            log.error("connect ap R1-Linux-roaming fail")
            log.info("{:+^70}".format("this case test over"))
            sleep(1)
            return False

        sleep(30)  # wait connect wireless

        if nf.now_connected_wireless() == "R1-Linux-roaming":
            log.info("connect R1-Linux-roaming success")

            step4 = {'step_name': 'step4',
                     'result': 'pass',
                     'expect': 'connect ap R1-Linux-roaming success',
                     'actual': 'connect ap R1-Linux-roaming success',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step4)
        else:
            step4 = {'step_name': 'step4',
                     'result': 'Fail',
                     'expect': 'connect ap R1-Linux-roaming success',
                     'actual': 'connect ap R1-Linux-roaming fail',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step4)

            nf.del_wireless_profile_from_reg()
            sleep(7)
            nf.enable_eth0()
            log.info("{:+^70}".format("this case test over"))
            sleep(1)
            return False

        if not nf.scan_wireless(SSID="R1-TC_5G_n"):
            step4 = {'step_name': 'step1',
                     'result': 'Fail',
                     'expect': 'found the R1-TC_5G_n in environment',
                     'actual': 'not can found the R1-TC_5G_n in environment, '
                               'or the R1-TC_5G_n is weak signal',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step4)
            log.info("{:+^70}".format("this case test over"))
            sleep(1)
            return False

        if nf.check_eth0_connect():  # check if the wired network is connected
            nf.disable_eth0()  # disable eth0
            sleep(5)

        nf.del_wireless_profile_from_reg()
        sleep(8)

        if not nf.connect_wireless_R1_TC_5G_n():  # check if connect R1_TC_5G_n
            nf.enable_eth0()

            step4 = {'step_name': 'step4',
                     'result': 'Fail',
                     'expect': 'connect ap R1_TC_5G_n success',
                     'actual': 'connect ap R1_TC_5G_n fail',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step4)
            log.error("connect ap R1_TC_5G_n fail")
            log.info("{:+^70}".format("this case test over"))
            sleep(1)
            return False

        sleep(30)  # wait connect wireless

        if nf.now_connected_wireless() == "R1-TC_5G_n":

            step4 = {'step_name': 'step4',
                     'result': 'pass',
                     'expect': 'connect ap R1_TC_5G_n success',
                     'actual': 'connect ap R1_TC_5G_n success',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step4)

        else:
            step4 = {'step_name': 'step4',
                     'result': 'fail',
                     'expect': 'connect ap R1_TC_5G_n success',
                     'actual': 'connect ap R1_TC_5G_n fail',
                     'note': 'null'}
            common_function.update_cases_result(report_file, case_name, step4)

            log.error("connect ap R1_TC_5G_n fail")

            nf.del_wireless_profile_from_reg()
            sleep(7)
            nf.enable_eth0()
            log.info("{:+^70}".format("this case test over"))
            sleep(1)
            return False

        nf.del_wireless_profile_from_reg()
        sleep(7)
        nf.enable_eth0()
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return True

    else:
        steps = {'step_name': 'Check current os',
                     'result': 'Fail',
                     'expect': 'Current os is indo',
                     'actual': 'current os is not indonesia.',
                     'note': 'null'}
        common_function.update_cases_result(report_file, case_name, steps)
        # log.error("this not is a indonesia image, can't run this case")
        log.info("this not is a indonesia image, skip this case")
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

