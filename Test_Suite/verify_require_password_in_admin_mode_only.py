from Test_Script.ts_power_manager.common_function import event, linux_check_locked, check_password_frame_exist, \
    SwitchThinProMode
from Common.common_function import new_cases_result, check_ip_yaml, get_current_dir
from Common.tool import right_click, mouse, click, tap_key,keyboard
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
from Test_Script.ts_power_manager import screensaver
import time
import copy
from Common.picture_operator import wait_element
from Common.exception import IconNotExistError
import os


def close_powermanager():
    return PowerManagerFactory.close_all_power_manager()


def set_screen_saver(revert=False):
    time.sleep(2)
    try:
        t = 1
        if revert:
            t = 10
        power_manager = PowerManagerFactory("ScreenSaver")
        power_manager.open_power_manager_from_control_panel()
        power_manager.ScreenSaver.switch()
        power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
        power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Minutes_before_automatic_Screensaver_activation, radio="on",
                                      text="{}".format(t))
        power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_domain_users, radio="on")
        power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_general_users, radio="off")
        power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_in_Administrator_Mode, radio="on")
        power_manager.apply()
    except IconNotExistError:
        return False
    finally:
        time.sleep(1)
        close_powermanager()
    return True


def resume_lock_screen(sctool):
    return sctool.resume_lock_screen_by_mouse()


def wait_and_check_screen_saver(t=65):
    time.sleep(t)
    return linux_check_locked()


def check_lock_screen_icon_exist(flag=True):
    right_click(200, 200)
    path = get_current_dir("Test_Data/td_power_manager/verify_require_password_in_admin/lock_screen")
    res = wait_element(path)
    flag_res = True if res else False
    if flag_res == flag:
        return True
    return False


def resume_right_click():
    loc = mouse.position()
    x, y = loc[0]-10, loc[1]-10
    click(x, y)
    return True


def tap_enter():
    time.sleep(1)
    tap_key(keyboard.enter_key)
    return


def step1(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    new_cases_result(yml_path, case_name)
    SwitchThinProMode("admin")
    event_dict = {
        "event_method": set_screen_saver,
        "event_params": ((), {}),
        "error_msg": {'actual': 'power manager set fail'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def step2(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    SwitchThinProMode("user")
    event_dict = {
        "event_method": wait_and_check_screen_saver,
        "event_params": ((), {}),
        "call_back": tap_enter,
        "error_msg": {'actual': 'screen saver launch fail'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def step3(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    sctool = kwargs.get("screensavertool")
    event_dict = {
        "event_method": check_password_frame_exist,
        "event_params": ((), {"flag": False}),
        "call_back": resume_lock_screen,
        "callback_parmas": ((sctool, ), {}),
        "do_call_back_while_fail": True,
        "error_msg": {'actual': 'password frame exist error'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def step4(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    event_dict = {
        "event_method": check_lock_screen_icon_exist,
        "event_params": ((), {"flag": False}),
        "call_back": resume_right_click,
        "case_name": case_name,
        "yml_path": yml_path}
    return event(**event_dict)


def step5(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    time.sleep(3)
    screensaver.ScreenSaver.lock_screen_by_hotkey()
    event_dict = {
        "event_method": wait_and_check_screen_saver,
        "event_params": ((3,), {}),
        "error_msg": {'actual': 'screen saver launch fail'},
        "call_back": tap_enter,
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def step6(*args, **kwargs):
    return step3(*args, **kwargs)


def step7(*args, **kwargs):
    SwitchThinProMode("admin")
    return step5(*args, **kwargs)


def step8(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    sctool = kwargs.get("screensavertool")
    event_dict = {
        "event_method": check_password_frame_exist,
        "event_params": ((), {}),
        "call_back": resume_lock_screen,
        "callback_parmas": ((sctool,), {}),
        "error_msg": {'actual': 'password frame not exist'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def restore_all_settings():
    return set_screen_saver(True)


def restore_all_settings_command():
    os.system("mclient --quiet set root/screensaver/timeoutScreensaver 10")
    os.system("mclient --quiet set root/screensaver/lockScreenUser 0")
    os.system("mclient --quiet set root/screensaver/lockScreenDomain 1")
    os.system("mclient --quiet set root/screensaver/lockScreen 1")
    time.sleep(1)
    os.system("mclient commit")
    SwitchThinProMode("admin")
    time.sleep(1)
    set_screen_saver(revert=True)
    SwitchThinProMode("user")


def start(case_name, **kwargs):
    ip = check_ip_yaml()
    yml_path = get_current_dir("Test_Report/{}.yaml").format(ip)
    screensavertool = screensaver.ScreenSaver()
    params = {"case_name": case_name,
              "yml_path": yml_path,
              "screensavertool": screensavertool}
    flag = True
    flag = step1(**params)
    flag = step2(**params) if flag else False
    flag = step3(**params) if flag else False
    flag = step4(**params) if flag else False
    flag = step5(**params) if flag else False
    flag = step6(**params) if flag else False
    flag = step7(**params) if flag else False
    flag = step8(**params) if flag else False
    if not flag:
        tap_enter()
    restore_all_settings_command()
    return flag