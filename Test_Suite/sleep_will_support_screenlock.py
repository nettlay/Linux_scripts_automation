from Common.common_function import get_current_dir
import os
from Common.common_function import new_cases_result, check_ip_yaml, get_folder_items
import time
from Common.log import log
from Common.picture_operator import wait_element, capture_screen_by_loc, compare_pic_similarity
from Common.tool import click, tap_key, keyboard, mouse
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
from Common.exception import IconNotExistError
from Test_Script.ts_power_manager.common_function import PrepareWakeUp, linux_check_locked, event, SwitchThinProMode
from Test_Script.ts_power_manager import screensaver


def close_control_pannel():
    time.sleep(2)
    return PowerManagerFactory.close_all_power_manager()


def set_user_password():
    current_path = get_current_dir("Test_Data")
    temp_path = current_path + "/temp.png"
    user = current_path + "/td_power_manager/user_icon"
    enabled = user + "/enabled"
    change_path = user + "/change"
    SwitchThinProMode("admin")
    time.sleep(1)
    log.info("Open security desktop")
    os.popen("hptc-control-panel --config-panel /etc/hptc-control-panel/applications/hptc-security.desktop")
    time.sleep(4)
    print(user)
    res = wait_element(user)
    if res:
        location, shape = res
        loc_x, loc_y = location
        offset_x, offset_y = 0, -20
        loc = {"left": loc_x + offset_x, "top": loc_y + offset_y, "width": 500, "height": 40}
        capture_screen_by_loc(temp_path, loc)
        enabled_list = get_folder_items(enabled, file_only=True)
        change_path_list = get_folder_items(change_path, file_only=True)
        flag = True
        for i in enabled_list:
            if compare_pic_similarity(enabled + "/{}".format(i), temp_path):
                break
        else:
            flag = False
        for i in change_path_list:
            change_res = compare_pic_similarity(change_path + "/{}".format(i), temp_path)
            if change_res:
                break
        else:
            change_res = False
        if flag and change_res:
            print(change_res, "change")
            change_loc, change_shape = change_res
            offset = (change_loc[0] + int(change_shape[1]/2), change_loc[1] + int(change_shape[0]/2))
            print(offset)
            return (loc_x + offset_x, loc_y + offset_y), offset
    return False


def set_user_password_callback(res):
    loc, offset = res
    loc_x, loc_y = loc[0] + offset[0], loc[1] + offset[1]
    click(loc_x, loc_y)
    time.sleep(1)
    tap_key("1", 1)
    tap_key("Tab", 1)
    tap_key("1", 1)
    tap_key(keyboard.enter_key, 2)
    close_control_pannel()
    return


def set_sleep_time(power_manager, t=2, revert=False):
    try:
        if revert:
            t = 30
        power_manager.AC.switch()
        power_manager.AC.set(pms=pms.AC.Minutes_before_system_sleep, radio="on", text="{}".format(t))
        power_manager.apply()
    except IconNotExistError:
        return False
    return True


def set_screen_saver_time(power_manager, t=1, revert=False):
    try:
        radio = "on"
        if revert:
            radio = "off"
            t = 10
        power_manager.ScreenSaver.switch()
        power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
        power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_general_users, radio=radio)
        power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Minutes_before_automatic_Screensaver_activation, radio="on",
                                      text="{}".format(t))
        power_manager.apply()
    except IconNotExistError:
        return False
    return True


def check_screen_saver():
    return linux_check_locked()


def wait_and_check_screen_saver(t=65):
    time.sleep(t)
    return check_screen_saver()


def resume_lock_screen(sctool):
    return sctool.resume_lock_screen_by_mouse()


def move_mouse():
    time.sleep(2)
    mouse.click(10, 10)
    time.sleep(2)
    return


def check_password_frame_exist(flag=True):
    time.sleep(2)
    pic_path = get_current_dir("Test_Data/td_power_manager/loc_screen_pic")
    res = wait_element(pic_path)
    res_flag = True if res else False
    if res_flag == flag:
        return True
    return False


def preparewakeup(t=120):
    with PrepareWakeUp(time=t) as w:
        w.wait(t)
    t_gap = w.get_max_time_gap()
    print(t_gap)
    if t_gap > 11:
        return True
    return False


def check_desktop_exist():
    path = get_current_dir("Test_Data/td_power_manager/desktop")
    res = wait_element(path)
    if not res:
        os.popen("reboot")
    return


