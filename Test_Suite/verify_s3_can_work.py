import os
import time
import traceback
from Test_Script.ts_power_manager.common_function import PrepareWakeUp, TimeCounter
from Test_Script.ts_power_manager.screensaver import ScreenSaver
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
from Common import picture_operator, common_function, tool, log
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.common_function import new_cases_result, update_cases_result
from Common.picture_operator import capture_screen
import pyautogui
pyautogui.FAILSAFE = False
from PIL import Image

log = log.Logger()


def check_sleep_status():
    power_manager = PowerManagerFactory("AC")
    if not power_manager.AC.open_power_manager_from_control_panel():
        log.info('try to open power manager again')
        if not power_manager.AC.open_power_manager_from_control_panel():
            return False
    power_manager.AC.switch()
    path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager',
                        'verify_s3_work', 'sleep_disable')
    power_icon = picture_operator.wait_element(path, offset=(10, 10))
    power_manager.AC.close_all_power_manager()
    if power_icon:
        log.warning('system sleep is disable')
        return False
    else:
        return True


def start_counter():
    counter = TimeCounter()
    counter.start()
    return counter


def get_time_gap():
    counter = start_counter()
    return int(counter.get_max_time_gap())


def click_icon(lis):
    log.info('check icon and click')
    path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager', 'verify_s3_work')
    for i in lis:
        power_icon = picture_operator.wait_element(os.path.join(path, i), offset=(20, 10))
        tool.click(power_icon[0][0], power_icon[0][1], 1)


def sleep_desktop():
    log.info('sleep by right click desktop')
    tool.right_click(300, 300, 1)
    # try:
    #     click_icon(['power', 'sleep'])
    # except:
    time.sleep(1)
    pyautogui.press("up", interval=0.5)
    pyautogui.press("enter", interval=0.5)
    pyautogui.press("down", interval=0.5)
    pyautogui.press("enter", interval=0.5)
    pyautogui.press("enter", interval=0.5)
    time.sleep(10)


def sleep_start_menu():
    log.info('sleep by start menu')
    # pyautogui.moveTo(1, 1)
    for _ in range(3):
        time.sleep(3)
        pyautogui.hotkey('ctrl', 'alt', 's')
        path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager', 'verify_s3_work')
        power_icon = picture_operator.wait_element(os.path.join(path, 'power'))
        if power_icon:
            break
    else:
        log.warning("power menu in start not found")
        return False
    # try:
    #     click_icon(['power', 'sleep'])
    # except:
    time.sleep(1)
    pyautogui.press("up", interval=0.5)
    pyautogui.press("right", interval=0.5)
    pyautogui.press("enter", interval=0.5)
    time.sleep(10)


def sleep_method1():
    try:
        log.info('sleep by wait time')
        power_manager = PowerManagerFactory("AC")
        power_manager.AC.open_power_manager_from_control_panel()
        power_manager.AC.switch()
        power_manager.AC.set(pms=pms.AC.Minutes_before_system_sleep, radio="on", text="{}".format('1'))
        with PrepareWakeUp(time=80) as w:
            power_manager.AC.apply()
            w.wait(60)
        to_os = ScreenSaver()
        to_os.resume_lock_screen_by_mouse()
        time_gap = w.get_max_time_gap()
        w.set_max_time_gap(0)
        power_manager.AC.set(pms=pms.AC.Minutes_before_system_sleep, radio="on", text="{}".format('30'))
        power_manager.AC.apply()
        time.sleep(5)
        power_manager.AC.close_all_power_manager()
        return time_gap
    except:
        log.warning(traceback.format_exc())
        return '0'


def sleep_method2(f):
    try:
        with PrepareWakeUp(time=0) as w:
            f()
        to_os = ScreenSaver()
        to_os.resume_lock_screen_by_mouse()
        time_gap = w.get_max_time_gap()
        w.set_max_time_gap(0)
        return time_gap
    except:
        log.warning(traceback.format_exc())
        return '0'


def start(case_name, **kwargs):
    try:
        result_file = os.path.join(common_function.get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(common_function.check_ip_yaml()))
        log.info('Begin to start test {}'.format(case_name))
        new_cases_result(result_file, case_name)
        SwitchThinProMode(switch_to='admin')
        if check_sleep_status():
            steps = {
                'step_name': 'check "Minutes before system sleep"',
                'result': 'Pass',
                'expect': 'enable',
                'actual': 'it is enable',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'check "Minutes before system sleep"',
                'result': 'Fail',
                'expect': 'enable',
                'actual': 'not enable',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
            log.info('{} end'.format(case_name))
            return False
        last_time_gap = int(sleep_method1())
        if last_time_gap > 5:
            steps = {
                'step_name': 'check tc go to sleep after 1 minute',
                'result': 'Pass',
                'expect': 'sleep',
                'actual': 'TC go to sleep',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'check tc go to sleep after 1 minute',
                'result': 'Fail',
                'expect': 'sleep',
                'actual': 'TC not go to sleep',
                'note': 'sleep time: {}'.format(last_time_gap)}
            update_cases_result(result_file, case_name, steps)
            os.system("wmctrl -c 'Control Panel'")
            log.info('{} end'.format(case_name))
            return False
        last_time_gap = int(sleep_method2(sleep_desktop))
        if last_time_gap > 5:
            steps = {
                'step_name': 'check tc go to sleep by desktop',
                'result': 'Pass',
                'expect': 'sleep',
                'actual': 'TC go to sleep',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            error_pic = os.path.join(common_function.get_current_dir(),
                                     r'Test_Report', 'img', '{}+sleep_by_desktop.png'.format(case_name.replace(' ', '_')))
            capture_screen(error_pic)
            steps = {
                'step_name': 'check tc go to sleep by desktop',
                'result': 'Fail',
                'expect': 'sleep',
                'actual': 'TC not go to sleep',
                'note': '{}'.format(error_pic)}
            update_cases_result(result_file, case_name, steps)
            log.info('{} end'.format(case_name))
            return False
        last_time_gap = int(sleep_method2(sleep_start_menu))
        if last_time_gap > 5:
            steps = {
                'step_name': 'check tc go to sleep by start menu',
                'result': 'Pass',
                'expect': 'sleep',
                'actual': 'TC go to sleep',
                'note': 'sleep time: {}'.format(last_time_gap)}
            update_cases_result(result_file, case_name, steps)
        else:
            error_pic = os.path.join(common_function.get_current_dir(),
                                     r'Test_Report', 'img', '{}+sleep_by_start_menu.png'.format(case_name.replace(' ', '_')))
            capture_screen(error_pic)
            steps = {
                'step_name': 'check tc go to sleep by start menu',
                'result': 'Fail',
                'expect': 'sleep',
                'actual': 'TC not go to sleep',
                'note': '{}'.format(error_pic)}
            update_cases_result(result_file, case_name, steps)
            log.info('{} end'.format(case_name))
            return False
        log.info('{} end'.format(case_name))
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                   r'Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_')))
        capture_screen(error_pic)
        os.system("wmctrl -c 'Control Panel'")
        pass

