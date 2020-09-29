# case name: 110.Verify_wpa_supplicant_password_encryption_works_with_wireless_network
# nick.lu

import subprocess
from Test_Script.ts_network import network_setting
from Common import common_function as cf
from Common.log import *


def start(case_name, **kwargs):
    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)

    wired = network_setting.Wired()
    wireless = network_setting.Wireless()

    if not wireless.check_wireless_card():                            # check wireless card
        log.error("not found the wireless card on thinpro")
        pre_check_report = {'step_name': 'pre_check',
                            'result': 'Fail',
                            'expect': 'ThinPro has wireless card',
                            'actual': 'not found the wireless card on thin client',
                            'note': ''}
        cf.update_cases_result(report_file, case_name, pre_check_report)
        log.error("{:+^80}".format("test case fail"))
        return False
    wireless.del_wireless_profile_from_reg()
    if wired.check_wired_is_connected():                             # check wired connected
        log.info("wired is connected")
        wired.set_wired_and_wireless_simultaneously()
        wired.disable_eth0()
        time.sleep(3)

    value = subprocess.getoutput("mclient --quiet get root/Network/EncryptWpaConfig")      # step 1-------------
    if int(value) != 1:
        log.error("the default value of 'network/EncryptWpaConfig' not is '1'")
        step_1_report = {'step_name': 'check value of "root/Network/EncryptWpaConfig"',
                            'result': 'Fail',
                            'expect': 'the value of "root/Network/EncryptWpaConfig" is 1',
                            'actual': 'the value of "root/Network/EncryptWpaConfig" not is 1',
                            'note': ''}
        cf.update_cases_result(report_file, case_name, step_1_report)
        wired.set_wired_connection_priority()
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("the default value of 'network/EncryptWpaConfig' is '1'")
    step_1_report = {'step_name': 'check value of "root/Network/EncryptWpaConfig"',
                     'result': 'Pass',
                     'expect': 'the value of "root/Network/EncryptWpaConfig" is 1',
                     'actual': 'the value of "root/Network/EncryptWpaConfig" is 1',
                     'note': ''}
    cf.update_cases_result(report_file, case_name, step_1_report)

    log.info("start connect a wireless ap")                                            # step 2-------------
    cf.SwitchThinProMode("admin")
    wireless.open_network()
    wireless.switch_to_wireless_tab()
    wireless.add(ssid="R1-Linux-disconnect")
    # wireless.add(ssid="R1-TC_5G_n")
    wireless.apply_and_ok()
    wireless.apply()
    wireless.close_control_panel()

    for i in range(12):
        log.info("wait connect wireless...")
        time.sleep(5)
        if wireless.check_wireless_connected():
            log.info("wireless connected success")
            break
    else:
        log.error("connect wireless time out")
        step_2_report = {'step_name': 'connect wireless',
                         'result': 'Fail',
                         'expect': 'connect wireless success',
                         'actual': 'connect wireless fail',
                         'note': ''}
        cf.update_cases_result(report_file, case_name, step_2_report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        if not wired.check_wired_is_connected():
            wired.enable_eth0()
        log.error("{:+^80}".format("test case fail"))
        return False
    step_2_report = {'step_name': 'connect wireless',
                     'result': 'Pass',
                     'expect': 'connect wireless success',
                     'actual': 'connect wireless success',
                     'note': ''}
    cf.update_cases_result(report_file, case_name, step_2_report)

    password = subprocess.getoutput("cat /etc/wpasupplicant.wireless.wlan0.conf")         # step 3 -------------
    if "neoware1234".lower() in password.lower():
        log.error("wireless password not is encryption")
        step_3_report = {'step_name': 'check wireless password profile is encryption',
                         'result': 'Fail',
                         'expect': 'check wireless password profile is encryption',
                         'actual': 'check wireless password profile not is encryption',
                         'note': ''}
        cf.update_cases_result(report_file, case_name, step_3_report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        if not wired.check_wired_is_connected():
            wired.enable_eth0()
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("wireless password is encryption")
    step_3_report = {'step_name': 'check wireless password profile is encryption',
                     'result': 'Pass',
                     'expect': 'check wireless password profile is encryption',
                     'actual': 'check wireless password profile is encryption',
                     'note': ''}
    cf.update_cases_result(report_file, case_name, step_3_report)
    log.info("start reset test environment")
    wireless.del_wireless_profile_from_reg()
    wired.set_wired_connection_priority()
    if not wired.check_wired_is_connected():
        wired.enable_eth0()
    for i in range(20):
        time.sleep(3)
        if wired.check_wired_is_connected():
            break
    log.info("{:+^80}".format("test case pass"))
    return True

