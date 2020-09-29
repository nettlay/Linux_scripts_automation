import os
import time
import traceback
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
from Test_Script.ts_power_manager.screensaver import ScreenSaver
from Test_Script.ts_power_manager.common_function import linux_check_locked, PrepareWakeUp
from Common import common_function, log, picture_operator, tool
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.picture_operator import capture_screen
from Test_Script.ts_power_manager.common_function import WebConn
from Common.vdi_connection import TelnetLinux
import pyautogui
from Test_Script.ts_power_manager.common_function import set_user_password

path = os.path.join(common_function.get_current_dir(), 'count_time.txt')
log = log.Logger()
steps_list = (
                "step1",
                "step2",
                "step3",
                "step3_res",
                "step4",
                "step5",
                "step5_res",
                "step6"
)


def click_icon(name, **kwargs):
    try:
        n = ''
        count = kwargs.get('count', n)
        path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager',
                            'verify_screen_lock_dialog', '{}'.format(name))
        if count:
            icon_location = picture_operator.wait_element(path, offset=(8, 10))
            print(icon_location)
            if icon_location:
                tool.click(icon_location[0][0], icon_location[0][1], count)
            print('click icon')
        else:
            return picture_operator.wait_element(path)
    except:
        log.warning(traceback.format_exc())
        pass


def lock_screen():
    ScreenSaver.lock_screen_by_hotkey()
    if not linux_check_locked():
        ScreenSaver.lock_screen_by_command()


def unlock_screen(user, password):
    log.info('Try  {}  {}  to unlock screen'.format(user, password))
    if not click_icon('start') and not click_icon('locked_dialog'):
        pyautogui.press('enter')
    if click_icon('error'):
        pyautogui.press('enter')
    if click_icon('user'):
        print('user exist')
        click_icon('user', count=3)
    pyautogui.typewrite(user)
    time.sleep(1)
    pyautogui.press("tab")
    time.sleep(1)
    pyautogui.typewrite(password)
    time.sleep(1)
    pyautogui.press("enter")


def reset_settings(*args, **kwargs):
    if not click_icon('start'):
        unlock_screen('root', '1')
    os.system('hptc-control-panel --term')
    web = WebConn([])
    web.close_web_connection()
    tl = TelnetLinux()
    tl.logoff()
    if os.path.exists(path):
        os.remove(path)
    os.system("mclient --quiet set root/screensaver/lockScreenUser {}".format(0))
    os.system("mclient commit")


def set_user_password1(**kwargs):
    password = kwargs.get("password", "1")
    icon_path = common_function.get_current_dir("Test_Data/td_power_manager/security_user_icon")
    time.sleep(1)
    log.info("Open security desktop")
    # os.popen("hptc-control-panel --config-panel /etc/hptc-control-panel/applications/hptc-security.desktop")
    common_function.open_window("security")
    time.sleep(2)
    res = picture_operator.wait_element(icon_path)
    loc, offset = res
    loc_x, loc_y = loc[0] + offset[1] - 60, loc[1] + int(offset[0] / 2) - 10
    pyautogui.click(loc_x, loc_y)
    time.sleep(1)
    pyautogui.typewrite(password, interval=0.2)
    time.sleep(1)
    pyautogui.hotkey("tab")
    time.sleep(1)
    pyautogui.typewrite(password, interval=0.2)
    time.sleep(1)
    pyautogui.press('enter', presses=2, interval=1)
    os.popen("hptc-control-panel --term")


def step1(*args, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    SwitchThinProMode(switch_to='admin')
    log.info('set user password: 1')
    set_user_password()
    log.info('enable require password for general users')
    power_m = PowerManagerFactory("ScreenSaver")
    power_m.ScreenSaver.open_power_manager_from_control_panel()
    power_m.ScreenSaver.switch()
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_general_users, radio="on")
    click_icon('ok', count=1)
    power_m.ScreenSaver.apply()
    time.sleep(5)
    power_m.ScreenSaver.close_all_power_manager()
    SwitchThinProMode(switch_to='user')
    log.info('start a web connection')
    web = WebConn([])
    web.open_firefox()
    if click_icon('firefox_title'):
        log.info('web connection success')
    lock_screen()
    pyautogui.press('enter')
    if click_icon('locked_dialog'):
        log.info('screen lock dialog shown')
        steps = {
            'step_name': "verify screen lock dialog shown",
            'result': 'Pass',
            'expect': 'show',
            'actual': 'show',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
    else:
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}+step1.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': "verify screen lock dialog shown",
            'result': 'Fail',
            'expect': 'show',
            'actual': 'not show',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
        reset_settings()
        return False


