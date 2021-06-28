import os
import time
import traceback
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
from Test_Script.ts_power_manager.screensaver import ScreenSaver
from Common import common_function, log, tool
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.picture_operator import capture_screen, wait_element

log = log.Logger()


def select_system_image():
    log.info('select custom screensaver image image file diretory to the system image mode')
    path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager',
                        'verify_screensaver_works_in_system_image_mode', 'open')
    pic_list = common_function.get_folder_items(path, file_only=True)
    for i in pic_list:
        time.sleep(1)
        icon_location = wait_element(os.path.join(path, i))
        if icon_location:
            tool.click(icon_location[0][0], icon_location[0][1], 1)


def rm_pic():
    os.system("rm /home/user/Images/*.png")
    os.system("rm /home/user/*.png")
    os.system("rm /media/*.png")
    os.system("rm /home/user/Images/*.jpg")
    os.system("rm /home/user/*.jpg")
    os.system("rm /media/*.jpg")


def set_system_image(power_m):
    log.info('set the screensaver image to custom image')
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Minutes_before_automatic_Screensaver_activation, radio="on", text="2")
    # rm_pic()
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Custom_image, selected=pms.ScreenSaver.Select.System_images,
                            pic_path='')
    select_system_image()
    time.sleep(2)
    power_m.ScreenSaver.apply()
    time.sleep(5)


def get_default_value():
    log.info('get the default value before start setting')
    enablescreensaver = os.popen("mclient --quiet get root/screensaver/enableScreensaver").read().strip()
    timeoutscreensaver = os.popen("mclient --quiet get root/screensaver/timeoutScreensaver").read().strip()
    customlogo = os.popen("mclient --quiet get root/screensaver/enableCustomLogo").read().strip()
    logopath = os.popen("mclient --quiet get root/screensaver/logoPath").read().strip()
    return [enablescreensaver, timeoutscreensaver, customlogo, logopath]


def check_icon(name):
    log.info('check the picture {}'.format(name))
    path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager',
                        'verify_screensaver_works_in_system_image_mode', '{}'.format(name))
    if os.path.exists(path):
        if wait_element(path):
            return True


def check_changed(name):
    log.info('check the screensaver activation {}'.format(name))
    a = check_icon(name)
    return a


def locked_wake_up():
    log.info('wake up tc')
    screen_saver = ScreenSaver()
    screen_saver.resume_lock_screen_by_mouse()


def reset_all_settings(lis):
    locked_wake_up()
    time.sleep(2)
    power_m = PowerManagerFactory("ScreenSaver")
    power_m.ScreenSaver.open_power_manager_from_control_panel()
    power_m.ScreenSaver.switch()
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Minutes_before_automatic_Screensaver_activation, radio="on", text=lis[1])
    power_m.ScreenSaver.apply()
    time.sleep(5)
    power_m.ScreenSaver.close_all_power_manager()
    if lis:
        log.info('reset all settings in the end')
        os.system("mclient --quiet set root/screensaver/enableScreensaver {}".format(lis[0]))
        os.system("mclient --quiet set root/screensaver/enableCustomLogo {}".format(lis[2]))
        os.system("mclient --quiet set root/screensaver/logoPath {}".format(lis[3]))
        os.system("mclient commit")


def step1(case_name):
    try:
        power_m = PowerManagerFactory("ScreenSaver")
        power_m.ScreenSaver.open_power_manager_from_control_panel()
        power_m.ScreenSaver.switch()
        before = check_changed('activation')
        set_system_image(power_m)
        time.sleep(5)
        after = check_changed('activation1')
        power_m.ScreenSaver.close_all_power_manager()
        if before and after:
            return True
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        return []


def step2(case_name):
    try:
        return check_icon('default')
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        return


def start(case_name, **kwargs):
    log.info('Begin to start test {}'.format(case_name))
    a = get_default_value()
    try:
        result_file = os.path.join(common_function.get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(common_function.check_ip_yaml()))
        common_function.new_cases_result(result_file, case_name)
        if not SwitchThinProMode(switch_to='admin'):
            SwitchThinProMode(switch_to='admin')
        if step1(case_name):
            steps = {
                'step_name': "verify settings can be changed",
                'result': 'Pass',
                'expect': 'can',
                'actual': 'can',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': "verify settings can be changed",
                'result': 'Fail',
                'expect': 'can',
                'actual': 'can not',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
            reset_all_settings(a)
            return False
        time.sleep(121)
        if step2(case_name):
            steps = {
                'step_name': "verify after 2 minutes the screensaver can work well",
                'result': 'Pass',
                'expect': 'success',
                'actual': 'success',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': "verify after 2 minutes the screensaver can work well",
                'result': 'Fail',
                'expect': 'success',
                'actual': 'fail',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
            reset_all_settings(a)
            return False
        reset_all_settings(a)
        log.info('{} is end'.format(case_name))
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        reset_all_settings(a)
        pass
