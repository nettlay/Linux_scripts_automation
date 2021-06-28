# Author: nick.lu
# Time: 2020-4-1
# Function: use verify indo regulation working well after dash indo image

from time import sleep
from Test_Script.ts_precheck import network_function as nf, precheck_function as cfn
from Test_Script.ts_precheck import thinpro_system_function as tsf
# from Common.log import log
from Common import common_function
from Common.tool import get_root_path
from Common.common_function import *

# log = log.log


def start(case_name, **kwargs):
    cfn.SwitchThinProMode(switch_to="admin")
    log.info("-" * 60)
    log.info("case name:" + case_name)
    # report_file = nf.system_ip() + '.yaml'
    # ip = common_function.check_ip_yaml()
    # report_file = get_root_path("Test_Report/{}.yaml".format(ip))
    base_name = get_report_base_name()
    report_file = get_current_dir('Test_Report', base_name)
    common_function.new_cases_result(report_file, case_name)  # new report
    sleep(0.2)

    build_id = tsf.sys_build_id()
    if build_id == "AR6":
        log.info("this is a indonesia image")
    else:
        steps = {'step_name': 'Check current os',
                     'result': 'Fail',
                     'expect': 'Current os is indo',
                     'actual': 'current os is not indonesia. Build id: {}'.format(build_id),
                     'note': 'null'}
        common_function.update_cases_result(report_file, case_name, steps)
        # log.error("this not is a indonesia image, can't run this case")
        log.info("Build id : {}, this not is an indonesia image, skip this case".format(build_id))
        log.info("{:+^70}".format("this case test over"))
        return False

    if not nf.check_wireless_card():    # check if there is a wireless card
        pre_check = {'step_name': 'check_wireless_card',
                 'result': 'Fail',
                 'expect': 'have wireless card',
                 'actual': 'not found the wireless card',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, pre_check)
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    if not nf.indo_wireless_channels_5g_check():
        step = {'step_name': 'indo_wireless_channels_5g_check',
                 'result': 'Fail',
                 'expect': 'channel 149, 153, 157, 161 is enable, and channel 165 is disabled',
                 'actual': 'indonesia wireless channel disable not correct',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False
    else:
        step = {'step_name': 'indo_wireless_channels_5g_check',
                 'result': 'pass',
                 'expect': 'channel 149, 153, 157, 161 is enable, and channel 165 is disabled',
                 'actual': 'channel 149, 153, 157, 161 is enable, and channel 165 is disabled',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)

    if not nf.scan_wireless(SSID="R1-Linux-roaming"):
        step = {'step_name': 'scan_wireless R1-Linux-roaming',
                 'result': 'Fail',
                 'expect': 'found the R1-Linux-roaming in environment',
                 'actual': 'not found the R1-Linux-roaming in environment',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    nf.del_wireless_profile_from_reg()

    # if nf.check_eth0_connect():  # check if the wired network is connected
    #     nf.disable_eth0()  # disable eth0
    #     sleep(5)

    # Set WiredWirelessSwitch value to 0 in registry to ensure eth0 and wlan0 to connect at same time.
    nf.wired_wireless_switch('off')
    sleep(1)

    if not nf.connect_wireless_wpa2_psk(ssid="R1-Linux-roaming"):  # check if connect R1_Linux_153
        nf.del_wireless_profile_from_reg()
        # nf.enable_eth0()
        # Restore WiredWirelessSwitch value to default 1 in registry
        nf.wired_wireless_switch('on')
        step = {'step_name': 'connect wireless R1-Linux-roaming',
                 'result': 'Fail',
                 'expect': 'connect ap R1-Linux-roaming success',
                 'actual': 'connect ap R1-Linux-roaming fail',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)
        log.error("connect ap R1-Linux-roaming fail")
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    # sleep(30)  # wait connect wireless

    if nf.now_connected_wireless() == "R1-Linux-roaming":
        log.info("connect R1-Linux-roaming success")
        step = {'step_name': 'check connected wireless R1-Linux-roaming',
                 'result': 'pass',
                 'expect': 'connect ap R1-Linux-roaming success',
                 'actual': 'connect ap R1-Linux-roaming success',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)
    else:
        step = {'step_name': 'check connected wireless R1-Linux-roaming',
                 'result': 'Fail',
                 'expect': 'connect ap R1-Linux-roaming success',
                 'actual': 'connect ap R1-Linux-roaming fail',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)

        nf.del_wireless_profile_from_reg()
        sleep(7)
        # nf.enable_eth0()
        # Restore WiredWirelessSwitch value to default 1 in registry
        nf.wired_wireless_switch('on')
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    if not nf.scan_wireless(SSID="R1-TC_5G_n"):
        step = {'step_name': 'scan_wireless R1-TC_5G_n',
                 'result': 'Fail',
                 'expect': 'found the R1-TC_5G_n in environment',
                 'actual': 'not found the R1-TC_5G_n in environment',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)
        # Restore WiredWirelessSwitch value to default 1 in registry
        nf.wired_wireless_switch('on')
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    # if nf.check_eth0_connect():  # check if the wired network is connected
    #     nf.disable_eth0()  # disable eth0
    #     sleep(5)

    nf.del_wireless_profile_from_reg()
    sleep(8)

    if not nf.connect_wireless_wpa2_psk(ssid='R1-TC_5G_n', password=''):  # check if connect R1_TC_5G_n
        # nf.enable_eth0()
        # Restore WiredWirelessSwitch value to default 1 in registry
        nf.wired_wireless_switch('on')
        step = {'step_name': 'connect wireless R1-TC_5G_n',
                 'result': 'Fail',
                 'expect': 'connect ap R1_TC_5G_n success',
                 'actual': 'connect ap R1_TC_5G_n fail',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)
        log.error("connect ap R1_TC_5G_n fail")
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    # sleep(30)  # wait connect wireless

    if nf.now_connected_wireless() == "R1-TC_5G_n":

        step = {'step_name': 'check connected wireless R1-TC_5G_n',
                 'result': 'pass',
                 'expect': 'connect ap R1_TC_5G_n success',
                 'actual': 'connect ap R1_TC_5G_n success',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)

    else:
        step = {'step_name': 'check connected wireless R1-TC_5G_n',
                 'result': 'fail',
                 'expect': 'connect ap R1_TC_5G_n success',
                 'actual': 'connect ap R1_TC_5G_n fail',
                 'note': 'null'}
        common_function.update_cases_result(report_file, case_name, step)

        log.error("connect ap R1_TC_5G_n fail")

        nf.del_wireless_profile_from_reg()
        sleep(7)
        # nf.enable_eth0()
        # Restore WiredWirelessSwitch value to default 1 in registry
        nf.wired_wireless_switch('on')
        log.info("{:+^70}".format("this case test over"))
        sleep(1)
        return False

    nf.del_wireless_profile_from_reg()
    sleep(7)
    # nf.enable_eth0()
    # Restore WiredWirelessSwitch value to default 1 in registry
    nf.wired_wireless_switch('on')
    log.info("{:+^70}".format("this case test over"))
    sleep(1)
    return True