def step2(*args, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    unlock_screen('user', '0')
    a = click_icon('error')
    time.sleep(5)
    unlock_screen('user', '1')
    b = click_icon('error')
    c = click_icon('locked_dialog')
    if a and not b and not c:
        steps = {
            'step_name': "verify screen can be resumed successfully",
            'result': 'Pass',
            'expect': 'success',
            'actual': 'success',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
    else:
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}+step2.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': "verify screen can be resumed successfully",
            'result': 'Fail',
            'expect': 'success',
            'actual': 'fail',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
        unlock_screen('root', '1')
        reset_settings()
        return False


def step3(*args, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    lock_screen()
    time.sleep(2)
    log.info('start reboot the tc by screen lock dialog')
    pyautogui.press('enter')
    click_icon('menu', count=1)
    click_icon('power', count=1)
    click_icon('reboot', count=1)
    cur_time = time.time()
    with open(path, 'a', encoding='utf-8') as f:
        f.write(str(int(cur_time)))
        f.write('\n')
    time.sleep(15)


def step3_res(*args, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    with open(path, 'r', encoding='utf-8') as f:
        file_info = f.readline()
        print(file_info)
    time.sleep(5)
    time_gap = time.time() - float(file_info)
    log.info('tc reboot time is {}'.format(time_gap))
    os.remove(path)
    if time_gap > 5:
        log.info('reboot success')
        steps = {
            'step_name': "verify screen can be unlocked and reboot immediately",
            'result': 'Pass',
            'expect': 'success',
            'actual': 'success',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
    else:
        steps = {
            'step_name': "verify screen can be unlocked and reboot immediately",
            'result': 'Fail',
            'expect': 'success',
            'actual': 'fail',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
        reset_settings()
        return False


def step4(*args, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    SwitchThinProMode(switch_to='user')
    tl = TelnetLinux()
    tl.logon()
    lock_screen()
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(1)
    a = click_icon('locked_dialog')
    if not a:
        log.debug("first check not found locked dialog",
                  common_function.get_current_dir('Test_Report', 'img', '{}_locked_dialog.png'.format(case_name)))
        pyautogui.press('enter')
        time.sleep(1)
        a = click_icon('locked_dialog')
    pyautogui.press('esc')
    time.sleep(1)
    b = click_icon('locked_dialog')
    unlock_screen('root', '1')
    tl.logoff()
    log.info('press esc before {}, press esc after {}'.format(a, b))
    if a and not b:
        steps = {
            'step_name': "verify press esc key will dismiss the dialog",
            'result': 'Pass',
            'expect': 'success',
            'actual': 'success',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
    else:
        steps = {
            'step_name': "verify press esc key will dismiss the dialog",
            'result': 'Fail',
            'expect': 'success',
            'actual': 'fail',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
        reset_settings()
        return False


def step5(*args, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    lock_screen()
    time.sleep(2)
    log.info('start to power off the tc by screen lock dialog')
    with PrepareWakeUp(time=0) as w:
        pyautogui.press('enter')
        click_icon('menu', count=1)
        click_icon('power', count=1)
        click_icon('poweroff', count=1)
        cur_time = time.time()
        with open(path, 'a', encoding='utf-8') as f:
            f.write(str(int(cur_time)))
            f.write('\n')


def step5_res(*args, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    with open(path, 'r', encoding='utf-8') as f:
        file_info = f.readline()
        print(file_info)
    time.sleep(5)
    time_gap = time.time() - float(file_info)
    log.info('tc power off time is {}'.format(time_gap))
    os.remove(path)
    if time_gap > 5:
        log.info('power off success')
        steps = {
            'step_name': "verify screen can be unlocked and shutdown immediately",
            'result': 'Pass',
            'expect': 'success',
            'actual': 'success',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
    else:
        steps = {
            'step_name': "verify screen can be unlocked and shutdown immediately",
            'result': 'Fail',
            'expect': 'success',
            'actual': 'fail',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
        reset_settings()
        return False


def step6(*args, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    lock_screen()
    if linux_check_locked():
        log.info('screen lock success')
        steps = {
            'step_name': "verify screen can be locked successful",
            'result': 'Pass',
            'expect': 'success',
            'actual': 'success',
            'note': ''}
        common_function.update_cases_result(report_file, case_name, steps)
    else:
        pyautogui.press('enter')
        if click_icon('locked'):
            log.info('screen lock success')
            steps = {
                'step_name': "verify screen can be locked successful",
                'result': 'Pass',
                'expect': 'success',
                'actual': 'success',
                'note': ''}
            common_function.update_cases_result(report_file, case_name, steps)
        else:
            log.info('screen lock fail')
            steps = {
                'step_name': "verify screen can be locked successful",
                'result': 'Fail',
                'expect': 'success',
                'actual': 'fail',
                'note': ''}
            common_function.update_cases_result(report_file, case_name, steps)
            reset_settings()
            return False
    unlock_screen('root', '1')


def start(case_name, *args, **kwargs):
    try:
        log.info('Begin to start test {}'.format(case_name))
        result_file = os.path.join(common_function.get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(common_function.check_ip_yaml()))
        common_function.new_cases_result(result_file, case_name)
        common_function.case_steps_run_control(steps_list, __name__, case_name=case_name, log=log,
                                               report_file=result_file)
        reset_settings()
        log.info('test case {} is end'.format(case_name))
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        pass
