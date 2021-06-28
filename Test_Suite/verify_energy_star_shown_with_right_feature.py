from Common.common_function import case_steps_run_control, get_current_dir
from Test_Script.ts_power_manager.common_function import event
import os
import time
from Common.common_function import new_cases_result, check_ip_yaml
from Common.picture_operator import wait_element
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory


def set_bios_config():
    path = get_current_dir("Test_Data/td_power_manager/bios_config.txt")
    os.system("hptc-bios-cfg -S {}".format(path))
    return True


def reboot(*args, **kwargs):
    time.sleep(3)
    os.system("reboot")
    time.sleep(15)
    return True


def check_estar_logo():
    path = get_current_dir("Test_Data/td_power_manager/verify_energy_star_shown_right/energy_star")
    res = wait_element(path)
    return res


def step1(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    new_cases_result(yml_path, case_name)
    event_dict = {
        "event_method": set_bios_config,
        "event_params": ((), {}),
        "case_name": case_name,
        "yml_path": yml_path}
    return event(**event_dict)


def step3(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    PowerManagerFactory.open_power_manager_from_control_panel()
    time.sleep(3)
    event_dict = {
        "event_method": check_estar_logo,
        "case_name": case_name,
        "yml_path": yml_path}
    return event(**event_dict)


def resume(*args, **kwargs):
    return PowerManagerFactory.close_all_power_manager()


def start(case_name, **kwargs):
    ip = check_ip_yaml()
    yml_path = get_current_dir("Test_Report/{}.yaml").format(ip)
    params = {"case_name": case_name,
              "yml_path": yml_path}
    step_list = ['step1', 'reboot', 'step3', 'resume']
    case_steps_run_control(step_list, __name__, **params)
    resume()
    return
