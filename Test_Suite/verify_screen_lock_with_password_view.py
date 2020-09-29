import os
import time
import pyautogui
import subprocess
import threading
from Common import common_function, vdi_connection
from Common.file_operator import YamlOperator
from Common.picture_operator import wait_element
from Test_Script.ts_power_manager import screensaver
from Test_Script.ts_power_manager.common_function import SwitchThinProMode


class Reset(threading.Thread):

    def __init__(self, user, wait=10):
        threading.Thread.__init__(self)
        self.user = user
        self.wait = wait
        self.flag = False

    @staticmethod
    def reset_key(user, key):
        vdi_connection.MultiUserManger().reset_key(user, key)

    def run(self):
        time.sleep(self.wait)
        self.reset_key(self.user, key='user')
        self.flag = True


class ScreenLockPassword:

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
        self.scr_save = screensaver.ScreenSaver()
        self.vdi = None
        self.user = ''
        self.view_server = ''
        self.parameters = ''

    @property
    def vdi_user_info(self):
        vdi_server = os.path.join(common_function.get_current_dir(), "Test_Data", "td_common", "vdi_server_config.yml")
        return YamlOperator(vdi_server).read()

    def wait_pictures(self, pic_folder_name):
        '''
        Wait a desired picture. If exists, return its coordinate.
        :param pic_folder_name: folder name of pictures. e.g. 'right_down_corner'
        :return: tuple of coordinate. e.g. ()
        '''
        pic_folder = self.path + '/Test_Data/td_power_manager/ScreenSaver/{}'.format(pic_folder_name)
        result = wait_element(pic_folder)
        if result:
            return result[0]
        else:
            self.log.info('Not found {} picture.'.format(pic_folder_name))
            return False

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

    def set_user_password(self, **kwargs):
        password = kwargs.get("password", "1")
        icon_path = common_function.get_current_dir("Test_Data/td_power_manager/security_user_icon")
        self.switch_user('admin')
        time.sleep(1)
        self.log.info("Open security desktop")
        # os.popen("hptc-control-panel --config-panel /etc/hptc-control-panel/applications/hptc-security.desktop")
        common_function.open_window("security")
        time.sleep(2)
        res = wait_element(icon_path)
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

    def set_screen_saver(self, passw_general_user=False):
        if not passw_general_user:
            self.scr_save.set_default_setting()
        else:
            self.scr_save.set_default_setting()
            subprocess.getoutput("mclient --quiet set root/screensaver/lockScreenUser 1 && mclient commit")

    def create_vdi_view(self, step_No):
        self.user = vdi_connection.MultiUserManger().get_a_available_key()
        self.log.info('user: {}'.format(self.user))
        setting_file = os.path.join(self.path, "Test_Data", "td_common", "thinpro_registry.yml")
        setting_view = YamlOperator(setting_file).read()["set"]["view"]
        if step_No == 'step1&2':
            setting = setting_view["screen_lock_with_password_step2"]
            self.parameters = {'vdi': 'view', 'session': 'pcoip win10'}
        elif step_No == 'step3&4':
            setting = setting_view["screen_lock_with_password_step3"]
            self.parameters = {'vdi': 'view', 'session': 'pcoip win10'}
        else:
            setting = '{}'
            self.parameters = {'vdi': 'view', 'session': 'pcoip win10'}
        self.vdi = vdi_connection.ViewLinux(user=self.user, setting=setting, parameters=self.parameters)
        return self.vdi, self.user

    def connect_vdi_view(self):
        protocol_win10 = self.parameters['session']
        connect_result = self.vdi.logon(protocol_win10)
        return connect_result

    def judge_vdi_connect_UI(self):
        connected = False
        for i in range(3):
            pyautogui.click()
            time.sleep(1)
            pyautogui.screenshot(self.img_path + 'vdi_view_{}.png'.format(i))
            screen = self.wait_pictures('_vdi_view')
            if not screen:
                time.sleep(5)
            else:
                connected = True
                os.remove(self.img_path + 'vdi_view_{}.png'.format(i))
                break
        return connected

    def logoff_vdi_view(self):
        logoff_result = self.vdi.logoff()
        time.sleep(2)
        self.reset_key(self.user, key='user')
        return logoff_result

    @staticmethod
    def reset_key(user, key):
        vdi_connection.MultiUserManger().reset_key(user, key)

    def lock_screen(self, passw=True, locked_by='normal'):
        self.scr_save.lock_screen_by_hotkey()
        self.log.info('Press ctrl+alt+l to lock.')
        time.sleep(3)
        if passw is True:
            pyautogui.click()
            time.sleep(1)
            if locked_by == 'normal':
                screen = self.wait_pictures('_lock_screen')
            else:
                screen = self.wait_pictures('_screen_lock_by_user')
            if screen:
                self.log.info('Lock screen successfully.')
                return True
            else:
                self.log.info('Fail to lock screen.')
                return False
        else:
            return True

    def check_unlock_result(self, unlock_result):
        if unlock_result == 'win10':
            unlock_result = self.wait_pictures('_win10_start_icon')
        else:
            unlock_result = self.wait_pictures('_start_icon')
        if unlock_result:
            self.log.info('Unlock screen successfully.')
            return True
        else:
            self.log.info('Fail to unlock screen.')
            return False

    def step_unlock_result(self, report_file, case_name, unlock_result='win10'):
        if self.check_unlock_result(unlock_result):
            step = {'step_name': 'Check unlock result for vdi view',
                     'result': 'Pass',
                     'expect': 'Unlock vdi view successfully.',
                     'actual': 'Unlock vdi view successfully.',
                     'note': 'none'}
            common_function.update_cases_result(report_file, case_name, step)
            return True
        else:
            step = {'step_name': 'Check unlock result for vdi view',
                     'result': 'Fail',
                     'expect': 'Unlock vdi view successfully.',
                     'actual': 'Fail to unlock vdi view.',
                     'note': 'none'}
            common_function.update_cases_result(report_file, case_name, step)
            return False

    def step_logoff(self, report_file, case_name):
        if self.logoff_vdi_view():
            step = {'step_name': 'Logoff vdi view',
                     'result': 'Pass',
                     'expect': 'Logoff vdi view successfully.',
                     'actual': 'Logoff vdi view successfully.',
                     'note': 'none'}
            common_function.update_cases_result(report_file, case_name, step)
            return True
        else:
            step = {'step_name': 'Logoff vdi view',
                     'result': 'Fail',
                     'expect': 'Logoff vdi view successfully.',
                     'actual': 'Fail to logoff vdi view.',
                     'note': 'none'}
            common_function.update_cases_result(report_file, case_name, step)
            return False

    def step_check_user_in_credential_list(self, in_list, report_file, case_name):
        flag = False
        user_in = self.wait_pictures("_user_of_credentials")
        if user_in and in_list:
            step = {'step_name': 'Check user in credential list',
                    'result': 'Pass',
                    'expect': 'User should be in credential list.',
                    'actual': 'User is in credential list.',
                    'note': 'none'}
            flag = True
        elif not user_in and not in_list:
            step = {'step_name': 'Check user not in credential list',
                    'result': 'Pass',
                    'expect': 'User should not be in credential list.',
                    'actual': 'User is not in credential list.',
                    'note': 'none'}
            flag = True
        else:
            step = {'step_name': 'Check whether user in credential list or not',
                    'result': 'Fail',
                    'expect': '',
                    'actual': 'Fail.',
                    'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        return flag

    def unlock_with_specified_account(self, account, passwd):
        if self.wait_pictures('_tool'):
            pyautogui.press("tab", presses=5, interval=0.3)
        else:
            pyautogui.press("tab", presses=9, interval=0.3)
        pyautogui.typewrite(account, interval=0.1)
        pyautogui.press("tab")
        time.sleep(1)
        pyautogui.typewrite(passwd, interval=0.1)
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(2)

    def restore_default_settings(self):
        subprocess.getoutput('wmctrl -c Server Login')
        subprocess.getoutput('wmctrl -c VMware Horizon Client')
        time.sleep(1)
        self.scr_save.set_default_setting()
        self.switch_user('admin')

    def deal_with_unexpected(self, vdi_user=''):
        if vdi_user == '':
            self.log.info('No available user for vdi connection.')
        else:
            self.reset_key(vdi_user, key='user')
        self.restore_default_settings()


def start(case_name, **kwargs):
    report_file = os.path.join(common_function.get_current_dir(), "Test_Report", "{}.yaml".format(common_function.
                                                                                                  check_ip_yaml()))
    common_function.new_cases_result(report_file, case_name)  # new report
    scr_lock_passw = ScreenLockPassword()
    log = scr_lock_passw.log
    img_path = scr_lock_passw.img_path
    log.info('-------------Start step 1 & 2-------------------')
    scr_lock_passw.set_screen_saver()
    scr_lock_passw.switch_user('user')
    create_result_step1 = scr_lock_passw.create_vdi_view('step1&2')
    if not create_result_step1[1]:
        scr_lock_passw.deal_with_unexpected()
        return False
    connect_step1_2 = scr_lock_passw.connect_vdi_view()
    # pyautogui.screenshot(img_path + 'connect_step1&2.png')
    # time.sleep(1)
    if connect_step1_2 is not True:
        pyautogui.screenshot(img_path + 'judge_connect_fail_step1&2.png')
        time.sleep(5)
        connect_UI = scr_lock_passw.judge_vdi_connect_UI()
        # pyautogui.screenshot(img_path + 'connect_UI_step1&2.png')
        # time.sleep(1)
        if not connect_UI:
            pyautogui.screenshot(img_path + 'judge_fail_connect_UI_step1&2.png')
            time.sleep(1)
            step = {'step_name': 'Connect vdi view for step 1&2',
                     'result': 'Fail',
                     'expect': 'Vdi view should be connected.',
                     'actual': 'Fail to connect vdi view.',
                     'note': 'none'}
            common_function.update_cases_result(report_file, case_name, step)
            scr_lock_passw.deal_with_unexpected(create_result_step1[1])
            return False
    lock_step_1_2 = scr_lock_passw.lock_screen(passw=False)
    if not lock_step_1_2:
        step = {'step_name': 'Lock screen for step 1&2',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        pyautogui.screenshot(img_path + 'fail_lock_screen_step1&2.png')
        time.sleep(1)
        scr_lock_passw.logoff_vdi_view()
        return False
    pyautogui.click()
    time.sleep(2)
    if not scr_lock_passw.step_unlock_result(report_file, case_name):
        scr_lock_passw.logoff_vdi_view()
        return False
    if not scr_lock_passw.step_logoff(report_file, case_name):
        return False
    step_1_2 = {'step_name': 'Step 1&2: Unlock with general user without password',
                 'result': 'Pass',
                 'expect': 'Pass.',
                 'actual': 'Pass.',
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step_1_2)
    log.info('-------------Finish step 1 & 2-------------------')
    time.sleep(10)
    log.info('-------------Start step 3 & 4-------------------')
    create_result_step3 = scr_lock_passw.create_vdi_view('step3&4')
    if not create_result_step3[1]:
        scr_lock_passw.deal_with_unexpected()
        return False
    if scr_lock_passw.connect_vdi_view() is not True:
        step = {'step_name': 'Connect vdi view for step 3&4',
                 'result': 'Fail',
                 'expect': 'Vdi view should be connected.',
                 'actual': 'Fail to connect vdi view.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.deal_with_unexpected(create_result_step3[1])
        return False
    lock_step_3_4 = scr_lock_passw.lock_screen()
    if not lock_step_3_4:
        step = {'step_name': 'Lock screen for step 3&4',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        pyautogui.screenshot(img_path + 'fail_lock_screen_step3&4.png')
        time.sleep(1)
        scr_lock_passw.logoff_vdi_view()
        return False
    passw = scr_lock_passw.vdi_user_info["password"]
    pyautogui.typewrite(passw, interval=0.1)
    pyautogui.press("enter")
    time.sleep(2)
    if not scr_lock_passw.step_unlock_result(report_file, case_name):
        scr_lock_passw.logoff_vdi_view()
        return False
    if not scr_lock_passw.step_logoff(report_file, case_name):
        scr_lock_passw.logoff_vdi_view()
        return False
    step_3_4 = {'step_name': 'Step 3&4: Unlock with connection credentials',
                 'result': 'Pass',
                 'expect': 'Pass.',
                 'actual': 'Pass.',
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step_3_4)
    log.info('-------------Finish step 3 & 4-------------------')
    time.sleep(10)
    log.info('-------------Start step 5 & 6-------------------')
    view, user = scr_lock_passw.create_vdi_view('step5&6')
    if not user:
        step = {'step_name': 'No available user for step 5&6',
                 'result': 'Fail',
                 'expect': 'Available user should be got.',
                 'actual': 'No available user got.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.deal_with_unexpected()
        return False
    view.delete_vdi('view')
    view.create_vdi('view')
    time.sleep(1)
    view_id = view.vdi_connection_id('view')[0]
    dic = {'credentialsType': 'password',
           'domain': 'sh',
           'desktopSize': '"All Monitors"',
           'viewSecurityLevel': '"Allow all connections"',
           'server': 'vnsvr.sh.dto',
           'preferredProtocol': '"PCOIP"',
           'desktop': 'AutoTestW10-P',
           'SingleSignOn': '1'}
    view.set_vdi(view_id, dic)
    view.connect_vdi(view_id)
    log.info("Launch View Login dialog.")
    time.sleep(5)
    pyautogui.typewrite(user)
    time.sleep(1)
    pyautogui.hotkey('tab')
    time.sleep(1)
    pyautogui.typewrite(passw, interval=0.1)
    time.sleep(1)
    pyautogui.hotkey('enter')
    time.sleep(15)
    connected = scr_lock_passw.judge_vdi_connect_UI()
    if not connected:
        step = {'step_name': 'Connect vdi view for step 5&6',
                 'result': 'Fail',
                 'expect': 'Vdi view should be connected.',
                 'actual': 'Fail to connect vdi view.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.deal_with_unexpected(user)
        return False
    time.sleep(10)  # wait some time to login desktop
    lock_step_5_6 = scr_lock_passw.lock_screen()
    if not lock_step_5_6:
        step = {'step_name': 'Lock screen for step 5&6',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        pyautogui.screenshot(img_path + 'fail_lock_screen_step5&6.png')
        time.sleep(1)
        scr_lock_passw.logoff_vdi_view()
        return False
    # user should not in the list of new credentials
    if not scr_lock_passw.step_check_user_in_credential_list(False, report_file, case_name):
        scr_lock_passw.logoff_vdi_view()
        return False
    log.info("Use 'root' to unlock.")
    scr_lock_passw.unlock_with_specified_account('root', '1')

    if not scr_lock_passw.wait_pictures("_invalid_credentials"):  # check invalid credentials dialog
        scr_lock_passw.log.info("Not found invalid credentials dialog")
        scr_lock_passw.logoff_vdi_view()
        return False
    pyautogui.press("enter")
    cancel = scr_lock_passw.wait_pictures("_cancel")
    pyautogui.click(cancel)
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(1)
    pyautogui.typewrite(passw, interval=0.1)
    pyautogui.press("enter")
    time.sleep(2)
    if not scr_lock_passw.step_unlock_result(report_file, case_name):
        scr_lock_passw.logoff_vdi_view()
        return False
    if not scr_lock_passw.step_logoff(report_file, case_name):
        return False
    step_5_6 = {'step_name': 'Step 5&6: Check user in locked account list and unlock with root, connection credentials',
                 'result': 'Pass',
                 'expect': 'Pass.',
                 'actual': 'Pass.',
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step_5_6)
    log.info('-------------Finish step 5 & 6-------------------')
    time.sleep(10)
    log.info('-------------Start step 7 & 8-------------------')
    scr_lock_passw.set_user_password(password='1')
    scr_lock_passw.set_screen_saver(True)
    scr_lock_passw.switch_user('user')
    lock_step_7_8 = scr_lock_passw.lock_screen(locked_by='user')
    if not lock_step_7_8:
        step = {'step_name': 'Lock screen by user for step 7&8',
                 'result': 'Fail',
                 'expect': 'Screen should be locked by user.',
                 'actual': 'Fail to lock screen by user.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        pyautogui.screenshot(img_path + 'fail_lock_screen_step7&8.png')
        time.sleep(1)
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    pyautogui.typewrite('1')
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(2)

    # if not scr_lock_passw.step_unlock_result(report_file, case_name, unlock_result='linux'):
    #     # restore settings to default
    #     scr_lock_passw.restore_default_settings()
    #     return False
    if scr_lock_passw.wait_pictures('_lock_screen'):
        step = {'step_name': 'Unlock screen by user for step 7&8',
                 'result': 'Fail',
                 'expect': 'Screen should be unlocked by user.',
                 'actual': 'Fail to unlock screen by user.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    else:
        step = {'step_name': 'Unlock screen by user for step 7&8',
                 'result': 'Pass',
                 'expect': 'Screen should be unlocked by user.',
                 'actual': 'Unlock screen by user successfully.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
    log.info('-------------Finish step 7 & 8-------------------')
    time.sleep(2)
    log.info('-------------Start step 9-------------------')
    create_result_step9 = scr_lock_passw.create_vdi_view('step3&4')
    if not create_result_step9[1]:
        scr_lock_passw.deal_with_unexpected()
        return False
    if scr_lock_passw.connect_vdi_view() is not True:
        step = {'step_name': 'Connect vdi view for step 9',
                 'result': 'Fail',
                 'expect': 'Vdi view should be connected.',
                 'actual': 'Fail to connect vdi view.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.deal_with_unexpected(create_result_step9[1])
        return False
    # Unlock with connection credential.
    lock_step_91 = scr_lock_passw.lock_screen()
    if not lock_step_91:
        pyautogui.screenshot(img_path + 'judge_screenlock_fail_step9_1.png')
        time.sleep(1)
        step = {'step_name': 'Lock screen step9_1',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'judge_screenlock_fail_step9_1.png'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.logoff_vdi_view()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    # user should in the list of new credentials
    if not scr_lock_passw.step_check_user_in_credential_list(True, report_file, case_name):
        scr_lock_passw.logoff_vdi_view()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    pyautogui.typewrite(passw, interval=0.1)
    pyautogui.press("enter")
    time.sleep(2)
    if not scr_lock_passw.step_unlock_result(report_file, case_name):
        scr_lock_passw.logoff_vdi_view()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False

    # Unlock with User.
    lock_step_92 = scr_lock_passw.lock_screen()
    if not lock_step_92:
        step = {'step_name': 'Lock screen step9_2',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        pyautogui.screenshot(img_path + 'fail_lock_screen_step92.png')
        time.sleep(1)
        scr_lock_passw.logoff_vdi_view()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    # print("Use 'user' to unlock.")
    log.info("Use 'user' to unlock.")
    scr_lock_passw.unlock_with_specified_account('user', '1')

    if not scr_lock_passw.step_unlock_result(report_file, case_name):
        scr_lock_passw.logoff_vdi_view()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    if not scr_lock_passw.step_logoff(report_file, case_name):
        scr_lock_passw.logoff_vdi_view()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    step_9 = {'step_name': 'Step 9: Unlock with connection credentials and user',
                 'result': 'Pass',
                 'expect': 'Pass.',
                 'actual': 'Pass.',
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step_9)
    # restore settings to default
    scr_lock_passw.restore_default_settings()
    log.info('-------------Finish step 9-------------------')
    time.sleep(10)








