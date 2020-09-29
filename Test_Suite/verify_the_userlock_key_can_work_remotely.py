# case name: verify_the_userlock_key_can_work_remotely
# Author: nick.lu
import subprocess
import pyautogui
import traceback
from Common.log import *
from Common import common_function as cf
from Test_Script.ts_network import network_setting


def get_default_hostname():
    eth_mac = subprocess.getoutput("ifconfig | grep eth0")
    lan_mac = subprocess.getoutput("ifconfig | grep wlan0")
    mac = eth_mac.split()[-1] if eth_mac else lan_mac.split()[-1]
    hostname = ''.join(mac.split(":"))
    return "HP"+hostname


def modify_hostname_registry(hostname):
    log.info("modify the hostname is '{}'".format(hostname))
    os.system("mclient --quiet set root/Network/Hostname '{}'".format(hostname))
    os.system("mclient commit")


def get_hostname_registry():
    log.info("get hostname")
    value = subprocess.getoutput("mclient --quiet get root/Network/Hostname")
    return value


def set_userlock(value):
    log.info("start set userLock value is {}".format(value))
    os.system("mclient --quiet set root/Network/userLock {}".format(value))
    os.system("mclient commit")


def export_profile(profile=cf.get_current_dir("Test_Data/profile_file.xml")):
    log.info("start export profile '{}'".format(profile))
    subprocess.call("export-profile.sh {} --quiet".format(profile), shell=True)


def import_profile(profile=cf.get_current_dir("Test_Data/profile_file.xml")):
    log.info("start import profile '{}'".format(profile))
    subprocess.call("import-profile.sh {} &".format(profile), shell=True)
    time.sleep(2)
    pyautogui.press("enter")


def set_static_network():
    try:
        log.info("start set static network")
        ip = cf.get_ip() if cf.get_ip() else ""
        log.info("ip: {}".format(ip))
        wired = network_setting.Wired()
        network_mask = wired.get_mask("eth0")
        mask = network_mask if network_mask else "255.255.255.192"
        log.info("mask: {}".format(mask))
        gateway = wired.gateway() if wired.gateway() else ""
        log.info("gateway: {}".format(gateway))
        wired.open_network_wired_dialog()
        wired.set_static_ip(ip_address=ip, subnet_mask=mask, default_gateway=gateway)
        return True
    except:
        log.error(traceback.format_exc())
        pyautogui.screenshot(cf.get_current_dir("Test_Report/set_static_network.png"))
        return False


def get_static_network_value():
    ip = subprocess.getoutput("mclient --quiet get root/Network/Wired/IPAddress")
    gateway = subprocess.getoutput("mclient --quiet get root/Network/Wired/DefaultGateway")
    mask = subprocess.getoutput("mclient --quiet get root/Network/Wired/SubnetMask")
    return ip, gateway, mask


def teardown_test_environment():
    os.system("mclient --quiet set root/Network/Wired/Method 'Automatic'")
    os.system("mclient --quiet set root/Network/Wired/IPAddress ''")
    os.system("mclient --quiet set root/Network/Wired/DefaultGateway ''")
    os.system("mclient --quiet set root/Network/Wired/SubnetMask ''")
    os.system("mclient commit")


