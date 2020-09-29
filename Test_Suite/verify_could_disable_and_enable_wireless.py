# case name: 123.Verify it could disable and enable wireless from Network Manager
# nick.lu
import pyautogui
import subprocess
from Test_Script.ts_network import network_setting
from Common import common_function as cf
from Common.picture_operator import wait_element
from Common.log import *

steps_list = ("disable_wireless", "enable_wireless", "enable_wireless_after_reboot")


def pic(picture_folder):
    return cf.get_current_dir("Test_Data/td_network/wireless/{}".format(picture_folder))


def step_1(**kwargs):
    case_name = kwargs.get("case_name")
    log.info("{:-^80}".format("start a case test"))
    log.info("case name: " + case_name)
    log.info("start prepare the pre_condition")
    wireless = network_setting.Wireless()  # check wireless card
    if not wireless.check_wireless_card():
        log.error("not found wireless card on thin client")
        return [False, "not found wireless card on thin client"]

    wired = network_setting.Wired()
    if wired.check_wired_is_connected():
        log.info("wired is connected")
        wired.set_wired_and_wireless_simultaneously()
        wired.disable_eth0()
        time.sleep(2)

    wireless.del_wireless_profile_from_reg()
    log.info("start connect wireless 'R1-TC_5G_n'")
    cf.SwitchThinProMode("admin")
    wireless.open_network()
    wireless.switch_to_wireless_tab()
    wireless.add(ssid="R1-TC_5G_n")
    wireless.apply_and_ok()
    wireless.apply()
    wireless.close_control_panel()
    for i in range(24):
        log.info("wait connect wireless...")
        time.sleep(5)
        if wireless.check_wireless_connected():
            log.info("wireless has connected")
            break
    else:
        log.error("connect wireless time out")
        wireless.set_wired_connection_priority()
        wired.enable_eth0()
        return [False, "connect wireless time out"]

    log.info("start test case-----------------------------")
    log.info("start disable wireless")
    wireless.open_network()
    wireless.switch_to_wireless_tab()
    wireless.disable_wireless()                             # disable wireless
    wireless.apply()
    add_edit_del = wait_element(pic("_gray_add_edit_del"), rate=0.99)
    if not add_edit_del:
        log.error("add, edit, delete not is gray")
        return [False, "add, edit, delete not is gray"]
    log.info("add, edit, delete is gray")
    wireless.close_control_panel()
    if wireless.check_wireless_connected():
        log.error("wireless is connected")
        return [False, "wireless is connected"]
    log.info("wireless is disconnected")
    if wait_element(pic("_systray_not_connect")):
        log.error("systray wireless icon is exist")
        return [False, "systray wireless icon is exist"]
    wlan0 = subprocess.getoutput("ifconfig | grep -i wlan0")
    if wlan0:
        log.error("found the 'wlan0' use command 'ifconfig'")
        return [False, "found the 'wlan0' use command 'ifconfig'"]
    log.info("systray wireless icon is not exist")
    log.info("start reboot")
    return [True, "step_1 test pass"]
    # os.system("reboot")                                           # reboot
    # time.sleep(60)


def step_2_1():
    log.info("start step-1_2------------------------")
    cf.SwitchThinProMode("admin")
    wireless = network_setting.Wireless()
    log.info("start check whether wireless is connected after reboot")
    if wireless.check_wireless_connected():
        log.error("wireless is connected after reboot")
        return [False, "wireless is connected after reboot"]
    log.info("wireless is disconnected after reboot")

    log.info("start check wireless systray icon")
    if wait_element(pic("_systray_not_connect")):
        log.error("found the wireless systray icon")
        return [False, "found the wireless systray icon"]
    log.info("not found the wireless systray icon")

    log.info("start check add, edit and delete button")
    wireless.open_network()
    wireless.switch_to_wireless_tab()
    if not wait_element(pic("_gray_add_edit_del"), rate=0.99):
        log.error("add, edit and delete button is not gray")
        return [False, "add, edit and delete button is not gray"]
    log.info("add, edit and delete button is gray")
    log.info("start step 2-------------------------")
    wireless.enable_wireless()
    wireless.apply()
    log.info("start check add, edit and delete button")
    if not wait_element(pic("_black_add_gray_edit_del"), rate=0.99):
        log.error("not found the black add and edit delete")
        return [False, "not found the black add and edit delete"]
    log.info("found the black add and edit delete")
    wireless.close_control_panel()

    for i in range(24):
        log.info("wait connect wireless...")
        time.sleep(5)
        if wireless.check_wireless_connected():
            log.info("wireless is connected")
            break
    else:
        log.error("connect wireless time out")
        return [False, "connect wireless time out"]

    if not wait_element(pic("_systray_connect")):
        log.warning("not found the wireless systray icon")
        pyautogui.screenshot(cf.get_current_dir("Test_Report/ssid_disable_and_enable_wireless_error.png"))
        log.info("start check wireless use command and process")
        wlan0 = subprocess.getoutput("ifconfig | grep -i wlan0")
        if not wlan0:
            log.info("not found the 'wlan0' use command 'ifconfig'")
            return [False, "not found the wireless systray icon and the 'wlan0' use command 'ifconfig'"]
        log.info("found the wlan0 use ifconfig")
        network_systray_icon_process = subprocess.getoutput("ps -ef | grep 'hptc-network-mgr-systray'")
        if not network_systray_icon_process:
            log.error("not found the 'hptc-network-mgr-systray' process")
            return [False, "not found the wireless systray icon and 'hptc-network-mgr-systray' process"]
        log.info("found the 'hptc-network-mgr-systray' process")
    log.info("found the wireless systray icon")
    log.info("start reboot")
    return [True, "step 2 success"]
    # os.system("reboot")
    # time.sleep(60)


