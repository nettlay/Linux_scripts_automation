import pyautogui
import time
import os
from Common import common_function
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Test_Script.ts_power_manager.power_manager_check import ScreenSaverCheck
from Common.picture_operator import wait_element


class ScreenSave:

    def __init__(self):
        self.log = common_function.log
        self.path = common_function.get_current_dir()
        self.report_path = self.path + '/Test_Report'
        self.img_path = self.report_path + '/img/'
        try:
            if not os.path.exists(self.report_path):
                os.mkdir(self.report_path)
            if not os.path.exists(self.img_path):
                os.mkdir(self.img_path)
        except Exception as e:
            self.log.error(e)

    def switch_user(self, user_mode):
        '''
        :param: user_mode: e.g. 'admin' or 'user'
        '''
        if user_mode == 'admin':
            SwitchThinProMode('admin')
        elif user_mode == 'user':
            SwitchThinProMode('user')
        else:
            self.log.info('invalid user_mode {}'.format(user_mode))

    def wait_pictures(self, pic_folder_name):
        '''
        Wait a desired picture. If exists, return its coordinate.
        :param pic_folder_name: folder name of pictures. e.g. 'right_down_corner'
        :return: tuple of coordinate. e.g. ()
        '''
        pic_folder = self.path + '/Test_Data/td_power_manager/PowerManager/ScreenSaver/{}'.format(pic_folder_name)
        result = wait_element(pic_folder)
        if result:
            return result[0]
        else:
            self.log.info('Not found {} picture.'.format(pic_folder_name))
            return False

    def open_screensaver_menu(self):
        pyautogui.hotkey('ctrl', 'alt', 's')
        time.sleep(1)
        pyautogui.typewrite('power manager', interval=0.25)
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(1)
        result = self.wait_pictures('screensaver_menu')
        if result:
            pyautogui.click(result[0], result[1])
            self.log.info('Open power menu successfully.')
            return True
        else:
            return False

    def apply_and_save(self):
        apply = self.wait_pictures('apply')
        if apply:
            pyautogui.click(apply[0], apply[1])
            self.log.info('Apply and save successfully.')
        else:
            self.log.info('Fail to find Apply button picture.')
            return False

    def close_window(self):
        self.log.info('Begin to close window.')
        pyautogui.hotkey('ctrl', 'alt', 'f4')
        time.sleep(1)

    def restore_default_settings(self):
        if not self.open_screensaver_menu():
            self.log.info('Fail to open screensaver menu')
            return False
        scr_saver_check = ScreenSaverCheck()
        ss = scr_saver_check.enable_SS_checked
        if not ss:
            ss_pic = self.wait_pictures('2')
            if not ss_pic:
                self.log.debug('Fail to find enable screensaver and screen lock picture.', self.img_path +
                               'fail_find_enable_screensaver_and_screen_lock.png')
                return False
            pyautogui.click(ss_pic[0], ss_pic[1])
            time.sleep(1)
            pyautogui.press('tab', presses=2, interval=0.5)
        else:
            pyautogui.press('tab', presses=6, interval=0.5)
        time.sleep(1)
        pyautogui.typewrite('10')
        self.apply_and_save()
        self.close_window()


def start(case_name, **kwargs):
    report_file = os.path.join(common_function.get_current_dir(), "Test_Report", "{}.yaml".format(common_function.check_ip_yaml()))
    common_function.new_cases_result(report_file, case_name)  # new report
    pyautogui.moveTo(1, 1)  # Move cursor in case it's at the corner of screen and PyAutuGui fail-safe is triggered
    time.sleep(1)
    saver = ScreenSave()
    saver.switch_user('admin')
    if not saver.open_screensaver_menu():
        return False
    scr_saver_check = ScreenSaverCheck()
    ss = scr_saver_check.enable_SS_checked
    if not ss:
        enable_saver = saver.wait_pictures('2')
        pyautogui.click(enable_saver[0], enable_saver[1])
        pyautogui.press('tab', presses=2, interval=0.5)
    else:
        pyautogui.press('tab', presses=6, interval=0.5)
    pyautogui.typewrite('1')
    time.sleep(1)
    enable_saver = saver.wait_pictures('2')
    if enable_saver:
        pyautogui.click(enable_saver[0], enable_saver[1])
    else:
        return False
    saver.apply_and_save()
    saver.close_window()
    time.sleep(65)
    pyautogui.click()
    time.sleep(1)
    unlock_dialog_folder = saver.path + '/Test_Data/td_power_manager/ScreenSaver/_lock_screen'
    unlock_dialog = wait_element(unlock_dialog_folder)
    if unlock_dialog:
        step = {'step_name': 'Check whether screensaver is activated or not',
                 'result': 'Fail',
                 'expect': 'Screensaver should not be activated after 1 min.',
                 'actual': 'Screensaver is activated after 1 min.',
                 'note': 'none'}
        pyautogui.typewrite('1')
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(1)
    else:
        step = {'step_name': 'Check whether screensaver is activated or not',
                 'result': 'Pass',
                 'expect': 'Screensaver should not be activated after 1 min.',
                 'actual': 'Screensaver is not activated after 1 min.',
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step)
    saver.restore_default_settings()

