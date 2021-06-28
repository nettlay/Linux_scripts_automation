from Test_Script.ts_power_manager.common_function import event, linux_check_locked
from Common.common_function import new_cases_result, check_ip_yaml, get_current_dir, get_folder_items
from Common.tool import tap_key, keyboard, click
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
import functools
import time
import copy
from Common.picture_operator import capture_screen_by_loc, compare_pic_similarity, wait_element
from Common.exception import IconNotExistError
import os
from Test_Script.ts_power_manager import screensaver
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common import log
log = log.Logger()


def check_default_status(**status):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if not res:
                return False
            loc, shape = res
            checked = status.get("checkedbox", "")
            text = status.get("text", "")
            selected = status.get("selected", "")
            loc_x, loc_y = loc
            save_path = get_current_dir() + "/Test_Data/td_power_manager/temp.png"
            if checked:
                checked_path = get_current_dir("Test_Data/td_power_manager/verify_screen_saver_works/checked")
                if checked.lower() == "disabled":
                    checked_path = get_current_dir("Test_Data/td_power_manager/verify_screen_saver_works/unchecked")
                pic_list = get_folder_items(checked_path)
                assert pic_list != [], "{} not exist".format(checked_path)
                off_x, off_y = -30, -15
                fil_x = loc_x + off_x if loc_x + off_x > 0 else 0
                fil_y = loc_y + off_y if loc_y + off_y > 0 else 0
                filter_dic = {"left": fil_x, "top": fil_y, "width": 30, "height": 30}
                capture_screen_by_loc(save_path, filter_dic)
                for i in pic_list:
                    if compare_pic_similarity(checked_path + "/" + i, save_path):
                        break
                else:
                    return False
            elif text:
                text_path = get_current_dir("Test_Data/td_power_manager/verify_screen_saver_works/text/{}".format(text))
                pic_list = get_folder_items(text_path)
                assert pic_list != [], "{} not exist".format(text_path)
                off_x, off_y = shape[1] - 10, -15
                fil_x = loc_x + off_x if loc_x + off_x > 0 else 0
                fil_y = loc_y + off_y if loc_y + off_y > 0 else 0
                filter_dic = {"left": fil_x, "top": fil_y, "width": 200, "height": 35}
                capture_screen_by_loc(save_path, filter_dic)
                for i in pic_list:
                    if compare_pic_similarity(text_path + "/" + i, save_path):
                        break
                else:
                    return False
            elif selected:
                text_path = get_current_dir("Test_Data/td_power_manager/verify_screen_saver_works/selected/{}".format(selected.lower()))
                pic_list = get_folder_items(text_path)
                assert pic_list != [], "{} not exist".format(text_path)
                off_x, off_y = shape[1] - 10, -15
                fil_x = loc_x + off_x if loc_x + off_x > 0 else 0
                fil_y = loc_y + off_y if loc_y + off_y > 0 else 0
                filter_dic = {"left": fil_x, "top": fil_y, "width": 200, "height": 35}
                capture_screen_by_loc(save_path, filter_dic)
                for i in pic_list:
                    if compare_pic_similarity(text_path + "/" + i, save_path):
                        break
                else:
                    return False
            return True

        return wrapper

    return decorator


@check_default_status(checkedbox="enabled")
def check_enable_screen_saver_status():
    path = get_current_dir("Test_Data/td_power_manager/verify_screen_saver_works/2")
    res = wait_element(path)
    return res


@check_default_status(text=10)
def check_default_time():
    path = get_current_dir("Test_Data/td_power_manager/PowerManager/ScreenSaver/3")
    res = wait_element(path)
    return res


@check_default_status(selected="Default")
def check_image_mapping():
    path = get_current_dir("Test_Data/td_power_manager/PowerManager/ScreenSaver/10")
    res = wait_element(path)
    return res


@check_default_status(checkedbox="enabled")
def check_standard_image():
    path = get_current_dir("Test_Data/td_power_manager/PowerManager/ScreenSaver/7")
    res = wait_element(path)
    return res


@check_default_status(checkedbox="enabled")
def check_require_password_in_admin():
    path = get_current_dir("Test_Data/td_power_manager/verify_screen_saver_works/4")
    res = wait_element(path)
    return res