def userlock_is_1(**kwargs):
    report_file = kwargs.get("report_file")
    case_name = kwargs.get("case_name")
    hostname = get_default_hostname()
    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)

    cf.SwitchThinProMode("admin")
    modify_hostname_registry("asdfgh")
    wired = network_setting.Wired()
    wired_connection_mode = subprocess.getoutput("mclient --quiet get root/Network/Wired/Method")
    if wired_connection_mode is not "Automatic":
        subprocess.call("mclient --quiet set root/Network/Wired/Method 'Automatic'", shell=True)
        subprocess.call("mclient commit", shell=True)
        for i in range(20):
            log.info("wait connect network...")
            time.sleep(2)
            if wired.check_wired_is_connected():
                log.info("wired is connected")
                break
    set_userlock("1")
    export_profile()

    if not set_static_network():
        log.error("set static network error")
        report = {'step_name': 'set static network',
                  'result': 'fail',
                  'expect': "set static network success",
                  'actual': "set static network fail",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        teardown_test_environment()
        modify_hostname_registry(hostname)
        cf.import_profile()
        os.remove(cf.get_current_dir("Test_Data/profile_file.xml"))
        log.error("{:+^80}".format("test case fail"))
        return False
    import_profile()
    log.info("reboot")
    time.sleep(30)


def userlock_is_0(**kwargs):
    report_file = kwargs.get("report_file")
    case_name = kwargs.get("case_name")
    hostname = get_default_hostname()

    cf.SwitchThinProMode("admin")
    if get_hostname_registry() != "asdfgh":
        log.error("hostname not is 'asdfgh'")
        report = {'step_name': 'check hostname after import profile',
                  'result': 'fail',
                  'expect': "hostname is 'asdfgh'",
                  'actual': "hostname not is 'asdfgh'",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        teardown_test_environment()
        modify_hostname_registry(hostname)
        cf.import_profile()
        os.remove(cf.get_current_dir("Test_Data/profile_file.xml"))
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("hostname is 'asdfgh'")
    report = {'step_name': 'check hostname after import profile',
              'result': 'pass',
              'expect': "hostname is 'asdfgh'",
              'actual': "hostname is 'asdfgh'",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)

    connection_mode = subprocess.getoutput("mclient --quiet get root/Network/Wired/Method")
    ip_list = get_static_network_value()
    if connection_mode != "Static" or ip_list.count("") == 3:                             # check mode and static ip
        log.error("connection mode and static ip info has modified after import profile")
        report = {'step_name': 'userLock is 1 and after import profile',
                  'result': 'fail',
                  'expect': "check connection mode is static and static ip not has clear",
                  'actual': "check connection mode not is static or static ip has clear",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        cf.import_profile()
        teardown_test_environment()
        modify_hostname_registry(hostname)
        os.remove(cf.get_current_dir("Test_Data/profile_file.xml"))
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("connection mode and static ip info not modified after import profile")
    report = {'step_name': 'userLock is 1 and after import profile',
              'result': 'pass',
              'expect': "check connection mode is static and static ip not has clear",
              'actual': "check connection mode is static and static ip not has clear",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)

    log.info("set userLock=0 and test again")                                 # set userLock = 0
    teardown_test_environment()
    set_userlock("0")
    export_profile()
    set_static_network()
    wired = network_setting.Wired()
    for i in range(20):
        log.info("wait wired connect...")
        time.sleep(2)
        if wired.check_wired_is_connected():
            log.info("wired is connected")
            break
    else:
        log.error("connect wired time out")
        report = {'step_name': 'connect wired',
                  'result': 'fail',
                  'expect': "connect wired success after set static ip",
                  'actual': "connect wired time out",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        cf.import_profile()
        teardown_test_environment()
        modify_hostname_registry(hostname)
        os.remove(cf.get_current_dir("Test_Data/profile_file.xml"))
        log.error("{:+^80}".format("test case fail"))
        return False
    import_profile()
    log.info("reboot")
    time.sleep(30)


def userlock_is_0_after_reboot(**kwargs):
    report_file = kwargs.get("report_file")
    case_name = kwargs.get("case_name")
    hostname = get_default_hostname()

    cf.SwitchThinProMode("admin")
    if get_hostname_registry() != "asdfgh":
        log.error("hostname not is 'asdfgh'")
        report = {'step_name': 'check hostname after import profile',
                  'result': 'fail',
                  'expect': "hostname is 'asdfgh'",
                  'actual': "hostname not is 'asdfgh'",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        cf.import_profile()
        teardown_test_environment()
        modify_hostname_registry(hostname)
        os.remove(cf.get_current_dir("Test_Data/profile_file.xml"))
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("hostname is 'asdfgh'")
    report = {'step_name': 'check hostname after import profile',
              'result': 'pass',
              'expect': "hostname is 'asdfgh'",
              'actual': "hostname is 'asdfgh'",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)

    connection_mode = subprocess.getoutput("mclient --quiet get root/Network/Wired/Method")
    ip_list = get_static_network_value()
    if connection_mode == "Static" or ip_list.count("") != 3:  # check mode and static ip
        log.error("the network setting of profile not restore after import profile")
        final_report = {'step_name': 'userLock is 0 and after import profile',
                        'result': 'fail',
                        'expect': "network connection mode is 'Automatic', and clear static ip",
                        'actual': "network connection mode not is 'Automatic', or not clear static ip",
                        'note': ''}
        cf.update_cases_result(report_file, case_name, final_report)
        cf.import_profile()
        teardown_test_environment()
        modify_hostname_registry(hostname)
        os.remove(cf.get_current_dir("Test_Data/profile_file.xml"))
        log.error("{:+^80}".format("test case fail"))
        return False

    log.info("the network setting of profile has restore after import profile")
    final_report = {'step_name': 'userLock is 0 and after import profile',
                    'result': 'Pass',
                    'expect': "network connection mode is 'Automatic', and clear static ip",
                    'actual': "network connection mode is 'Automatic', and clear static ip",
                    'note': ''}
    cf.update_cases_result(report_file, case_name, final_report)
    cf.import_profile()
    modify_hostname_registry(hostname)
    os.remove(cf.get_current_dir("Test_Data/profile_file.xml"))
    log.info("{:+^80}".format("test case pass"))
    return True


def start(case_name, **kwargs):
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)

    steps_list = ("userlock_is_1", "userlock_is_0", "userlock_is_0_after_reboot")
    cf.case_steps_run_control(steps_list, __name__, case_name=case_name, report_file=report_file)


