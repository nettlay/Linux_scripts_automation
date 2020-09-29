from Test_Script.ts_power_manager.common_function import event, PrepareWakeUp
from Common.common_function import open_window, get_current_dir
from Common.common_function import new_cases_result, check_ip_yaml
from Test_Script.ts_power_manager import screensaver
from Test_Script.ts_power_manager.common_function import SwitchThinProMode


def preparewakeup(t=15):
    with PrepareWakeUp(time=t) as w:
        open_window("sleep")
    t_gap = w.get_max_time_gap()
    print(t_gap)
    if t_gap > 11:
        return True
    return False


def resume_lock_screen(sctool):
    return sctool.resume_lock_screen_by_mouse()


def step1(*args, **kwargs):
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path")
    sctool = kwargs.get("screensavertool")
    new_cases_result(yml_path, case_name)
    SwitchThinProMode("admin")
    event_dict = {
        "event_method": preparewakeup,
        "event_params": ((), {}),
        "call_back": resume_lock_screen,
        "callback_parmas": ((sctool, ), {}),
        "do_call_back_while_fail": True,
        "error_msg": {'actual': 'wol wake up fail'},
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
    step1(**params)
    SwitchThinProMode("user")