# case name: check connectivity with the SSID R1-TC_2.4G_n_WPA2P
# Author: nick.lu
import pyautogui
import traceback
from Common.log import *
from Common import common_function as cf
from Test_Script.ts_network import network_setting, network
from Common.picture_operator import wait_element


def connect_wireless(ssid):
    try:
        log.info("start connect wireless {}".format(ssid))
        wireless = network_setting.Wireless()
        wireless.open_network()
        wireless.switch_to_wireless_tab()
        wireless.add(ssid=ssid)
        wireless.apply_and_ok()
        wireless.apply()
        wireless.close_control_panel()
        return True
    except:
        log.error(traceback.format_exc())
        return False


def stop_network():
    log.info("stop network from network systray icon")
    nw = wait_element(cf.get_current_dir("Test_Data/td_network/wired/_wired_connect_systray"))
    if not nw:
        log.error("not found network systray icon")
        return False
    pyautogui.click(nw[0])
    stop = wait_element(cf.get_current_dir("Test_Data/td_network/wired/_systray_stop"))
    if not stop:
        log.error("not found network systray stop icon")
        return False
    pyautogui.click(stop[0])
    time.sleep(5)
    wireless = network_setting.Wireless()
    if wireless.check_wireless_connected():
        log.error("stop network fail")
        return False
    log.info("stop network success")
    return True


def start_network():
    log.info("start network from network systray icon")
    nw = wait_element(cf.get_current_dir("Test_Data/td_network/wired/_wired_disconnect_systray"))
    if not nw:
        log.error("not found network systray icon")
        return False
    pyautogui.click(nw[0])
    stop = wait_element(cf.get_current_dir("Test_Data/td_network/wired/_systray_start"))
    if not stop:
        log.error("not found network systray stop icon")
        return False
    pyautogui.click(stop[0])
    wireless = network_setting.Wireless()
    for i in range(20):
        log.info("wait network connect...")
        time.sleep(5)
        if wireless.check_wireless_connected():
            log.info("network connected success")
            return True
    log.error("network connected fail")
    return False


def restart_network():
    log.info("restart network from network systray icon")
    nw = wait_element(cf.get_current_dir("Test_Data/td_network/wired/_wired_connect_systray"))
    if not nw:
        log.error("not found network systray icon")
        return False
    pyautogui.click(nw[0])
    stop = wait_element(cf.get_current_dir("Test_Data/td_network/wired/_systray_restart"))
    if not stop:
        log.error("not found network systray stop icon")
        return False
    pyautogui.click(stop[0])
    wireless = network_setting.Wireless()
    for i in range(20):
        log.info("wait network disconnect...")
        time.sleep(2)
        if not wireless.check_wireless_connected():
            log.info("network disconnected")
            break
    else:
        log.error("network disconnect fail")
        return False
    for i in range(40):
        log.info("wait network connect...")
        time.sleep(3)
        if wireless.check_wireless_connected():
            log.info("network connected success")
            log.info("restart network from network systray icon success")
            return True
    log.error("network connected fail")
    log.error("restart network from network systray icon fail")
    return False


