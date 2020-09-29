# case_name: check_ethernet_link_speed_when_both_client_and_switch_set_to_auto
# nick.lu

import subprocess
import traceback
import pyautogui
from Common.log import *
from Common import common_function as cf
from Test_Script.ts_network import network_setting


def pre_check():
    wired = network_setting.Wired()
    wired_state = wired.check_wired_is_connected()
    if not wired_state:
        log.error("thinpro wired is not connected")
        del wired
        return False
    else:
        del wired
        return True


def set_eth0_speed(ethernet_speed):
    try:
        cf.SwitchThinProMode("admin")
        wired = network_setting.Wired()
        wired.open_network_wired_dialog()
        wired.set_ethernet_speed(speed=ethernet_speed)
        wired.apply()
        log.info("close control panel")
        wired.close_control_panel()
        time.sleep(1)
        s = subprocess.getoutput("mclient --quiet get root/Network/Wired/EthernetSpeed")
        if s == ethernet_speed:
            log.info("set 'Ethernet Speed' is '{}' success".format(ethernet_speed))
            return True
        else:
            log.error("set 'Ethernet Speed' is '{}' fail".format(ethernet_speed))
            return False
    except:
        log.error(traceback.format_exc())
        pyautogui.screenshot(cf.get_current_dir("Test_Report/check_speed_{}.png".format(ethernet_speed)))
        return False


def get_eth0_speed():
    """
    :return: {'speed': '1000Mb/s', 'duplex': 'Full', 'auto-negotiation': 'on'}
    """
    speed = dict()
    s = subprocess.getoutput("ethtool eth0 | grep Speed").split(":")[1].strip()
    duplex = subprocess.getoutput("ethtool eth0 | grep Duplex").split(":")[1].strip()
    auto_negotiation = subprocess.getoutput("ethtool eth0 | grep Auto-negotiation").split(":")[1].strip()
    speed["speed"] = s
    speed["duplex"] = duplex
    speed["auto-negotiation"] = auto_negotiation
    return speed


def reset_test_environment():
    log.info("start reset test environment")
    wired = network_setting.Wired()
    os.system("mclient --quiet set root/Network/Wired/EthernetSpeed 'Automatic'")
    os.system("mclient commit")
    wired.disable_eth0()
    time.sleep(2)
    wired.enable_eth0()
    for i in range(12):
        log.info("wait wired reconnect...")
        time.sleep(5)
        if wired.check_wired_is_connected():
            log.info("wired is connected")
            break
    del wired


def start(case_name, **kwargs):
    ethernet_speed = kwargs.get("ethernet_speed", "Automatic")
    speed = kwargs.get("speed", "1000Mb/s")
    duplex = kwargs.get("duplex", "Full")
    auto_negotiation = kwargs.get("auto_negotiation", "on")

    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)

    if not pre_check():
        pre_check_report = {'step_name': 'pre_check',
                            'result': 'Fail',
                            'expect': 'ThinPro connected wired',
                            'actual': 'ThinPro not connected wired',
                            'note': ''}
        cf.update_cases_result(report_file, case_name, pre_check_report)
        log.error("{:+^80}".format("test case fail"))
        return False
    wired = network_setting.Wired()
    if not set_eth0_speed(ethernet_speed=ethernet_speed):              # set Ethernet Speed
        set_speed_report = {'step_name': 'set eth0 speed',
                            'result': 'Fail',
                            'expect': "set 'Ethernet Speed' success",
                            'actual': "set 'Ethernet Speed' fail",
                            'note': ''}
        cf.update_cases_result(report_file, case_name, set_speed_report)
        wired.close_control_panel()
        reset_test_environment()
        log.error("{:+^80}".format("test case fail"))
        return False

    for i in range(24):
        log.info("wait wired reconnect...")
        time.sleep(5)
        if wired.check_wired_is_connected():
            log.info("wired is connected")
            break
    else:
        log.error("reconnect wired time out 2 minutes")
        reconnect_wired_report = {'step_name': 'reconnect wired',
                                  'result': 'Fail',
                                  'expect': "reconnect wired success",
                                  'actual': "reconnect wired time out 2 minutes",
                                  'note': ''}
        cf.update_cases_result(report_file, case_name, reconnect_wired_report)
        reset_test_environment()
        log.error("{:+^80}".format("test case fail"))
        return False

    eth0_speed = get_eth0_speed()
    if eth0_speed["speed"] == speed and eth0_speed["duplex"] == duplex and \
            eth0_speed["auto-negotiation"] == auto_negotiation:
        log.info("eth0 speed is '{}'".format(eth0_speed["speed"]))
        log.info("eth0 duplex is '{}'".format(eth0_speed["duplex"]))
        log.info("eth0 auto-negotiation is '{}'".format(eth0_speed["auto-negotiation"]))
    else:
        log.error("eth0 speed is '{}'".format(eth0_speed["speed"]))
        log.error("eth0 duplex is '{}'".format(eth0_speed["duplex"]))
        log.error("eth0 auto-negotiation is '{}'".format(eth0_speed["auto-negotiation"]))
        check_speed_report = {'step_name': 'check eth0 speed',
                              'result': 'Fail',
                              'expect': "eth0 speed is '{}', '{}', '{}'".format(speed, duplex, auto_negotiation),
                              'actual': "eth0 speed is '{speed}', '{duplex}', '{auto-negotiation}'".format_map(eth0_speed),
                              'note': ''}
        cf.update_cases_result(report_file, case_name, check_speed_report)
        reset_test_environment()
        log.error("{:+^80}".format("test case fail"))
        return False

    reset_test_environment()
    check_speed_report = {'step_name': 'check eth0 speed',
                          'result': 'Pass',
                          'expect': "eth0 speed is '{}', '{}', '{}'".format(speed, duplex, auto_negotiation),
                          'actual': "eth0 speed is '{speed}', '{duplex}', '{auto-negotiation}'".format_map(eth0_speed),
                          'note': ''}
    cf.update_cases_result(report_file, case_name, check_speed_report)
    del wired
    log.info("{:+^80}".format("test case pass"))
    return True