def step_2_2():
    log.info("start check wireless after reboot")
    cf.SwitchThinProMode("admin")
    wireless = network_setting.Wireless()
    for i in range(24):
        log.info("wait connect wireless...")
        time.sleep(5)
        if wireless.check_wireless_connected():
            log.info("wireless is connected")
            break
    else:
        log.error("connect wireless time out")
        return [False, "connect wireless time out"]

    if not wait_element(pic("_systray_connect")):
        log.error("not found the wireless systray icon")
        pyautogui.screenshot(cf.get_current_dir("Test_Report/ssid_disable_and_enable_wireless_error.png"))
        return [False, "not found the wireless systray icon"]
    log.info("found the wireless systray icon")

    wireless.open_network()
    wireless.switch_to_wireless_tab()
    if not wait_element(pic("_black_add_gray_edit_del"), rate=0.99):
        log.error("not found the black add and edit delete")
        return [False, "not found the black add and edit delete"]
    log.info("found the black add and edit delete")
    wireless.close_control_panel()
    restore()
    # log.info("{:+^80}".format("test case pass"))
    return [True, "success"]


def restore():
    log.info("start restore test environment")
    wireless = network_setting.Wireless()
    wired = network_setting.Wired()
    wireless.close_control_panel()
    wireless.del_wireless_profile_from_reg()
    wireless.set_wired_connection_priority()
    if not wired.check_wired_is_connected():
        wired.enable_eth0()


def disable_wireless(*args, **kwargs):
    report_file = kwargs.get("report_file")
    case_name = kwargs.get("case_name")
    step_1_result = step_1(**kwargs)
    if not step_1_result[0]:
        step_1_report = {'step_name': 'step_1 disable wireless',
                         'result': 'Fail',
                         'expect': "disable wireless success",
                         'actual': "disable wireless fail",
                         'note': '{}'.format(step_1_result[1])}
        cf.update_cases_result(report_file, case_name, step_1_report)
        restore()
        log.error("{:+^80}".format("test case fail"))
        return False
    step_1_report = {'step_name': 'step_1 disable wireless',
                     'result': 'Pass',
                     'expect': "disable wireless success",
                     'actual': "disable wireless success",
                     'note': '{}'.format(step_1_result[1])}
    cf.update_cases_result(report_file, case_name, step_1_report)

    os.system("reboot")
    time.sleep(60)


def enable_wireless(*args, **kwargs):
    report_file = kwargs.get("report_file")
    case_name = kwargs.get("case_name")
    step_2_result = step_2_1()
    if not step_2_result[0]:
        step_2_report = {'step_name': 'step_2 enable wireless',
                         'result': 'Fail',
                         'expect': "enable wireless success",
                         'actual': "enable wireless fail",
                         'note': '{}'.format(step_2_result[1])}
        cf.update_cases_result(report_file, case_name, step_2_report)
        restore()
        log.error("{:+^80}".format("test case fail"))
        return False
    step_2_report = {'step_name': 'step_2 enable wireless',
                     'result': 'Pass',
                     'expect': "enable wireless success",
                     'actual': "enable wireless success",
                     'note': '{}'.format(step_2_result[1])}
    cf.update_cases_result(report_file, case_name, step_2_report)

    os.system("reboot")
    time.sleep(60)


def enable_wireless_after_reboot(**kwargs):
    report_file = kwargs.get("report_file")
    case_name = kwargs.get("case_name")
    after_reboot_result = step_2_2()
    if not after_reboot_result[0]:
        step_2_report = {'step_name': 'step_2 enable wireless',
                         'result': 'Fail',
                         'expect': "enable wireless success",
                         'actual': "enable wireless fail",
                         'note': '{}'.format(after_reboot_result[1])}
        cf.update_cases_result(report_file, case_name, step_2_report)
        restore()
        log.error("{:+^80}".format("test case fail"))
        return False
    step_2_report = {'step_name': 'step_2 enable wireless',
                     'result': 'Pass',
                     'expect': "enable wireless success",
                     'actual': "enable wireless success",
                     'note': '{}'.format(after_reboot_result[1])}
    cf.update_cases_result(report_file, case_name, step_2_report)
    restore()
    log.info("{:+^80}".format("test case pass"))
    return True


def start(case_name, **kwargs):
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)

    cf.case_steps_run_control(steps_list, __name__, case_name=case_name, report_file=report_file)

