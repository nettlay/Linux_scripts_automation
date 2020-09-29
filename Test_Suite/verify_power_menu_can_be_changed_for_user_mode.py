from Common import common_function
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.tool import *
import pyautogui
import time
from Test_Script.ts_power_manager.power_manager_check import PowerMenuCheck


class PowerMenuChange:

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
        self.menu_folder_dict = {'menu_show': '1',
                                 'submenu_logout': '2',
                                 'submenu_poweroff': '3',
                                 'submenu_reboot': '4',
                                 'submenu_sleep': '5'}

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

    def open_power_menu(self):
        pyautogui.hotkey('ctrl', 'alt', 's')
        time.sleep(1)
        pyautogui.typewrite('power manager', interval=0.25)
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(1)
        result = self.wait_pictures('power_menu')
        if result:
            pyautogui.click(result[0], result[1])
            self.log.info('Open power menu successfully.')
            return True
        else:
            return False

    def check_power_menu_default(self):
        power_menu_default = PowerMenuCheck()
        pm = power_menu_default.show_PM_checked
        logout = power_menu_default.show_logout_checked
        poweroff = power_menu_default.show_poweroff_checked
        reboot = power_menu_default.show_reboot_checked
        sleep = power_menu_default.show_sleep_checked
        if all([pm, logout, poweroff, reboot, sleep]):
            self.log.info('Power menu is set by default. All checkboxes are checked.')
            return True
        else:
            self.log.info('Power menu is not set by default')
            return False

    def menu_items(self, menu_name_short):
        folder = self.menu_folder_dict[menu_name_short]
        pic_folder = self.path + r'/Test_Data/td_power_manager/PowerManager/PowerMenu/{}'.format(folder)
        result = wait_element(pic_folder)
        if result:
            return result[0]
        else:
            self.log.info('Not found {} item.'.format(menu_name_short))
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

    def wait_pictures(self, pic_folder_name):
        '''
        Wait a desired picture. If exists, return its coordinate.
        :param pic_folder_name: folder name of pictures. e.g. 'right_down_corner'
        :return: tuple of coordinate. e.g. ()
        '''
        pic_folder = self.path + '/Test_Data/td_power_manager/PowerManager/PowerMenu/{}'.format(pic_folder_name)
        result = wait_element(pic_folder)
        if result:
            return result[0]
        else:
            self.log.info('Not found {} picture.'.format(pic_folder_name))
            return False

    @staticmethod
    def right_click_desktop():
        w, h = pyautogui.size()
        pyautogui.rightClick(w - 200, h - 200)

    def click_power_menu_show_checkbox(self):
        flag = True
        self.switch_user('admin')
        self.open_power_menu()
        time.sleep(1)
        menu_show = self.menu_items('menu_show')
        if menu_show:
            pyautogui.click(menu_show[0], menu_show[1])
            self.apply_and_save()
            # Check setting is successful TBD.
            self.log.info('Click power menu show checkbox successfully.')
        else:
            self.log.info('Fail to find menu_show item.')
            flag = False
        # Close window TBD
        self.close_window()
        return flag

    def click_power_sub_menu_checkbox(self):
        self.switch_user('admin')
        self.open_power_menu()
        time.sleep(1)
        for item in self.menu_folder_dict.items():
            if item[0] == 'menu_show':
                continue
            submenu = self.menu_items(item[0])
            if submenu:
                pyautogui.click(submenu[0], submenu[1])
                self.log.info('Click(check/uncheck) {} successfully.'.format(item[0]))
            else:
                self.log.info('Click(check/uncheck) {} failed.'.format(item[0]))
        # verify all the submenus unchecked TBD.
        self.apply_and_save()
        # Check setting is successful TBD.
        self.log.info('Click power menu show checkbox successfully.')
        # close window TBD
        self.close_window()

    def check_power_option_in_desktop_and_start_menu(self, user_mode, power_option_desktop, power_option_start, postfix):
        self.switch_user(user_mode)
        self.right_click_desktop()
        time.sleep(1)
        power_desktop = self.wait_pictures(power_option_desktop)
        if not power_desktop:
            pyautogui.screenshot(self.img_path + 'power_option_desktop_{}.png'.format(postfix))
            time.sleep(1)
        pyautogui.hotkey('esc')
        pyautogui.sleep(1)
        pyautogui.hotkey('ctrl', 'alt', 's')
        pyautogui.sleep(1)
        power_start = self.wait_pictures(power_option_start)
        if not power_start:
            pyautogui.screenshot(self.img_path + 'power_option_start_{}.png'.format(postfix))
            time.sleep(1)
        time.sleep(1)
        pyautogui.press('esc')
        time.sleep(1)
        return power_desktop, power_start

    def check_result(self, user_mode, power_option_desktop, power_option_start, postfix):
        power_desktop, power_start = self.check_power_option_in_desktop_and_start_menu(user_mode, power_option_desktop
                                                                                       , power_option_start, postfix)
        if power_desktop and power_start:
            step = {'step_name': 'Check power option in desktop and Start menu for {}'.format(user_mode),
                    'result': 'Pass',
                    'expect': '{} and {}.'.format(power_option_desktop, power_option_start),
                    'actual': '{} and {}.'.format(power_option_desktop, power_option_start),
                    'note': 'none'}
        else:
            step = {'step_name': 'Check power option in desktop and Start menu for {}'.format(user_mode),
                    'result': 'Fail',
                    'expect': '{} and {}.'.format(power_option_desktop, power_option_start),
                    'actual': 'Not {0} or not {1}. Desktop result: {2}, Start menu result: {3}'.format(power_option_desktop, power_option_start, power_desktop, power_start),
                    'note': 'power_option_desktop_{}.png, power_option_start_{}.png'.format(postfix, postfix)}
        return step

    def check_power_menu_in_desktop_and_start_menu(self, user_mode, postfix):
        self.switch_user(user_mode)
        self.right_click_desktop()
        time.sleep(1)
        power_desktop = self.wait_pictures('power_option_desktop')
        if power_desktop:
            pyautogui.click(power_desktop[0], power_desktop[1])
            pyautogui.sleep(1)
            power_menu_desktop = self.wait_pictures('power_menu_desktop')
            if not power_menu_desktop:
                pyautogui.screenshot(self.img_path + 'power_menu_desktop_{}.png'.format(postfix))
                time.sleep(1)
            pyautogui.press('esc', presses=2, interval=0.5)
            pyautogui.sleep(1)
        else:
            pyautogui.screenshot(self.img_path + 'power_option_desktop_{}.png'.format(postfix))
            time.sleep(1)
            self.log.info('Fail to find power option in desktop.')
            power_menu_desktop = False
        pyautogui.hotkey('ctrl', 'alt', 's')
        pyautogui.sleep(1)
        power_option_start = self.wait_pictures('power_option_start')
        if power_option_start:
            pyautogui.click(power_option_start[0], power_option_start[1])
            time.sleep(1)
            power_menu_start = self.wait_pictures('power_menu_start')
            if not power_menu_start:
                pyautogui.screenshot(self.img_path + 'power_menu_start_{}.png'.format(postfix))
                time.sleep(1)
            time.sleep(1)
        else:
            pyautogui.screenshot(self.img_path + 'power_option_start_{}.png'.format(postfix))
            time.sleep(1)
            self.log.info('Fail to find power option in Start menu.')
            power_menu_start = False
        pyautogui.press('esc')
        return power_menu_desktop, power_menu_start


