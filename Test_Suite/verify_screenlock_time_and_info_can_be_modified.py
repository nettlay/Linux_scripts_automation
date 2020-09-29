from Common import common_function
from Common.tool import *
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Test_Script.ts_power_manager.power_manager_check import ScreenSaverCheck
import pyautogui
import time


class ScreenLock:

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

    def wait_pictures(self, pic_folder_name):
        '''
        Wait a desired picture. If exists, return its coordinate.
        :param pic_folder_name: folder name of pictures. e.g. 'right_down_corner'
        :return: tuple of coordinate. e.g. ()
        '''
        pic_folder = self.path + '/Test_Data/td_power_manager/PowerManager/ScreenLock/{}'.format(pic_folder_name)
        result = wait_element(pic_folder)
        if result:
            return result[0]
        else:
            self.log.info('Not found {} picture.'.format(pic_folder_name))
            return False

    def image_match(self, img, pic_folder_name, offset=(10, 10)):
        """
        Only compare pictures, no capture.
        """
        flag = False
        pic_folder = self.path + '/Test_Data/td_power_manager/PowerManager/ScreenLock/{}'.format(pic_folder_name)
        pic_list = os.listdir(pic_folder)
        for pic in pic_list:
            pic = '{}/{}'.format(pic_folder, pic)
            img_template = cv2.imread(pic)
            t = cv2.matchTemplate(cv2.imread(img), img_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(t)

            if max_val > 0.95:
                x = max_loc[0]
                y = max_loc[1]
                flag = (x + offset[0], y + offset[1]), img_template.shape
                break
            else:
                continue
        return flag

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

    def open_screensaver_menu(self):
        pyautogui.hotkey('ctrl', 'alt', 's')
        time.sleep(1)
        pyautogui.typewrite('power manager', interval=0.25)
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(1)
        result = wait_element(self.path + '/Test_Data/td_power_manager/PowerManager/ScreenSaver/screensaver_menu')
        if result:
            pyautogui.click(result[0][0], result[0][1])
            self.log.info('Open power menu successfully.')
            return True
        else:
            return False

    def close_window(self):
        self.log.info('Begin to close window.')
        pyautogui.hotkey('ctrl', 'alt', 'f4')
        time.sleep(1)

    def enable_timed_system_lock(self):
        if not self.open_screensaver_menu():
            self.log.info('Fail to open screensaver menu.')
        screen_saver = ScreenSaverCheck()
        tsl = screen_saver.enable_TSL_checked
        if tsl:
            self.log.info('Enable Timed System Lock is checked.')
            self.close_window()
            return True
        else:
            pos_tsl = wait_element(self.path + '/Test_Data/td_power_manager/PowerManager/ScreenSaver/1')
            if not pos_tsl:
                self.log.info('Fail to find enable Timed System Lock picture.')
                return False
            pyautogui.click(pos_tsl[0][0], pos_tsl[0][1])
            subprocess.getoutput("wmctrl -c 'Control Panel'")
            time.sleep(1)
            pyautogui.hotkey('enter')
            time.sleep(1)
            return True

    def enable_timed_system_lock_from_reg(self):
        subprocess.getoutput('mclient --quiet set root/screensaver/enableTimedSystemLock 1 && mclient commit')
        time.sleep(1)
        result = subprocess.getoutput('mclient --quiet get root/screensaver/enableTimedSystemLock')
        if result == '1':
            self.log.info('enable_timed_system_lock_from_reg successfully.')
            return True
        else:
            self.log.info('enable_timed_system_lock_from_reg faild.')
            return False

    def set_lockinfo(self, lockinfo):
        subprocess.getoutput('mclient --quiet set root/ScreenLock/lockInfo {} && mclient commit'.format(lockinfo))
        value = subprocess.getoutput('mclient --quiet get root/ScreenLock/lockInfo')
        if value == lockinfo:
            self.log.info('Set lockinfo {} successully.'.format(lockinfo))
            return True

    def set_locktime(self, locktime):
        subprocess.getoutput('mclient --quiet set root/ScreenLock/lockTime {} && mclient commit'.format(locktime))
        value = subprocess.getoutput('mclient --quiet get root/ScreenLock/lockTime')
        if value == locktime:
            self.log.info('Set locktime {} successully.'.format(locktime))
            return True

    def lockinfo_in_dialog(self, step_name=''):
        flag = False
        pyautogui.hotkey('ctrl', 'alt', 'c')
        time.sleep(0.5)
        timed_system_lock_icon = self.wait_pictures('timed_system_lock_icon')
        if timed_system_lock_icon:
            l_info = self.wait_pictures('lockinfo')
            if not l_info:
                self.log.debug('Fail to find lockinfo', self.img_path + 'lockinfo_{}.png'.format(step_name))
            flag = l_info
        else:
            self.log.debug('Fail to go to HP Timed System Lock dialog.', self.img_path + 'timed_system_lock_'
                                                                                         'icon_{}.png'.format(step_name))
        pyautogui.hotkey('ctrl', 'alt', 'u')
        return flag

    def locktime_in_dialog(self, step_name=''):
        flag = False
        pyautogui.hotkey('ctrl', 'alt', 'c')
        time.sleep(0.5)
        pyautogui.screenshot('img.png')
        # timed_system_lock_icon = self.wait_pictures('timed_system_lock_icon')
        timed_system_lock_icon = self.image_match('img.png', 'timed_system_lock_icon')
        if timed_system_lock_icon:
            # l_time = self.wait_pictures('locktime')
            l_time = self.image_match('img.png', 'locktime')
            if not l_time:
                self.log.debug('Fail to find locktime', self.img_path + 'locktime_{}.png'.format(step_name))
            flag = l_time
        else:
            self.log.debug('Fail to go to HP Timed System Lock dialog.', self.img_path + 'timed_system_lock_'
                                                                                         'icon_{}.png'.format(step_name))
        pyautogui.hotkey('ctrl', 'alt', 'u')
        os.remove('img.png')
        return flag

    @staticmethod
    def reboot():
        pyautogui.hotkey('ctrl', 'alt', 's')
        time.sleep(1)
        pyautogui.typewrite('reboot', interval=0.25)
        pyautogui.hotkey('enter')
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(5)


screen_lock = ScreenLock()


def switch_to_admin(**kwargs):
    log = kwargs.get("log")
    log.info('start switch to admin')
    screen_lock.switch_user('admin')


def enable_timed_system_lock(**kwargs):
    log = kwargs.get("log")
    log.info('start enable_timed_system_lock')
    # screen_lock.enable_timed_system_lock()
    screen_lock.enable_timed_system_lock_from_reg()


def set_lockinfo(**kwargs):
    log = kwargs.get("log")
    log.info('start set_lockinfo')
    result = screen_lock.set_lockinfo('test')
    update_case_result(result, 'set_lockinfo', **kwargs)


def check_lockinfo_in_dialog(**kwargs):
    log = kwargs.get("log")
    log.info('start check_lockinfo_in_dialog')
    result = screen_lock.lockinfo_in_dialog(step_name='check_lockinfo_in_dialog')
    if result:
        log.info('check_lockinfo_in_dialog successfully.')
    update_case_result(result, 'check_lockinfo_in_dialog', **kwargs)


def set_locktime(**kwargs):
    log = kwargs.get("log")
    log.info('start set_locktime')
    result = screen_lock.set_locktime('01:00')
    update_case_result(result, 'set_locktime', **kwargs)


def check_locktime_in_dialog(**kwargs):
    log = kwargs.get("log")
    log.info('start check_locktime_in_dialog')
    result = screen_lock.locktime_in_dialog('check_locktime_in_dialog')
    if result:
        log.info('check_locktime_in_dialog successfully.')
    update_case_result(result, 'check_locktime_in_dialog', **kwargs)


def reboot(**kwargs):
    log = kwargs.get("log")
    log.info('start reboot')
    screen_lock.reboot()
    # update_case_result('True', 'reboot', **kwargs)


def check_lockinfo_in_dialog_reboot(**kwargs):
    log = kwargs.get("log")
    log.info('start check_lockinfo_in_dialog_reboot')
    result = screen_lock.lockinfo_in_dialog('check_lockinfo_in_dialog_reboot')
    if result:
        log.info('check_lockinfo_in_dialog_reboot successfully.')
    update_case_result(result, 'check_lockinfo_in_dialog_reboot', **kwargs)


def check_locktime_in_dialog_reboot(**kwargs):
    log = kwargs.get("log")
    log.info('start check_locktime_in_dialog_reboot')
    result = screen_lock.locktime_in_dialog('check_locktime_in_dialog_reboot')
    if result:
        log.info('check_locktime_in_dialog_reboot successfully.')
    update_case_result(result, 'check_locktime_in_dialog_reboot', **kwargs)


def update_case_result(result, step_name, **kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    if result:
        step = {'step_name': step_name,
                'result': 'Pass',
                'expect': '{} successfully.'.format(step_name),
                'actual': '{} successfully.'.format(step_name),
                'note': 'none'}
    else:
        step = {'step_name': step_name,
                'result': 'Fail',
                'expect': '{} successfully.'.format(step_name),
                'actual': '{} failed.'.format(step_name),
                'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step)


def start(case_name, **kwargs):

    report_file = os.path.join(common_function.get_current_dir(), "Test_Report",
                               "{}.yaml".format(common_function.check_ip_yaml()))

    common_function.new_cases_result(report_file, case_name)  # new report

    steps_list = ("switch_to_admin",
                  "enable_timed_system_lock",
                  "set_lockinfo",
                  "check_lockinfo_in_dialog",
                  "set_locktime",
                  "check_locktime_in_dialog",
                  "reboot",
                  "check_lockinfo_in_dialog_reboot",
                  "check_locktime_in_dialog_reboot"
                  )
    pyautogui.moveTo(1, 1)  # Move cursor in case it's at the corner of screen and PyAutuGui fail-safe is triggered
    time.sleep(1)
    common_function.case_steps_run_control(steps_list, __name__, case_name=case_name, log=screen_lock.log,
                                           report_file=report_file)