def start(case_name, **kwargs):
    ssid = kwargs.get("ssid", "R1-TC_2.4G_n_WPA2P")
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)

    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)

    wireless = network_setting.Wireless()
    if not wireless.check_wireless_card():
        log.error("not found the wireless card on thin client")
        report = {'step_name': 'check wireless card',
                  'result': 'fail',
                  'expect': "thin client has wireless card",
                  'actual': "not found wireless card on thin client",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        log.error("{:+^80}".format("test case fail"))
        return False

    cf.SwitchThinProMode("admin")
    wireless.close_control_panel()
    wired = network_setting.Wired()
    if wired.check_wired_is_connected():
        wired.set_wired_and_wireless_simultaneously()
        wired.disable_eth0()

    wireless.del_wireless_profile_from_reg()

    if not connect_wireless(ssid=ssid):  # connect wireless
        log.error("add wireless {} profile fail".format(ssid))
        wireless.close_control_panel()
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        if not wired.check_wired_is_connected():
            wired.enable_eth0()
            log.info("wait connect wired")
            time.sleep(10)
        report = {'step_name': 'add wireless ' + ssid + ' profile fail',
                  'result': 'fail',
                  'expect': "connect wireless success",
                  'actual': "connect wireless fail, time out",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        return False

    for i in range(24):
        log.info("wait connect wireless...")
        time.sleep(5)
        if wireless.check_wireless_connected():
            log.info("wireless connect success")
            break
    else:
        log.error("connect wireless time out")
        report = {'step_name': 'connect wireless',
                  'result': 'fail',
                  'expect': "connect wireless success",
                  'actual': "connect wireless fail, time out",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        log.error("{:+^80}".format("test case fail"))
        return False
    report = {'step_name': 'connect wireless',
              'result': 'Pass',
              'expect': "connect wireless success",
              'actual': "connect wireless success",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)

    if not network.ping_server(ip="15.83.240.98"):  # ping 15.83.240.98
        report = {'step_name': 'ping "15.83.240.98"',
                  'result': 'fail',
                  'expect': "ping server success",
                  'actual': "ping server fail",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        log.error("{:+^80}".format("test case fail"))
        return False
    report = {'step_name': 'ping "15.83.240.98"',
              'result': 'pass',
              'expect': "ping server success",
              'actual': "ping server success",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)

    log.info("set 'root/Network/disableLeftClickMenu' is 0")
    os.system("mclient --quiet set root/Network/disableLeftClickMenu 0")
    os.system("mclient commit")
    time.sleep(1)

    if not stop_network():                                                  # stop network
        report = {'step_name': 'stop network',
                  'result': 'fail',
                  'expect': "stop network from network systray icon success",
                  'actual': "stop network from network systray icon fail",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        os.system("mclient --quiet set root/Network/disableLeftClickMenu 1")
        os.system("mclient commit")
        log.error("{:+^80}".format("test case fail"))
        return False
    report = {'step_name': 'stop network',
              'result': 'pass',
              'expect': "stop network from network systray icon success",
              'actual': "stop network from network systray icon success",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)

    if not start_network():  # start network
        report = {'step_name': 'start network',
                  'result': 'fail',
                  'expect': "start network from network systray icon success",
                  'actual': "start network from network systray icon fail",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        os.system("mclient --quiet set root/Network/disableLeftClickMenu 1")
        os.system("mclient commit")
        log.error("{:+^80}".format("test case fail"))
        return False
    report = {'step_name': 'start network',
              'result': 'pass',
              'expect': "start network from network systray icon success",
              'actual': "start network from network systray icon success",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)

    if not restart_network():  # start network
        report = {'step_name': 'restart network',
                  'result': 'fail',
                  'expect': "restart network from network systray icon success",
                  'actual': "restart network from network systray icon fail",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        os.system("mclient --quiet set root/Network/disableLeftClickMenu 1")
        os.system("mclient commit")
        log.error("{:+^80}".format("test case fail"))
        return False
    report = {'step_name': 'restart network',
              'result': 'pass',
              'expect': "restart network from network systray icon success",
              'actual': "restart network from network systray icon success",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)

    log.info("start delete the wireless profile")
    wireless.del_wireless_profile_from_reg()
    log.info("wait wireless disconnect")
    time.sleep(10)
    if wireless.check_wireless_connected():
        log.error("wireless connected")
        report = {'step_name': 'check wireless status',
                  'result': 'fail',
                  'expect': "wireless is disconnect after delete wireless profile",
                  'actual': "wireless is connect after delete wireless profile",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wired.set_wired_connection_priority()
        os.system("mclient --quiet set root/Network/disableLeftClickMenu 1")
        os.system("mclient commit")
        log.error("{:+^80}".format("test case fail"))
        return False
    report = {'step_name': 'check wireless status',
              'result': 'pass',
              'expect': "wireless is disconnect after delete wireless profile",
              'actual': "wireless is disconnect after delete wireless profile",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)
    wired.set_wired_connection_priority()
    os.system("mclient --quiet set root/Network/disableLeftClickMenu 1")
    os.system("mclient commit")
    if not wired.check_wired_is_connected():
        log.info("wired is not connected")
        wired.enable_eth0()
        time.sleep(20)
    log.info("{:+^80}".format("test case pass"))
    return True
