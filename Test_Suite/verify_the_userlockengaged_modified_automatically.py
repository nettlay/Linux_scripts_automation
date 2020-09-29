# case name: verify_the_userlockengaged_key_value_can_be_modified_automatically
# nick.lu
import subprocess
from Common.log import *
from Common import common_function as cf
from Test_Script.ts_network import network_setting


def userlockengaged_value():
    value = subprocess.getoutput("mclient --quiet get root/Network/userLockEngaged")
    return value


def start(case_name, **kwargs):
    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)

    cf.SwitchThinProMode("admin")
    default_profile = cf.get_current_dir("Test_Data/profile.xml")
    if not os.path.exists(default_profile):
        log.error("not found the default profile")
        check_profie_report = {'step_name': 'check default profile file',
                               'result': 'Fail',
                               'expect': "found default profile file",
                               'actual': "not found default profile file",
                               'note': ''}
        cf.update_cases_result(report_file, case_name, check_profie_report)
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("found the default profile")
    log.info("start import the default profile")
    cf.import_profile()

    log.info("start check the value of userLockEngaged")                          # step 1 -------------
    if userlockengaged_value() is not "0":
        log.error("the default value of userLockEngaged not is '0'")
        check_userLockEngaged_report = {'step_name': 'check default profile file',
                                        'result': 'Fail',
                                        'expect': "userLockEngaged is '0'",
                                        'actual': "userLockEngaged not is '0'",
                                        'note': ''}
        cf.update_cases_result(report_file, case_name, check_userLockEngaged_report)
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("the default value of userLockEngaged is '0'")
    check_userLockEngaged_report = {'step_name': 'check default profile file',
                                    'result': 'Pass',
                                    'expect': "userLockEngaged is '0'",
                                    'actual': "userLockEngaged is '0'",
                                    'note': ''}
    cf.update_cases_result(report_file, case_name, check_userLockEngaged_report)
    log.info("start modify the hostname")                                       # step 2 ---------------
    dns = network_setting.DNS()
    dns.open_dns()
    dns.dns_set_hostname("123456")
    dns.apply()
    dns.close_control_panel()

    log.info("check the value of userLockEngaged again")                        # step 3 -------------------
    if userlockengaged_value() is not "1":
        log.error("the value of userLockEngaged not is '1'")
        check_userLockEngaged_report = {'step_name': 'check default profile file',
                                        'result': 'Fail',
                                        'expect': "userLockEngaged auto changed to '1'",
                                        'actual': "userLockEngaged not auto changed to '1'",
                                        'note': ''}
        cf.update_cases_result(report_file, case_name, check_userLockEngaged_report)
        cf.import_profile()
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("the value of userLockEngaged is '1'")
    check_userLockEngaged_report = {'step_name': 'check default profile file',
                                    'result': 'Pass',
                                    'expect': "userLockEngaged auto changed to '1'",
                                    'actual': "userLockEngaged auto changed to '1'",
                                    'note': ''}
    cf.update_cases_result(report_file, case_name, check_userLockEngaged_report)
    cf.import_profile()
    wired = network_setting.Wired()
    for i in range(20):
        if wired.check_wired_is_connected():
            break
        time.sleep(2)
    log.info("{:+^80}".format("test case pass"))
    return True

