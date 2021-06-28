# case name: 06.Verify screen lock with password_XD 7.x Storefront_Win10
import os
import time
import pyautogui
pyautogui.FAILSAFE = False
import traceback
import subprocess
from Common.log import Logger
from Common import common_function as cf
from Common import vdi_connection
from Common.file_operator import YamlOperator
from Common.picture_operator import wait_element
from Test_Script.ts_power_manager.screensaver import ScreenSaver
from Test_Script.ts_power_manager.common_function import set_user_password
from Test_Script.ts_power_manager import common_function as pmcf


def vdi_setting():
    setting_file = os.path.join(cf.get_current_dir(), "Test_Data", "td_common", "thinpro_registry.yml")
    return YamlOperator(setting_file).read()


def vdi_user_info():
    vdi_server = os.path.join(cf.get_current_dir(), "Test_Data", "td_common", "vdi_server_config.yml")
    return YamlOperator(vdi_server).read()


def pic(path):
    return os.path.join(cf.get_current_dir(), "Test_Data", "td_power_manager", "ScreenSaver", "{}".format(path))


def step_1(**kwargs):
    log = kwargs.get("log")
    try:
        screensaver = ScreenSaver()
        screensaver.set_default_setting()
        log.info("set screen saver default success")
        pmcf.SwitchThinProMode("user")
        return True
    except:
        log.error(traceback.format_exc())
        log.error("set screen saver default fail")
        return False


