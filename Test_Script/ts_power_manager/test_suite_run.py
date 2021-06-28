# from Test_Script.ts_power_manager import reboot_function
from Common import common_function


steps_list = ("setup",
              "set_lock_screen",
              "lock_screen",
              "check_screen_lock",
              "record_result",
              "teardown"
              )


def setup(*args, **kwargs):
    case_name = kwargs.get("case_name")
    log = kwargs.get("log")
    report_file = kwargs.get("report_file")

    # case_name, log, report_file, *arg = args
    print("setup ============ ", case_name)
    print("log", log)
    print("report_file", report_file)
    return True


def set_lock_screen(*args, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    # report_file, case_name, *arg = args
    print("set_lock_screen ========== ")
    print("report_file", report_file)
    print("case_name", case_name)
    return True


def lock_screen(*args, **kwargs):
    print("lock_screen========")
    return True


def check_screen_lock(*args, **kwargs):
    print("check_screen_lock==========")
    return True


def record_result(*args, **kwargs):
    print("record_result===========")
    return True


def teardown(*args, **kwargs):
    print("teardown=============")
    return True


def start(case_name, *args, **kwargs):
    log = "log----------"
    report_file = "report_file--------"
    common_function.case_steps_run_control(steps_list, __name__, case_name=case_name, log=log, report_file=report_file)