def step1(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    power_manager = kwargs.get("power_manager")
    new_cases_result(yml_path, case_name)
    event_dict = {
        "event_method": set_user_password,
        "event_params": ((), {}),
        "call_back": set_user_password_callback,
        "inherit": True,
        "error_msg": {'actual': 'icon not exist'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    if not event(**event_dict):
        close_control_pannel()
        return False
    time.sleep(3)
    power_manager.open_power_manager_from_control_panel()
    time.sleep(1)
    event_dict = {
        "event_method": set_sleep_time,
        "event_params": ((power_manager,), {}),
        "error_msg": {'actual': 'set sleep time fail'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    event(**event_dict)
    event_dict.update({"event_method": set_screen_saver_time,
                       "event_params": ((power_manager,), {}),
                       "error_msg": {'actual': 'set screen saver fail'}
                       })
    event(**event_dict)
    close_control_pannel()
    return True


def step2(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    SwitchThinProMode("user")
    event_dict = {
        "event_method": wait_and_check_screen_saver,
        "event_params": ((), {}),
        "call_back": move_mouse,
        "callback_parmas": ((), {}),
        "error_msg": {'actual': 'screen saver launch fail, lock screen fail'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def step3(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    event_dict = {"event_method": check_password_frame_exist,
                  "error_msg": {"expect": "need password",
                                'actual': 'no password'},
                  "case_name": case_name,
                  "yml_path": yml_path
                  }
    return event(**event_dict)


def step4(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    sctool = kwargs.get("screensavertool")
    event_dict = {"event_method": preparewakeup,
                  "error_msg": {'actual': 'wake too late or not sleep'},
                  "callback_parmas": ((sctool,), {}),
                  "call_back": resume_lock_screen,
                  "do_call_back_while_fail": True,
                  "do_call_back": False,
                  "case_name": case_name,
                  "yml_path": yml_path
                  }
    return event(**event_dict)


def step5(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    SwitchThinProMode("user")
    event_dict = {
        "event_method": wait_and_check_screen_saver,
        "event_params": ((1, ), {}),
        "call_back": move_mouse,
        "callback_parmas": ((), {}),
        "error_msg": {'actual': 'screen saver launch fail, lock screen fail'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def step6(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    sctool = kwargs.get("screensavertool")
    event_dict = {"event_method": check_password_frame_exist,
                  "error_msg": {"expect": "need password",
                                'actual': 'no password'},
                  "call_back": resume_lock_screen,
                  "do_call_back_while_fail": True,
                  "callback_parmas": ((sctool,), {}),
                  "case_name": case_name,
                  "yml_path": yml_path
                  }
    return event(**event_dict)


def step7(*args, **kwargs):
    time.sleep(5)
    screensaver.ScreenSaver.lock_screen_by_hotkey()
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    event_dict = {"event_method": wait_and_check_screen_saver,
                  "event_params": ((2,), {}),
                  "error_msg": {'actual': 'lock screen fail'},
                  "case_name": case_name,
                  "yml_path": yml_path
                  }
    return event(**event_dict)


def step8(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    sctool = kwargs.get("screensavertool")
    event_dict = {"event_method": preparewakeup,
                  "error_msg": {'actual': 'wake up fail'},
                  "call_back": resume_lock_screen,
                  "do_call_back_while_fail": True,
                  "callback_parmas": ((sctool,), {}),
                  "case_name": case_name,
                  "yml_path": yml_path
                  }
    return event(**event_dict)


def step9(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    sctool = kwargs.get("screensavertool")
    event_dict = {"event_method": check_password_frame_exist,
                  "event_params": ((), {"flag": False}),
                  "error_msg": {'actual': 'password frame exist', 'expect': ''},
                  "call_back": resume_lock_screen,
                  "do_call_back": False,
                  "do_call_back_while_fail": True,
                  "callback_parmas": ((sctool,), {}),
                  "case_name": case_name,
                  "yml_path": yml_path
                  }
    return event(**event_dict)


def resume_all_settings(*args, **kwargs):
    SwitchThinProMode("admin")
    os.system("mclient --quiet set root/screensaver/timeoutScreensaver 10")
    os.system("mclient --quiet set root/screensaver/lockScreenUser 0")
    os.system("mclient --quiet set root/Power/default/AC/sleep 30")
    time.sleep(1)
    os.system("mclient commit")
    power_manager = kwargs.get("power_manager")
    power_manager.open_power_manager_from_control_panel()
    set_sleep_time(power_manager, revert=True)
    set_screen_saver_time(power_manager, revert=True)
    power_manager.apply()
    SwitchThinProMode("user")
    close_control_pannel()
    return


def start(case_name, **kwargs):
    close_control_pannel()
    ip = check_ip_yaml()
    yml_path = get_current_dir("Test_Report/{}.yaml").format(ip)
    power_manager = PowerManagerFactory("AC", "ScreenSaver")
    screensavertool = screensaver.ScreenSaver()
    params = {"case_name": case_name,
              "yml_path": yml_path,
              "screensavertool": screensavertool,
              "power_manager": power_manager}
    flag = True
    flag = step1(**params) if flag else False
    flag = step2(**params) if flag else False
    flag = step3(**params) if flag else False
    flag = step4(**params) if flag else False
    flag = step5(**params) if flag else False
    flag = step6(**params) if flag else False
    flag = step7(**params) if flag else False
    flag = step8(**params) if flag else False
    flag = step9(**params) if flag else False
    resume_all_settings(**params)
    return True