def step_2(**kwargs):
    log = kwargs.get("log")
    case_name = kwargs.get("case_name")
    try:
        pmcf.SwitchThinProMode("user")
        multiuser = vdi_connection.MultiUserManger()
        for _ in range(6):
            user = multiuser.get_a_available_key()
            if user:
                break
            time.sleep(180)
        else:
            log.error("not get a valid user")
            return [False, "not has invalid user"]
        parameters = {'vdi': 'citrix', 'session': 'win10'}
        citrix = vdi_connection.CitrixLinux(user=user,
                                        setting=vdi_setting()["set"]["citrix"]["screen_lock_with_password_step2"],
                                        parameters=parameters)

        for _ in range(2):
            if citrix.logon(parameters.get("session", "")):
                for _ in range(10):
                    time.sleep(10)
                    if wait_element(pic("_win10_start_icon")):
                        break
                else:
                    log.debug("log on vdi fail",
                              cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
                    citrix.logoff()
                    time.sleep(5)
                    continue
                break
        else:
            log.debug("log on vdi fail",
                      cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
            os.system("wmctrl -c 'Citrix Workspace'")
            multiuser.reset_key(user)
            return [False, "log on vdi fail"]
        log.info("logon vdi success")
        screensaver = ScreenSaver()
        screensaver.lock_screen_by_hotkey()
        log.info("lock screen")
        time.sleep(2)
        pyautogui.click()
        time.sleep(2)
        if wait_element(pic("_lock_screen_dialog")):
            log.error("found lock screen dialog")
            citrix.logoff()
            multiuser.reset_key(user)
            return [False, "found lock screen dialog"]
        if wait_element(pic("_win10_start_icon")):
            log.info("unlock screen success")
            citrix.logoff()
            multiuser.reset_key(user)
            return [True, "unlock screen success"]
        log.error("unlock screen fail")
        citrix.logoff()
        multiuser.reset_key(user)
        return [False, "unlock screen fail"]
    except:
        log.error(traceback.format_exc())
        return [False, traceback.format_exc()]


def step_3_4(**kwargs):
    log = kwargs.get("log")
    case_name = kwargs.get("case_name")
    try:
        pmcf.SwitchThinProMode("user")
        multiuser = vdi_connection.MultiUserManger()
        for _ in range(6):
            user = multiuser.get_a_available_key()
            if user:
                break
            time.sleep(180)
        else:
            log.error("not get a valid user")
            return [False, "not has invalid user"]
        parameters = {'vdi': 'citrix', 'session': 'win10'}
        citrix = vdi_connection.CitrixLinux(user=user,
                                         setting=vdi_setting()["set"]["citrix"]["screen_lock_with_password_step3"],
                                         parameters=parameters)

        for _ in range(2):
            if citrix.logon(parameters.get("session", "")):
                for _ in range(10):
                    time.sleep(10)
                    if wait_element(pic("_win10_start_icon")):
                        break
                else:
                    log.debug("log on vdi fail",
                              cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
                    citrix.logoff()
                    time.sleep(5)
                    continue
                break
        else:
            log.debug("log on vdi fail",
                      cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
            multiuser.reset_key(user)
            return [False, "log on vdi fail"]
        log.info("logon vdi success")
        screensaver = ScreenSaver()
        screensaver.lock_screen_by_hotkey()
        time.sleep(2)
        pyautogui.click()
        time.sleep(2)

        if not wait_element(pic("_vdi_lock_screen_dialog")):
            log.error("not found screen lock by 'sh autotest'")
            log.debug("not found screen lock by 'sh autotest'",
                      cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
            citrix.logoff()
            multiuser.reset_key(user)
            return [False, "not found screen lock by 'sh autotest'"]

        log.info("found screen lock by 'sh autotest'")
        pyautogui.typewrite(vdi_user_info()["password"], interval=0.1)
        pyautogui.press("enter")
        time.sleep(2)
        if not wait_element(pic("_win10_start_icon")):
            log.error("not into the vdi connection")
            log.debug("not into the vdi connection",
                      cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
            citrix.logoff()
            multiuser.reset_key(user)
            return [False, "not into the vdi connection"]

        log.info("into the vdi connection success")
        citrix.logoff()
        multiuser.reset_key(user)
        return [True, "success"]
    except:
        log.error(traceback.format_exc())
        return [False, traceback.format_exc()]


def step_5_6(**kwargs):
    log = kwargs.get("log")
    session = kwargs.get("session")
    case_name = kwargs.get('case_name')
    root_password = kwargs.get("root_password", "1")
    try:
        pmcf.SwitchThinProMode("user")
        multiuser = vdi_connection.MultiUserManger()
        for _ in range(6):
            user = multiuser.get_a_available_key()
            if user:
                break
            time.sleep(180)
        else:
            log.error("not get a valid user")
            return [False, "not has invalid user"]
        citrix = vdi_connection.CitrixLinux(user=user,
                                            setting=vdi_setting()["set"]["citrix"]["screen_lock_with_password_step5"],
                                            parameters={'vdi': 'citrix', 'session': 'win10'})
        if not citrix.import_cert():
            log.error("thinpro import rootca certificate fail")
            multiuser.reset_key(user)
            return [False, "thinpro import rootca certificate fail"]
        citrix.delete_vdi('xen')
        citrix.create_vdi('xen')
        time.sleep(1)
        citrix_id = citrix.vdi_connection_id('xen')[0]
        citrix.set_citrix_connection_from_yml(citrix_id)

        log.info("connect citrix VDI desktop")
        time.sleep(1)
        # os.popen("connection-mgr start {}".format(citrix_id))
        for _ in range(2):
            citrix.connect_vdi_by_pic()

            time.sleep(10)
            if not wait_element(pic("_citrix_input_credentials_dialog")):
                log.debug("not open input credentials dialog",
                          cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
                os.system("wmctrl -c 'HP - Citrix Server Error'")
                os.system("wmctrl -c 'Citrix Workspace'")
                time.sleep(5)
                continue
            log.info("input domain, user and password")
            pyautogui.typewrite(r"{}\{}".format(vdi_user_info()["domain"], user), interval=0.1)
            pyautogui.press("tab")
            pyautogui.typewrite(vdi_user_info()["password"], interval=0.1)
            pyautogui.press("enter")
            log.info(
                r"user: '{}\{}', password: '{}'".format(vdi_user_info()["domain"], user, vdi_user_info()["password"]))
            time.sleep(20)

            if not wait_element(pic("_citrix_workspace_broker")):
                if wait_element(pic("_win10_start_icon")):             # check whether auto logon vdi desktop
                    log.info("auto logon vdi desktop success")
                    pyautogui.click(1, 1)
                    break
                else:
                    log.debug("open citrix workspace broker fail",
                              cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
                    os.system("wmctrl -c 'HP - Citrix Server Error'")
                    os.system("wmctrl -c 'Citrix Workspace'")
                    time.sleep(5)
                    continue
            else:
                log.info("open citrix workspace broker success")
                if not citrix.logon_desktop_by_pic():
                    log.debug("desktops or target desktop not found",
                              cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name)))
                    os.system("wmctrl -c 'HP - Citrix Server Error'")
                    os.system("wmctrl -c 'Citrix Workspace'")
                    time.sleep(5)
                    continue
                for i in range(15):
                    log.info("wait log on citrix desktop...")
                    time.sleep(10)
                    if wait_element(pic("_win10_start_icon")):
                        log.info("login vdi connection success")
                        break
                    else:
                        continue
                else:
                    log.debug("login vdi connection fail",
                              cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
                    os.system("wmctrl -c 'HP - Citrix Server Error'")
                    os.system("wmctrl -c 'Citrix Workspace'")
                    time.sleep(5)
                    continue
                break
        else:
            os.system("wmctrl -c 'Citrix Workspace'")
            multiuser.reset_key(user)
            return [False, "login vdi connection fail"]

        time.sleep(5)
        screensaver = ScreenSaver()
        screensaver.lock_screen_by_hotkey()               # lock screen
        time.sleep(2)
        pyautogui.press("enter")
        time.sleep(2)
        if not wait_element(pic("_lock_screen_dialog")):
            log.error("not found the lock screen dialog")
            citrix.logoff()
            multiuser.reset_key(user)
            return [False, "not found the lock screen dialog"]
        if wait_element(pic("_user_of_credentials")):      # user in the list of new credentials
            log.error("'user' in credentials dialog")
            citrix.logoff()
            multiuser.reset_key(user)
            return [False, "'user' in credentials dialog"]
        log.info("'user' not in credentials dialog")
        log.info("try use 'root' to unlock")
        if wait_element(pic("_tool")):
            pyautogui.press("tab", presses=5, interval=0.3)
        else:
            pyautogui.press("tab", presses=9, interval=0.3)
        pyautogui.typewrite("root", interval=0.1)
        pyautogui.press("tab")
        pyautogui.typewrite(root_password, interval=0.1)
        pyautogui.press("enter")
        time.sleep(2)

        if not wait_element(pic("_invalid_credentials")):       # check invalid credentials dialog
            log.error("not found invalid credentials dialog")
            citrix.logoff()
            multiuser.reset_key(user)
            return [False, "not found invalid credentials dialog"]
        pyautogui.press("enter")
        cancel = wait_element(pic("_cancel"))
        pyautogui.click(cancel[0])
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(1)
        pyautogui.typewrite(vdi_user_info()["password"], interval=0.1)
        pyautogui.press("enter")
        time.sleep(2)
        if not wait_element(pic("_win10_start_icon")):
            log.error("into the vdi desktop fail")
            citrix.logoff()
            multiuser.reset_key(user)
            return [False, "into the vdi desktop fail"]
        log.info("into the vdi desktop success")
        log.info("screen can be unlock by the credentials")
        citrix.logoff()
        multiuser.reset_key(user)
        return [True, "screen can be unlock by the credentials"]
    except:
        log.info(traceback.format_exc())
        return [False, traceback.format_exc()]


def step_7_8(**kwargs):
    log = kwargs.get("log")
    case_name = kwargs.get("case_name")
    user_password = kwargs.get("user_password", "1")
    try:
        log.info("start set the user password")
        set_user_password(password=user_password)
        os.system("mclient --quiet set root/screensaver/lockScreenUser 1")  # enable require password for general users
        os.system("mclient commit")
        log.info("enable require password for general users")
        pmcf.SwitchThinProMode("user")
        screensaver = ScreenSaver()
        log.info("lock screen")
        screensaver.lock_screen_by_hotkey()                               # lock screen
        time.sleep(2)
        pyautogui.click()
        time.sleep(2)
        if not wait_element(pic("_screen_lock_by_user")):
            log.error("not found the lock screen dialog")
            pyautogui.click()
            return [False, "not found the lock screen dialog"]
        log.info("found the lock screen dialog")
        pyautogui.typewrite(user_password)
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(2)
        if wait_element(pic("_screen_lock_by_user")):
            log.error("unlock fail")
            log.debug("unlock fail",
                      cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
            screensaver.resume_screensaver_by_keyboard()
            pyautogui.screenshot(cf.get_current_dir("Test_Report/screen_lock_citrix_error.png"))
            return [False, "unlock fail"]
        log.info("unlock success")
        return [True, "unlock success"]
    except:
        log.error(traceback.format_exc())
        return [False, traceback.format_exc()]


def step_9(**kwargs):
    log = kwargs.get("log")
    case_name = kwargs.get("case_name")
    user_password = kwargs.get("user_password", "1")
    try:
        pmcf.SwitchThinProMode("user")
        multiuser = vdi_connection.MultiUserManger()
        for _ in range(6):
            user = multiuser.get_a_available_key()
            if user:
                break
            time.sleep(180)
        else:
            log.error("not get a valid user")
            return [False, "not has invalid user"]
        parameters = {'vdi': 'citrix', 'session': 'win10'}
        vdi = vdi_connection.CitrixLinux(user=user,
                                         setting=vdi_setting()["set"]["citrix"]["screen_lock_with_password_step3"],
                                         parameters=parameters)
        for _ in range(2):
            if vdi.logon(parameters.get("session", "")):
                for _ in range(10):
                    time.sleep(10)
                    if wait_element(pic("_win10_start_icon")):
                        break
                else:
                    log.debug("log on vdi fail",
                              cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
                    vdi.logoff()
                    time.sleep(5)
                    continue
                break
        else:
            log.debug("log on vdi fail",
                      cf.get_current_dir('Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_'))))
            multiuser.reset_key(user)
            return [False, "log on vdi fail"]
        log.info("logon vdi success")
        log.info("start lock screen")
        screensaver = ScreenSaver()
        screensaver.lock_screen_by_hotkey()      # lock screen
        time.sleep(2)
        pyautogui.click()
        if not wait_element(pic("_user_of_credentials")):
            log.error("'user' not in credentials list")
            vdi.logoff()
            multiuser.reset_key(user)
            return [False, "'user' not in credentials list"]
        log.info("'user' in credentials list")
        log.info("try use logon vdi password to unlock")
        pyautogui.typewrite(vdi_user_info()["password"], interval=0.1)
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(1)
        if not wait_element(pic("_win10_start_icon")):
            log.error("unlock screen fail")
            vdi.logoff()
            multiuser.reset_key(user)
            return [False, "unlock screen fail"]
        log.info("unlock screen success")

        time.sleep(2)
        screensaver.lock_screen_by_hotkey()
        time.sleep(2)
        pyautogui.click()
        if not wait_element(pic("_user_of_credentials")):
            log.error("'user' not in credentials list")
            vdi.logoff()
            multiuser.reset_key(user)
            return [False, "'user' not in credentials list"]
        log.info("'user' in credentials list")
        log.info("try use 'user' to unlock")

        if wait_element(pic("_tool")):
            pyautogui.press("tab", presses=5, interval=0.3)
        else:
            pyautogui.press("tab", presses=9, interval=0.3)
        pyautogui.typewrite("user", interval=0.1)
        pyautogui.press("tab")
        time.sleep(1)
        pyautogui.typewrite(user_password, interval=0.1)
        time.sleep(1)
        pyautogui.press("enter")
        if not wait_element(pic("_win10_start_icon")):
            log.error("unlock screen fail")
            vdi.logoff()
            multiuser.reset_key(user)
            return [False, "'user' not in credentials list"]
        log.info("unlock screen success")
        log.info("start logoff vdi")
        vdi.logoff()
        multiuser.reset_key(user)
        return [True, "success"]
    except:
        log.error(traceback.format_exc())
        return [False, traceback.format_exc()]


def start(case_name, **kwargs):
    log = Logger()
    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)
    session = "win10"
    root_password = '1'
    user_password = '1'
    time.sleep(0.5)

    log.info(" -------------------------------------------step 1")
    if not step_1(log=log):
        step1_report = {'step_name': 'step1',
                        'result': 'Fail',
                        'expect': 'set screen saver default success',
                        'actual': 'set screen saver default fail',
                        'note': ''}
        cf.update_cases_result(report_file, case_name, step1_report)
        cf.SwitchThinProMode("admin")
        log.error("{:+^80}".format("test case fail"))
        return False
    step1_report = {'step_name': 'step1',
                    'result': 'Pass',
                    'expect': 'set screen saver default and switch to user success',
                    'actual': 'set screen saver default and switch to user success',
                    'note': ''}
    cf.update_cases_result(report_file, case_name, step1_report)

    log.info(" -------------------------------------------step 2")
    result_2 = step_2(log=log, case_name=case_name)
    if not result_2[0]:
        step2_report = {'step_name': 'step2',
                        'result': 'Fail',
                        'expect': 'no need to input any accounts to unlock the screen',
                        'actual': 'fail',
                        'note': '{}'.format(result_2[1])}
        cf.update_cases_result(report_file, case_name, step2_report)
        log.error("{:+^80}".format("test case fail"))
        cf.SwitchThinProMode("admin")
        return False
    step2_report = {'step_name': 'step2',
                    'result': 'pass',
                    'expect': 'no need to input any accounts to unlock the screen',
                    'actual': 'success',
                    'note': '{}'.format(result_2[1])}
    cf.update_cases_result(report_file, case_name, step2_report)

    log.info(" ---------------------------------------------step 3_4")
    result_3_4 = step_3_4(log=log, case_name=case_name)
    if not result_3_4[0]:
        step4_report = {'step_name': 'step 3_4',
                        'result': 'Fail',
                        'expect': 'screen can be unlock by the credentals',
                        'actual': 'fail',
                        'note': '{}'.format(result_3_4[1])}
        cf.update_cases_result(report_file, case_name, step4_report)
        cf.SwitchThinProMode("admin")
        log.error("{:+^80}".format("test case fail"))
        return False
    step4_report = {'step_name': 'step 3_4',
                    'result': 'pass',
                    'expect': 'screen can be unlock by the credentals',
                    'actual': 'success',
                    'note': '{}'.format(result_3_4[1])}
    cf.update_cases_result(report_file, case_name, step4_report)

    log.info(" -------------------------------------------step 5_6")
    result_5_6 = step_5_6(log=log, session=session, root_password=root_password, case_name=case_name)
    if not result_5_6[0]:
        step6_report = {'step_name': 'step 5_6',
                        'result': 'fail',
                        'expect': "'user' is not in the locked accounts, 'root' can not unlock the remote session,"
                                  " screen can be unlock by the credentials",
                        'actual': 'fail',
                        'note': '{}'.format(result_5_6[1])}
        cf.update_cases_result(report_file, case_name, step6_report)
        cf.SwitchThinProMode("admin")
        log.error("{:+^80}".format("test case fail"))
        return False
    step6_report = {'step_name': 'step 5_6',
                    'result': 'pass',
                    'expect': "'user' is not in the locked accounts, 'root' can not unlock the remote session,"
                              " screen can be unlock by the credentials",
                    'actual': 'success',
                    'note': '{}'.format(result_5_6[1])}
    cf.update_cases_result(report_file, case_name, step6_report)

    log.info("-------------------------------------------step 7_8")
    result_7_8 = step_7_8(log=log, user_password=user_password, case_name=case_name)
    if not result_7_8[0]:
        step8_report = {'step_name': 'step 7_8',
                        'result': 'fail',
                        'expect': "'user' account can unlock the screen",
                        'actual': 'fail',
                        'note': '{}'.format(result_7_8[1])}
        cf.update_cases_result(report_file, case_name, step8_report)
        os.system("mclient --quiet set root/screensaver/lockScreenUser 0")  # disable require password for general users
        os.system("mclient commit")
        cf.SwitchThinProMode("admin")
        log.error("{:+^80}".format("test case fail"))
        return False
    step8_report = {'step_name': 'step 7_8',
                    'result': 'pass',
                    'expect': "'user' account can unlock the screen",
                    'actual': 'success',
                    'note': '{}'.format(result_7_8[1])}
    cf.update_cases_result(report_file, case_name, step8_report)

    log.info(" ------------------------------------------- step 9")
    result_9 = step_9(log=log, user_password=user_password, case_name=case_name)
    if not result_9[0]:
        step9_report = {'step_name': 'step9',
                        'result': 'fail',
                        'expect': "both 'user' and the login account can unlock the screen",
                        'actual': 'fail',
                        'note': '{}'.format(result_9[1])}
        cf.update_cases_result(report_file, case_name, step9_report)
        os.system("mclient --quiet set root/screensaver/lockScreenUser 0")  # disable require password for general users
        os.system("mclient commit")
        cf.SwitchThinProMode("admin")
        log.error("{:+^80}".format("test case fail"))
        return False
    step9_report = {'step_name': 'step9',
                    'result': 'pass',
                    'expect': "both 'user' and the login account can unlock the screen",
                    'actual': 'success',
                    'note': '{}'.format(result_9[1])}
    cf.update_cases_result(report_file, case_name, step9_report)

    os.system("mclient --quiet set root/screensaver/lockScreenUser 0")  # disable require password for general users
    os.system("mclient commit")
    log.info("test case pass")
    cf.SwitchThinProMode("admin")
    log.info("{:+^80}".format("this case test over"))
    return True

