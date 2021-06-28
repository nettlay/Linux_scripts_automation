import os
import time
from Common.log import Logger
from Common import common_function as cf
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
from Test_Script.ts_power_manager.screensaver import ScreenSaver
from Common.file_operator import YamlOperator


steps_list = ("setup",
              "set_lock_screen",
              "lock_screen",
              "check_screen_lock",
              "record_result",
              "teardown"
              )


def setup(*args, **kwargs):
    print("setup============")

    case_name = kwargs.get("case_name")
    log = kwargs.get("log")
    report_file = kwargs.get("report_file")

    log.info("{:-^80}".format(" start a case test "))
    log.info("case name:" + case_name)
    cf.new_cases_result(report_file, case_name)                                         # new report file
    time.sleep(0.5)
    return True


def set_lock_screen(*args, **kwargs):
    print("set_lock_screen ========== ")

    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")

    # cf.SwitchThinProMode("user")  # switch to user mode
    # cf.SwitchThinProMode("admin")  # switch to admin mode
    # time.sleep(2)
    # power_manager = PowerManagerFactory("AC", "Battery", "ScreenSaver", "PowerMenu", "LOG")

    # open power manager
    # power_manager.open_power_manager()  # open power manager direct use command
    # power_manager.open_power_manager_from_control_panel()  # open power manager from control panel
    # power_manager.open_power_manager_from_tray()  # open power manager from systray
    #
    # screensaver = ScreenSaver()
    # screensaver.check_default_set()  # check screensaver default set
    #
    # # set power manager
    # power_manager.ScreenSaver.switch()  # switch to screensaver tab
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Timed_System_Lock, radio="on")  # enable timed system lock
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Timed_System_Lock,
    #                               radio="off")  # disable timed system lock
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock,
    #                               radio="on")  # enable timed system lock
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock,
    #                               radio="off")  # disable timed system lock
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Minutes_before_automatic_Screensaver_activation,
    #                               radio="off")  # disable
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Minutes_before_automatic_Screensaver_activation,
    #                               radio="on")  # enable
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Minutes_before_automatic_Screensaver_activation, radio="on",
    #                               text="15")  # enable and set time is 15 minutes
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_domain_users, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_general_users, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_in_Administrator_Mode, radio="on")
    #
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Standard_image, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Image_Mapping, selected=pms.ScreenSaver.Select.SlideShowStretch,
    #                               pic_path=cf.get_current_dir() + r"/Test_Data/td_power_manager/ScreenSaver/_screensaver_picture")
    #
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Custom_image, selected=pms.ScreenSaver.Select.Customized_dictory)
    #
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Standard_image, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Image_Mapping, selected=pms.ScreenSaver.Select.Center)

    step1 = {'step_name': 'step1',
             'result': 'pass',
             'expect': 'set screensaver success',
             'actual': 'set screensaver success',
             'note': 'xxx'}
    cf.update_cases_result(report_file, case_name, step1)  # record test step result

    # screensaver.resume_screensaver_by_keyboard()  # resume and logon
    # screensaver.resume_screensaver_by_mouse()
    #
    # screensaver.reboot_by_screen_lock()  # reboot by screen lock
    # screensaver.power_off_by_screen_lock()
    return True


def lock_screen(*args, **kwargs):
    print("lock_screen========")
    # screensaver = ScreenSaver()
    # screensaver.lock_screen_by_command()
    # screensaver.lock_screen_by_hotkey()  # lock screen by press hotkey "ctrl"+"alt"+"l"
    # screensaver.lock_screen_by_right_click()  # lock screen by right click desktop
    return True


def check_screen_lock(*args, **kwargs):
    print("check_screen_lock==========")
    # screensaver = ScreenSaver()
    # screensaver.linux_check_locked(pic_name)  # default screensaver mode
    # screensaver.linux_check_screen_lock_slideshowstredch  # check screen lock slideshowstredch mode
    # screensaver.linux_check_screen_lock_slideshow
    # screensaver.linux_check_screen_lock_center
    # screensaver.linux_check_screen_lock_expand
    # screensaver.linux_check_screen_lock_stretch
    # screensaver.linux_check_screen_lock_tile
    return True


def record_result(*args, **kwargs):
    print("record_result===========")
    return True


def teardown(*args, **kwargs):
    print("teardown=============")
    log = kwargs.get("log")

    log.info("{:+^80}".format(" this case test over "))
    time.sleep(1)
    return True


def start(case_name, **kwargs):
    log = Logger()
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.get_ip()))

    cf.case_steps_run_control(steps_list, __name__, case_name=case_name, log=log, report_file=report_file)