def start(case_name, **kwargs):
    resolution = pyautogui.size()
    common_function.log.info(resolution)
    report_file = os.path.join(common_function.get_current_dir(), "Test_Report", "{}.yaml".format(common_function.check_ip_yaml()))
    common_function.new_cases_result(report_file, case_name)  # new report
    power_menu = PowerMenuChange()
    log = power_menu.log
    img_path = power_menu.img_path
    pyautogui.moveTo(1, 1)  # Move cursor in case it's at the corner of screen and PyAutuGui fail-safe is triggered
    time.sleep(1)
    power_menu.switch_user('admin')
    power_menu.open_power_menu()
    default = power_menu.check_power_menu_default()
    if default:
        step1 = {'step_name': 'Check power menu default values',
                 'result': 'Pass',
                 'expect': 'Power menu is set by default. All checkboxes are checked.',
                 'actual': 'Power menu is set by default. All checkboxes are checked.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step1)
    else:
        pyautogui.screenshot(img_path + 'power_menu_default.png')
        time.sleep(1)
        step1 = {'step_name': 'Check power menu default values',
                 'result': 'Fail',
                 'expect': 'Power menu is set by default. All checkboxes are checked.',
                 'actual': 'Power menu is not set by default.',
                 'note': 'power_menu_default.png'}
        common_function.update_cases_result(report_file, case_name, step1)
        power_menu.close_window()
        return False
    power_menu.close_window()
    log.info('finish step1')
    step2 = power_menu.check_result('admin', 'power_option_desktop', 'power_option_start', 'step2')
    common_function.update_cases_result(report_file, case_name, step2)
    # if not step2['result']:
    #     return False
    # if step2['result'].upper() == 'FAIL':
    #     return False
    log.info('finish step2')
    # Disable power menu show for regular user
    power_menu.click_power_menu_show_checkbox()
    step3 = power_menu.check_result('user', 'no_power_option_desktop', 'no_power_option_start', 'step3')
    common_function.update_cases_result(report_file, case_name, step3)
    # if not step3['result']:
    #     return False
    # if step3['result'].upper() == 'FAIL':
    #     return False
    log.info('finish step3')
    step4 = power_menu.check_result('admin', 'power_option_desktop', 'power_option_start', 'step4')
    common_function.update_cases_result(report_file, case_name, step4)
    # if not step4['result']:
    #     return False
    # if step4['result'].upper() == 'FAIL':
    #     return False
    log.info('finish step4')
    # Enable power menu show but disable sub menus
    power_menu.click_power_menu_show_checkbox()
    power_menu.click_power_sub_menu_checkbox()
    step5 = power_menu.check_result('user', 'no_power_option_desktop', 'no_power_option_start', 'step5')
    common_function.update_cases_result(report_file, case_name, step5)
    # if not step5['result']:
    #     return False
    # if step5['result'].upper() == 'FAIL':
    #     return False
    step6 = power_menu.check_result('admin', 'power_option_desktop', 'power_option_start', 'step6')
    common_function.update_cases_result(report_file, case_name, step6)
    # if not step6['result']:
    #     return False
    # if step6['result'].upper() == 'FAIL':
    #     return False
    log.info('finish step5, step6')
    # Enable sub menus
    power_menu.click_power_sub_menu_checkbox()
    step7 = power_menu.check_result('user', 'power_option_desktop', 'power_option_start', 'step7')
    common_function.update_cases_result(report_file, case_name, step7)
    # if not step7['result']:
    #     return False
    # if step7['result'].upper() == 'FAIL':
    #     return False
    log.info('finish step 7')
    # Check power option sub menus
    power_m_desktop, power_m_start = power_menu.check_power_menu_in_desktop_and_start_menu('user', 'step8')
    if power_m_desktop and power_m_start:
        step8 = {'step_name': 'Check power menu in desktop and Start menu for user',
                 'result': 'Pass',
                 'expect': 'Power menu should exist in desktop and Start menu.',
                 'actual': 'Power menu should exist in desktop and Start menu.',
                 'note': 'none'}
    else:
        step8 = {'step_name': 'Check power menu in desktop and Start menu for user',
                 'result': 'Fail',
                 'expect': 'Power menu should exist in desktop and Start menu.',
                 'actual': 'No power menu exists in desktop or Start menu. Desktop result: {0}, Start menu result: '
                           '{1}'.format(power_m_desktop, power_m_start),
                 'note': 'power_menu_desktop_step8.png, power_menu_start_step8.png'}
    common_function.update_cases_result(report_file, case_name, step8)
    log.info('finish step 8')




