from Test_Script.ts_power_manager.common_function import event, linux_check_locked, preparewakeup
from Common.common_function import new_cases_result, check_ip_yaml, get_current_dir
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
import time
from Common.picture_operator import wait_element
from Common.exception import IconNotExistError
import os
from Test_Script.ts_power_manager import screensaver
from Test_Script.ts_power_manager.common_function import SwitchThinProMode


def close_powermanager():
    return PowerManagerFactory.close_all_power_manager()


def set_ac_min_to_one(power_manager, revert=False):
    try:
        t = 1
        if revert:
            t = 30
        power_manager.open_power_manager_from_control_panel()
        power_manager.AC.switch()
        power_manager.AC.set(pms=pms.AC.Minutes_before_system_sleep, radio="on", text="{}".format(t))
        power_manager.apply()
    except IconNotExistError:
        return False
    finally:
        close_powermanager()
    return True


def set_ac_min_to_close(power_manager, revert=False):
    try:
        radio = "off"
        if revert:
            radio = "on"
        time.sleep(2)
        power_manager.open_power_manager_from_control_panel()
        power_manager.AC.switch()
        power_manager.AC.set(pms=pms.AC.Minutes_before_system_sleep, radio=radio)
    except IconNotExistError:
        return False
    return True


def resume_all_settings(*args, **kwargs):
    power_manager = kwargs.get("power_manager")
    os.system("mclient --quiet set root/Power/default/AC/sleep 30")
    time.sleep(1)
    os.system("mclient commit")
    SwitchThinProMode("admin")
    time.sleep(1)
    set_ac_min_to_one(power_manager, revert=True)
    SwitchThinProMode("user")


def check_screen_saver():
    return linux_check_locked()


def wait_and_check_screen_saver(t=65, flag=True):
    time.sleep(t)
    res = check_screen_saver()
    res = res if res else False
    if flag == res:
        return True
    return False


def resume_lock_screen(sctool):
    return sctool.resume_lock_screen_by_mouse()


def check_min_to_zero():
    path = get_current_dir("Test_Data/td_power_manager/verify_sleep_mode_disabled")
    res = wait_element(path)
    if res:
        return True
    return False


def step1(*args, **kwargs):
    SwitchThinProMode("admin")
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    new_cases_result(yml_path, case_name)
    power_manager = kwargs.get("power_manager")
    event_dict = {
        "event_method": set_ac_min_to_one,
        "event_params": ((power_manager, ), {}),
        "error_msg": {'actual': 'set power manager fail'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def step2(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    sctool = kwargs.get("screensavertool")
    event_dict = {"event_method": preparewakeup,
                  "event_params": ((60,), {}),
                  "call_back": resume_lock_screen,
                  "callback_parmas": ((sctool,), {}),
                  "do_call_back_while_fail": True,
                  "do_call_back": False,
                  "error_msg": {'actual': 'wake too late or not sleep'},
                  "case_name": case_name,
                  "yml_path": yml_path
                  }
    return event(**event_dict)


def step3(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    sctool = kwargs.get("screensavertool")
    event_dict = {
        "event_method": wait_and_check_screen_saver,
        "event_params": ((1, ), {}),
        "error_msg": {'actual': 'screen saver launch fail'},
        "call_back": resume_lock_screen,
        "do_call_back_while_fail": True,
        "callback_parmas": ((sctool,), {}),
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def step4(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    power_manager = kwargs.get("power_manager")
    event_dict = {
        "event_method": set_ac_min_to_close,
        "event_params": ((power_manager, ), {}),
        "error_msg": {'actual': 'set power manager fail'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def step5(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    power_manager = kwargs.get("power_manager")
    event_dict = {
        "event_method": check_min_to_zero,
        "event_params": ((), {}),
        "error_msg": {'actual': 'not zero'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    flag = event(**event_dict)
    try:
        power_manager.apply()
    except IconNotExistError:
        return False
    return flag


def step6(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    event_dict = {
        "event_method": wait_and_check_screen_saver,
        "event_params": ((), {"flag": False}),
        "error_msg": {'actual': 'screen saver launch', "expect": "screens saver not launch"},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def start(case_name, **kwargs):
    ip = check_ip_yaml()
    yml_path = get_current_dir("Test_Report/{}.yaml").format(ip)
    power_manager = PowerManagerFactory("AC", "ScreenSaver")
    screensavertool = screensaver.ScreenSaver()
    params = {"case_name": case_name,
              "yml_path": yml_path,
              "screensavertool": screensavertool,
              "power_manager": power_manager}
    flag = step1(**params)
    flag = step2(**params) if flag else False
    flag = step3(**params) if flag else False
    flag = step4(**params) if flag else False
    flag = step5(**params) if flag else False
    flag = step6(**params) if flag else False
    power_manager.close_all_power_manager()
    resume_all_settings(**params)
    return flag