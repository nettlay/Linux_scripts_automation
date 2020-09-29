import os
import subprocess
import time
import pyautogui
from Common import common_function
from Common.picture_operator import wait_element
from Test_Script.ts_network import network_setting


class WirelessPriority:

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
        self.wireless = network_setting.Wireless()

    def wait_pictures(self, pic_folder_name):
        '''
        Wait a desired picture. If exists, return its coordinate.
        :param pic_folder_name: folder name of pictures. e.g. 'right_down_corner'
        :return: tuple of coordinate. e.g. ()
        '''
        pic_folder = self.path + '/Test_Data/td_network/wireless/{}'.format(pic_folder_name)
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
        result = False
        if user_mode == 'admin':
            result = common_function.SwitchThinProMode('admin')
        elif user_mode == 'user':
            result = common_function.SwitchThinProMode('user')
        else:
            self.log.info('invalid user_mode {}'.format(user_mode))
        return result

    def open_network_wireless_dialog(self):
        pyautogui.hotkey('ctrl', 'alt', 's')
        time.sleep(1)
        pyautogui.typewrite('network', interval=0.25)
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(1)
        result = self.wait_pictures('_wireless_tab')
        if result:
            pyautogui.click(result[0], result[1])
            self.log.info('open_network_wireless_dialog successfully.')
            return True
        else:
            return False

    def apply_control_panel(self):
        apply = self.wait_pictures('apply')
        if apply:
            pyautogui.click(apply[0], apply[1])
            self.log.info('Apply and save successfully.')
        else:
            self.log.info('Fail to find Apply button picture.')
            return False

    def apply_ok_wireless_profile(self, button):
        if button.upper() == 'APPLY':
            btn_pic = self.wait_pictures('_apply')
        elif button.upper() == 'OK':
            btn_pic = self.wait_pictures('_ok')
        else:
            self.log.info('Invalid button name.')
            return False
        if btn_pic:
            pyautogui.click(btn_pic[0], btn_pic[1])
            self.log.info('Click {} successfully.'.format(button))
        else:
            self.log.info('Fail to find {} button picture.'.format(button))
            return False

    def close_window(self):
        self.log.info('Begin to close window.')
        pyautogui.hotkey('ctrl', 'alt', 'f4')
        time.sleep(1)

    def close_control_panel(self):
        # judge control panel - TBD
        # self.close_window()
        subprocess.getoutput("wmctrl -c 'Control Panel'")
        btn_discard = self.wait_pictures('discard')
        if btn_discard:
            pyautogui.click(btn_discard[0], btn_discard[1])
            time.sleep(1)

    @staticmethod
    def reboot():
        pyautogui.hotkey('ctrl', 'alt', 's')
        time.sleep(1)
        pyautogui.typewrite('reboot', interval=0.25)
        pyautogui.hotkey('enter')
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(5)

    def add_wireless_profiles(self, ssid_lst):
        try:
            for ssid in ssid_lst:
                self.wireless.add(ssid=ssid)
                self.apply_ok_wireless_profile('apply')
                self.apply_ok_wireless_profile('ok')
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def get_wireless_ip(self):
        sys_wlan0_ip = subprocess.getoutput("ifconfig | grep wlan0 -A 1 | grep -i 'inet addr'")
        if not sys_wlan0_ip:
            self.log.info('No wirelss ip get.')
            return False
        wlan0_ip = sys_wlan0_ip.strip().split()[1].split(":")[1]
        self.log.info('Current wireless ip: {}'.format(wlan0_ip))
        if wlan0_ip:
            return True
        else:
            return False

    def check_connected_SSID(self, exp_ssid):
        ssid = self.wireless.now_connected_wireless()
        self.log.info('Current connected ssid: {}'.format(ssid))
        if ssid == exp_ssid:
            time.sleep(5)
            if not self.get_wireless_ip():
                self.log.info('Fail to get wireless ip.')
                return False
            else:
                return True
        else:
            self.log.info('Current ssid is not the expected ssid.')
            return False

    def delete_wireless_profile(self):
        if self.wireless.del_wireless_profile_from_reg():
            return True
        else:
            return False

    def restore_default_settings(self):
        # Delete wireless profile from registry
        self.delete_wireless_profile()
        # Turn on wireless switch
        self.wireless.wired_wireless_switch('on')


