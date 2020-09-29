#  case name: Verify can open the power manager from the system tray mtc

import os
import time
import subprocess
from Common import common_function as cf
from Test_Script.ts_power_manager import power_manager_factory
from Common.log import Logger


def start(case_name, **kwargs):
    log = Logger()
    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)
    time.sleep(0.5)

    platform = subprocess.getoutput("hptc-hwsw-id --hw")
    if "mt" not in platform:
        log.error("dtc can't run this case")
        log.info("{:+^70}".format("this case test over"))
        time.sleep(1)
        return False
    cf.SwitchThinProMode(switch_to="user")
    time.sleep(2)
    if not power_manager_factory.PowerManager.open_power_manager_from_tray():
        step1 = {'step_name': 'step1',
                 'result': 'Fail',
                 'expect': 'in user mode, open the power manager from the system tray success',
                 'actual': 'open the power manager from the system tray fail',
                 'note': ''}
        cf.update_cases_result(report_file, case_name, step1)
        log.info("{:+^70}".format("this case test over"))
        time.sleep(1)
        return False
    step1 = {'step_name': 'step1',
             'result': 'Pass',
             'expect': 'in user mode, open the power manager from the system tray success',
             'actual': 'open the power manager from the system tray success',
             'note': ''}
    cf.update_cases_result(report_file, case_name, step1)
    os.system("wmctrl -c 'Control Panel'")
    time.sleep(1)

    cf.SwitchThinProMode(switch_to="admin")
    time.sleep(2)
    if not power_manager_factory.PowerManager.open_power_manager_from_tray():
        step2 = {'step_name': 'step2',
                 'result': 'Fail',
                 'expect': 'in admin mode, open the power manager from the system tray success',
                 'actual': 'open the power manager from the system tray fail',
                 'note': ''}
        cf.update_cases_result(report_file, case_name, step2)
        log.info("{:+^70}".format("this case test over"))
        time.sleep(1)
        return False
    step2 = {'step_name': 'step2',
             'result': 'Pass',
             'expect': 'in admin mode, open the power manager from the system tray success',
             'actual': 'open the power manager from the system tray success',
             'note': ''}
    cf.update_cases_result(report_file, case_name, step2)
    time.sleep(1)
    os.system("wmctrl -c 'Control Panel'")       # close control panel

    log.info("{:+^70}".format("this case test over"))
    time.sleep(1)
    return True

