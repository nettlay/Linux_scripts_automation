import os
import time
import pyautogui
pyautogui.FAILSAFE = False
import subprocess
from Common import common_function, vdi_connection
from Common.file_operator import YamlOperator
from Common.picture_operator import wait_element
from Test_Script.ts_power_manager import screensaver
from Test_Script.ts_power_manager.common_function import set_user_password
from Test_Script.ts_power_manager.common_function import SwitchThinProMode


class ScreenLockPassword:

    def __init__(self):
        self.log = common_function.log
        self.path = common_function.get_current_dir()
        self.scr_save = screensaver.ScreenSaver()
        self.vdi = None
        self.user = ''
        self.rdp_server = ''

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
            return SwitchThinProMode('admin')
        elif user_mode == 'user':
            return SwitchThinProMode('user')
        else:
            self.log.info('invalid user_mode {}'.format(user_mode))
            return False

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

    def create_vdi_rdp(self, step_No):
        for _ in range(6):
            self.user = vdi_connection.MultiUserManger().get_a_available_key()
            if self.user:
                break
            time.sleep(180)
        self.log.info('user: {}'.format(self.user))
        for _ in range(6):
            self.rdp_server = vdi_connection.MultiUserManger().get_a_available_key('rdp win10')
            if self.rdp_server:
                break
            time.sleep(180)
        self.log.info('rdp_server: {}'.format(self.rdp_server))
        setting_file = os.path.join(self.path, "Test_Data", "td_common", "thinpro_registry.yml")
        setting_rdp = YamlOperator(setting_file).read()["set"]["RDP"]
        if step_No == 'step1&2':
            setting = setting_rdp["screen_lock_with_password_step2"]
        elif step_No == 'step3&4':
            setting = setting_rdp["screen_lock_with_password_step3"]
        else:
            setting = '{}'
        self.vdi = vdi_connection.RDPLinux(user=self.user, setting=setting, rdp_server=self.rdp_server)
        return self.vdi, self.user, self.rdp_server

    def connect_vdi_rdp(self):
        connect_result = self.vdi.logon('rdp win10')
        return connect_result

    def logoff_vdi_rdp(self):
        res = subprocess.getoutput("wmctrl -lx | grep -i '{}'".format(self.vdi.grep))
        self.log.info("vdi window:{}".format(res))
        logoff_result = self.vdi.logoff()
        time.sleep(2)
        self.reset_key(self.user, key='user')
        self.reset_key(self.rdp_server, key='rdp win10')
        return logoff_result

    def reset_key(self, user, key):
        self.log.info('start reset user: {}'.format(user))
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
            step = {'step_name': 'Check unlock result for vdi rdp',
                     'result': 'Pass',
                     'expect': 'Unlock vdi rdp successfully.',
                     'actual': 'Unlock vdi rdp successfully.',
                     'note': 'none'}
            common_function.update_cases_result(report_file, case_name, step)
            return True
        else:
            rdp_id = self.vdi.vdi_connection_id('freerdp')[0]
            share_credential = subprocess.getoutput(
                "mclient --quiet get root/ConnectionType/freerdp/connections/{}/SingleSignOn".format(rdp_id))
            step = {'step_name': 'Check unlock result for vdi rdp',
                     'result': 'Fail',
                     'expect': 'Unlock vdi rdp successfully.',
                     'actual': 'Fail to unlock vdi rdp.',
                     'note': 'share credentials with screensaver: {}'.format(share_credential)}
            common_function.update_cases_result(report_file, case_name, step)
            return False

    def step_logoff(self, report_file, case_name):
        if self.logoff_vdi_rdp():
            step = {'step_name': 'Logoff vdi rdp',
                     'result': 'Pass',
                     'expect': 'Logoff vdi rdp successfully.',
                     'actual': 'Logoff vdi rdp successfully.',
                     'note': 'none'}
            common_function.update_cases_result(report_file, case_name, step)
            return True
        else:
            step = {'step_name': 'Logoff vdi rdp',
                     'result': 'Fail',
                     'expect': 'Logoff vdi rdp successfully.',
                     'actual': 'Fail to logoff vdi rdp.',
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
        self.scr_save.set_default_setting()
        self.reset_key(self.user, key='user')
        self.reset_key(self.rdp_server, key='rdp win10')


def start(case_name, **kwargs):
    report_file = os.path.join(common_function.get_current_dir(), "Test_Report", "{}.yaml".format(common_function.
                                                                                                  check_ip_yaml()))
    common_function.new_cases_result(report_file, case_name)  # new report
    scr_lock_passw = ScreenLockPassword()
    log = scr_lock_passw.log
    log.info('-------------Start step 1 & 2-------------------')
    scr_lock_passw.set_screen_saver()
    if not scr_lock_passw.switch_user('user'):
        log.error('switch to user fail')
        return False
    scr_lock_passw.create_vdi_rdp('step1&2')
    for _ in range(2):
        if scr_lock_passw.connect_vdi_rdp() is True:
            break
        log.debug('connect vdi rdp for step 1&2 fail,try again',
                  common_function.get_current_dir("Test_Report", "img", "{}.png".format(case_name.replace(' ', '_'))))
    else:
        step = {'step_name': 'Connect vdi rdp for step 1&2',
                 'result': 'Fail',
                 'expect': 'Vdi rdp should be connected.',
                 'actual': 'Fail to connect vdi rdp.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.restore_default_settings()
        return False
    if not scr_lock_passw.lock_screen(passw=False):
        step = {'step_name': 'Lock screen for step 1&2',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.logoff_vdi_rdp()
        return False
    pyautogui.click()
    time.sleep(2)
    if not scr_lock_passw.step_unlock_result(report_file, case_name):
        log.debug("try to unlock vdi screen",
                  common_function.get_current_dir("Test_Report", "img", "{}.png".format(case_name.replace(' ', '_'))))
        pyautogui.click()
        screen = scr_lock_passw.wait_pictures('_lock_screen')
        if screen:
            passw = scr_lock_passw.vdi_user_info["password"]
            pyautogui.typewrite(passw, interval=0.1)
            pyautogui.press("enter")
            time.sleep(2)
            if screen:
                pyautogui.press("enter")
                time.sleep(1)
                pyautogui.click()
                time.sleep(1)
                pyautogui.press("esc")
                time.sleep(2)
                pyautogui.click()
                time.sleep(2)
                pyautogui.typewrite('1')
                pyautogui.press("enter")
                time.sleep(2)
            scr_lock_passw.logoff_vdi_rdp()
        else:
            scr_lock_passw.logoff_vdi_rdp()
            time.sleep(20)
            pyautogui.click()
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
    time.sleep(2)
    log.info('-------------Start step 3 & 4-------------------')
    scr_lock_passw.create_vdi_rdp('step3&4')
    for _ in range(2):
        if scr_lock_passw.connect_vdi_rdp() is True:
            break
        log.debug('connect vdi rdp for step 3&4 fail,try again',
                  common_function.get_current_dir("Test_Report", "img", "{}.png".format(case_name.replace(' ', '_'))))
    else:
        step = {'step_name': 'Connect vdi rdp for step 3&4',
                 'result': 'Fail',
                 'expect': 'Vdi rdp should be connected.',
                 'actual': 'Fail to connect vdi rdp.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.restore_default_settings()
        return False
    if not scr_lock_passw.lock_screen():
        step = {'step_name': 'Lock screen for step 3&4',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.logoff_vdi_rdp()
        return False
    passw = scr_lock_passw.vdi_user_info["password"]
    pyautogui.typewrite(passw, interval=0.1)
    pyautogui.press("enter")
    time.sleep(2)
    if not scr_lock_passw.step_unlock_result(report_file, case_name):
        scr_lock_passw.logoff_vdi_rdp()
        return False
    if not scr_lock_passw.step_logoff(report_file, case_name):
        scr_lock_passw.logoff_vdi_rdp()
        return False
    step_3_4 = {'step_name': 'Step 3&4: Unlock with connection credentials',
                 'result': 'Pass',
                 'expect': 'Pass.',
                 'actual': 'Pass.',
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step_3_4)
    log.info('-------------Finish step 3 & 4-------------------')
    time.sleep(2)
    log.info('-------------Start step 5 & 6-------------------')
    rdp, user, rdp_server = scr_lock_passw.create_vdi_rdp('step5&6')
    rdp.delete_vdi('freerdp')
    rdp.create_vdi('freerdp')
    time.sleep(1)
    rdp_id = rdp.vdi_connection_id('freerdp')[0]
    dic = {'credentialsType': 'password',
           'domain': 'sh',
           'securityLevel': '0',
           'windowType': 'full',
           'address': rdp_server,
           'SingleSignOn': '1'}
    rdp.set_vdi(rdp_id, dic)
    # rdp.connect_vdi(rdp_id)
    for _ in range(2):
        rdp.connect_vdi_by_pic()
        log.info("Launch RDP Login dialog.")
        time.sleep(5)
        pyautogui.typewrite(user)
        time.sleep(1)
        pyautogui.hotkey('tab')
        time.sleep(1)
        pyautogui.typewrite(passw)
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(10)
        screen = scr_lock_passw.wait_pictures('_win10_start_icon')
        if screen:
            break
        log.debug('connect vdi rdp for step 5&6 fail,try again',
                  common_function.get_current_dir("Test_Report", "img", "{}.png".format(case_name.replace(' ', '_'))))
    else:
        step = {'step_name': 'Connect vdi rdp for step 5&6',
                 'result': 'Fail',
                 'expect': 'Vdi rdp should be connected.',
                 'actual': 'Fail to connect vdi rdp.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.restore_default_settings()
        return False
    if not scr_lock_passw.lock_screen():
        step = {'step_name': 'Lock screen for step 5&6',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.logoff_vdi_rdp()
        return False
    # pyautogui.hotkey('enter')
    # time.sleep(2)
    # user should not in the list of new credentials
    if not scr_lock_passw.step_check_user_in_credential_list(False, report_file, case_name):
        scr_lock_passw.logoff_vdi_rdp()
        return False
    log.info("Use 'root' to unlock.")
    scr_lock_passw.unlock_with_specified_account('root', '1')

    if not scr_lock_passw.wait_pictures("_invalid_credentials"):  # check invalid credentials dialog
        scr_lock_passw.log.info("Not found invalid credentials dialog")
        scr_lock_passw.logoff_vdi_rdp()
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
        scr_lock_passw.logoff_vdi_rdp()
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
    time.sleep(2)
    log.info('-------------Start step 7 & 8-------------------')
    scr_lock_passw.set_user_password(password='1')
    scr_lock_passw.set_screen_saver(True)
    if not scr_lock_passw.switch_user('user'):
        return False
    if not scr_lock_passw.lock_screen(locked_by='user'):
        step = {'step_name': 'Lock screen by user for step 7&8',
                 'result': 'Fail',
                 'expect': 'Screen should be locked by user.',
                 'actual': 'Fail to lock screen by user.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
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
    scr_lock_passw.create_vdi_rdp('step3&4')
    for _ in range(2):
        if scr_lock_passw.connect_vdi_rdp() is True:
            break
        log.debug('connect vdi rdp for step 9 fail,try again',
                  common_function.get_current_dir("Test_Report", "img", "{}.png".format(case_name.replace(' ', '_'))))
    else:
        step = {'step_name': 'Connect vdi rdp for step 9',
                 'result': 'Fail',
                 'expect': 'Vdi rdp should be connected.',
                 'actual': 'Fail to connect vdi rdp.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    # Unlock with connection credential.
    if not scr_lock_passw.lock_screen():
        step = {'step_name': 'Lock screen step9_1',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.logoff_vdi_rdp()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    # user should in the list of new credentials
    if not scr_lock_passw.step_check_user_in_credential_list(True, report_file, case_name):
        scr_lock_passw.logoff_vdi_rdp()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    pyautogui.typewrite(passw, interval=0.1)
    pyautogui.press("enter")
    time.sleep(2)
    if not scr_lock_passw.step_unlock_result(report_file, case_name):
        scr_lock_passw.logoff_vdi_rdp()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False

    # Unlock with User.
    if not scr_lock_passw.lock_screen():
        step = {'step_name': 'Lock screen step9_2',
                 'result': 'Fail',
                 'expect': 'Screen should be locked.',
                 'actual': 'Fail to lock screen.',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step)
        scr_lock_passw.logoff_vdi_rdp()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    log.info("Use 'user' to unlock.")
    scr_lock_passw.unlock_with_specified_account('user', '1')

    if not scr_lock_passw.step_unlock_result(report_file, case_name):
        scr_lock_passw.logoff_vdi_rdp()
        # restore settings to default
        scr_lock_passw.restore_default_settings()
        return False
    if not scr_lock_passw.step_logoff(report_file, case_name):
        scr_lock_passw.logoff_vdi_rdp()
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
    time.sleep(2)