wireless_pro = WirelessPriority()


def preparation(**kwargs):
    log = kwargs.get("log")
    log.info('start check_wireless_card')
    wireless_pro.switch_user('admin')
    result = wireless_pro.wireless.check_wireless_card()
    update_case_result(result, 'check_wireless_card', **kwargs)
    if not result:
        wireless_pro.restore_default_settings()
        return False
    del_wireless = wireless_pro.delete_wireless_profile()
    if not del_wireless:
        wireless_pro.restore_default_settings()
        return False
    wireless_pro.wireless.wired_wireless_switch('off')
    time.sleep(1)


def set_wireless(**kwargs):
    log = kwargs.get("log")
    log.info('start open_network_dialog')
    open_result = wireless_pro.open_network_wireless_dialog()
    update_case_result(open_result, 'set_wireless', **kwargs)
    if not open_result:
        pyautogui.screenshot(wireless_pro.img_path + 'open_network_dialog.png')
        time.sleep(1)
        wireless_pro.restore_default_settings()
        return False
    add_result = wireless_pro.add_wireless_profiles(['R1-TC_5G_n', "R1-TC_5G_ac_WPA2P", "R1-Linux-disconnect"])
    update_case_result(add_result, 'set_wireless', **kwargs)
    if not add_result:
        pyautogui.screenshot(wireless_pro.img_path + 'add_wireless_profiles.png')
        time.sleep(1)
        wireless_pro.restore_default_settings()
        return False
    wireless_pro.apply_control_panel()
    wireless_pro.close_window()


def check_connected_wireless(**kwargs):
    log = kwargs.get("log")
    log.info('start check_connected_wireless')
    result = wireless_pro.check_connected_SSID('R1-Linux-disconnect')
    update_case_result(result, 'check_connected_wireless', **kwargs)
    if not result:
        log.info('Debug scanning R1-Linux-disconnect')
        wireless_pro.wireless.scan_wireless('R1-Linux-disconnect')
        wireless_pro.restore_default_settings()
        return False


def move_up_ssid(**kwargs):
    log = kwargs.get("log")
    log.info('start move_up_ssid')
    open_result = wireless_pro.open_network_wireless_dialog()
    update_case_result(open_result, 'move_up_ssid', **kwargs)
    if not open_result:
        pyautogui.screenshot(wireless_pro.img_path + 'open_network_dialog_failed_in_move_up_ssid.png')
        time.sleep(1)
        wireless_pro.restore_default_settings()
        return False
    for i in range(2):
        pic = wireless_pro.wait_pictures('ssid_3')
        if not pic:
            pyautogui.screenshot(wireless_pro.img_path + 'wait_ssid_3.png')
            time.sleep(1)
            wireless_pro.restore_default_settings()
            return False
        pyautogui.rightClick(pic[0], pic[1])
        time.sleep(1)
        pic2 = wireless_pro.wait_pictures('move_up')
        if not pic2:
            pyautogui.screenshot(wireless_pro.img_path + 'wait_moveup.png')
            time.sleep(1)
            wireless_pro.restore_default_settings()
            return False
        pyautogui.click(pic2[0], pic2[1])
        time.sleep(1)
        log.info('Move up {} time.'.format(i+1))
    wireless_pro.apply_control_panel()
    wireless_pro.close_window()


def reboot(**kwargs):
    log = kwargs.get("log")
    log.info('start reboot')
    wireless_pro.reboot()


def check_connected_wireless_reboot(**kwargs):
    log = kwargs.get("log")
    log.info('start check_connected_wireless_reboot')
    result = wireless_pro.check_connected_SSID('R1-TC_5G_n')
    update_case_result(result, 'check_connected_wireless_reboot', **kwargs)
    if not result:
        wireless_pro.restore_default_settings()
        return False


def restore_environment(**kwargs):
    log = kwargs.get("log")
    log.info('start restore_environment')
    wireless_pro.restore_default_settings()


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

    steps_list = ("preparation",
                  "set_wireless",
                  "check_connected_wireless",
                  "move_up_ssid",
                  "reboot",
                  "check_connected_wireless_reboot",
                  "restore_environment"
                  )

    common_function.case_steps_run_control(steps_list, __name__, case_name=case_name, log=wireless_pro.log,
                                           report_file=report_file)
