import pyautogui
import time
import os
from Common import common_function
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Test_Script.ts_power_manager.power_manager_check import ScreenSaverCheck
from Common.picture_operator import wait_element


class AutomaticScreenSave:

    def __init__(self):
        self.log = common_function.log
        self.path = common_function.get_current_dir()

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
        self.open_screensaver_menu()
        scr_saver_check = ScreenSaverCheck()
        minutes = scr_saver_check.minutes_before_asa_checked
        if not minutes:
            # Enable automatic screensaver activation
            pyautogui.press('tab', presses=5, interval=0.5)
            time.sleep(1)
            pyautogui.hotkey(' ')
            time.sleep(1)
            pyautogui.hotkey('tab')
            time.sleep(1)
        else:
            pyautogui.press('tab', presses=6, interval=0.5)
            time.sleep(1)
        # Reset minutes to default 10
        pyautogui.typewrite('10')
        time.sleep(1)
        self.apply_and_save()
        self.close_window()


def start(case_name, **kwargs):
    report_file = os.path.join(common_function.get_current_dir(), "Test_Report", "{}.yaml".format(common_function.check_ip_yaml()))
    common_function.new_cases_result(report_file, case_name)  # new report
    auto_saver = AutomaticScreenSave()
    auto_saver.switch_user('admin')
    if not auto_saver.open_screensaver_menu():
        return False
    auto_ss = ScreenSaverCheck().minutes_before_asa_checked
    if auto_ss:
        # Disable automatic screensaver activation
        pyautogui.press('tab', presses=5, interval=0.5)
        time.sleep(1)
        pyautogui.hotkey(' ')
        time.sleep(1)
    minutes = auto_saver.wait_pictures('minutes')
    if minutes:
        step1 = {'step_name': 'Check whether screensaver minutes is disabled and changed to 0',
                'result': 'Pass',
                'expect': 'Screensaver minutes should be disabled and changed to 0.',
                'actual': 'Screensaver minutes is disabled and changed to 0.',
                'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step1)
    else:
        step1 = {'step_name': 'Check whether screensaver minutes is disabled and changed to 0',
                'result': 'Fail',
                'expect': 'Screensaver minutes should be disabled and changed to 0.',
                'actual': 'Screensaver minutes is not disabled and changed to 0.',
                'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step1)
        auto_saver.close_window()
        return False
    auto_saver.apply_and_save()
    auto_saver.close_window()
    time.sleep(65)
    pyautogui.click()
    time.sleep(1)
    unlock_dialog_folder = auto_saver.path + '/Test_Data/td_power_manager/ScreenSaver/_lock_screen'
    unlock_dialog = wait_element(unlock_dialog_folder)
    if unlock_dialog:
        step2 = {'step_name': 'Check whether screensaver is activated or not',
                'result': 'Fail',
                'expect': 'Screensaver should not be activated.',
                'actual': 'Screensaver is activated.',
                'note': 'none'}
        pyautogui.typewrite('1')
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(1)
    else:
        step2 = {'step_name': 'Check whether screensaver is activated or not',
                'result': 'Pass',
                'expect': 'Screensaver should not be activated.',
                'actual': 'Screensaver is not activated.',
                'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step2)
    auto_saver.restore_default_settings()