@check_default_status(checkedbox="enabled")
def check_require_password_for_domain():
    path = get_current_dir("Test_Data/td_power_manager/verify_screen_saver_works/5")
    res = wait_element(path)
    return res


@check_default_status(checkedbox="disabled")
def check_require_passwoed_for_general_user():
    path = get_current_dir("Test_Data/td_power_manager/verify_screen_saver_works/6")
    res = wait_element(path)
    return res


def wait_and_check_screen_saver(t=55):
    log.info("start wait time")
    for i in range(9):
        time.sleep(t)
        if linux_check_locked():
            log.error("current loop times {}".format(i))
            break
    else:
        time.sleep(t + 35)
        flag = linux_check_locked()
        log.info("check screen lock result:{}".format(flag))
        return flag
    return False


def resume():
    return tap_key(keyboard.enter_key)


def check_password_frame_exist(flag=True):
    time.sleep(2)
    pic_path = get_current_dir("Test_Data/td_power_manager/loc_screen_pic")
    res = wait_element(pic_path)
    res_flag = True if res else False
    if res_flag == flag:
        return True
    return False


def open_screensaver():
    time.sleep(2)
    try:
        power_manager = PowerManagerFactory("ScreenSaver")
        power_manager.open_power_manager_from_control_panel()
        power_manager.ScreenSaver.switch()
    except IconNotExistError:
        close_powermanager()
        return False
    return True


def resume_lock_screen(sctool):
    return sctool.resume_lock_screen_by_mouse()


def close_powermanager():
    return PowerManagerFactory.close_all_power_manager()


def step1(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    new_cases_result(yml_path, case_name)
    SwitchThinProMode("user")
    event_list = []
    event_dict = {
        "event_method": open_screensaver,
        "error_msg": {'actual': 'open screensaver fail'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    event_list.append(copy.deepcopy(event_dict))
    event_dict = {
        "event_method": check_enable_screen_saver_status,
        "error_msg": {'actual': 'disabled',
                      'except': 'enabled'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    event_list.append(copy.deepcopy(event_dict))
    event_dict.update({"event_method": check_default_time,
                       'except': '10',
                       'actual': ''})
    event_list.append(copy.deepcopy(event_dict))
    event_dict.update({"event_method": check_image_mapping,
                       'except': 'default',
                       'actual': ''})
    event_list.append(copy.deepcopy(event_dict))
    event_dict.update({"event_method": check_standard_image,
                       'except': 'disabled',
                       'actual': 'enabled'})
    event_list.append(copy.deepcopy(event_dict))
    event_dict.update({"event_method": check_require_password_in_admin,
                       'except': 'enabled',
                       'actual': 'disabled'})
    event_list.append(copy.deepcopy(event_dict))
    event_dict.update({"event_method": check_require_password_for_domain,
                       'except': 'enabled',
                       'actual': 'disabled'})
    event_list.append(copy.deepcopy(event_dict))
    event_dict.update({"event_method": check_require_passwoed_for_general_user,
                       'except': 'disabled',
                       'actual': 'enabled'})
    event_list.append(copy.deepcopy(event_dict))
    for i in event_list:
        res = event(**i)
        if not res:
            return False
    close_powermanager()
    return True


def step2(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    click(150, 200)
    event_dict = {
        "event_method": wait_and_check_screen_saver,
        "error_msg": {'actual': 'screen saver launch fail'},
        "call_back": resume,
        "do_call_back_while_fail": True,
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
        "do_call_back": False,
        "do_call_back_while_fail": True,
        "callback_parmas": ((sctool,), {}),
        "error_msg": {'actual': 'user mode need password'},
        "case_name": case_name,
        "yml_path": yml_path
    }
    return event(**event_dict)


def start(case_name, **kwargs):
    ip = check_ip_yaml()
    yml_path = get_current_dir("Test_Report/{}.yaml").format(ip)
    screensavertool = screensaver.ScreenSaver()
    params = {"case_name": case_name,
              "yml_path": yml_path,
              "screensavertool": screensavertool}
    flag = step1(**params)
    flag = step2(**params) if flag else False
    flag = step3(**params)
    if not flag:
        os.popen("reboot")
        time.sleep(15)
    return flag

