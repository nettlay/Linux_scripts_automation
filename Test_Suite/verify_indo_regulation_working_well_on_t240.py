import os
import subprocess
import time
import pyautogui
from Common import common_function
from Common.picture_operator import wait_element
from Test_Script.ts_network import network_setting


class IndoRegulation:

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
        self.wireless_aps_between_149_161 = ['R1-Iverson-5G', 'R1-Function-5G', 'R1-TC_5G_ax_WPA2P', 'IN-PSSWIMM-5G',
                                             'R1-TC_5G_ac_WPA2P', 'R1-Linux-roaming', 'HPDM-5G', 'R1-Linux-AC',
                                             'R1-TC_5G_n', 'R1_5G_CH161_BW20M']

    def wait_pictures(self, pic_folder_name):
        '''
        Wait a desired picture. If exists, return its coordinate.
        :param pic_folder_name: folder name of pictures. e.g. 'right_down_corner'
        :return: tuple of coordinate. e.g. ()
        '''
        pic_folder = self.path + '/Test_Data/td_network/wireless/{}'.format(pic_folder_name)
        result = wait_element(pic_folder, rate=0.97)
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

    def configure_registry(self):
        subprocess.getoutput("mclient --quiet set root/Network/Wireless/countryOverride ID && mclient commit")
        time.sleep(1)
        result = subprocess.getoutput("mclient --quiet get root/Network/Wireless/countryOverride")
        if result and result == 'ID':
            self.log.info('Configure registry to set countryOverride ID successfully.')
            return True
        else:
            self.log.info('Fail to configure registry.')
            return False

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

    def close_control_panel(self, option='Discard'):
        """
        Close control panel with Apply or Discard option.
        :param option: options for save or discard. e.g. 'Discard'
        :return: none
        """
        subprocess.getoutput("wmctrl -c 'Control Panel'")
        time.sleep(1)
        if option.upper() == 'DISCARD':
            btn_discard = self.wait_pictures('discard')
            if btn_discard:
                pyautogui.click(btn_discard[0], btn_discard[1])
                time.sleep(1)
        else:
            pyautogui.hotkey('enter')
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

    def scan_indo_wireless_ap(self):
        scan_result = os.popen("iwlist wlan0 scan | grep 'Channel:' | awk '{print $1}'").readlines()
        if not scan_result:
            self.log.info('There is no wireless ap scanned.')
            return False
        for item in scan_result:
            if not item:
                continue
            i = item.split(':')[1]
            # 5g channel: 36 ~ 165
            # indo 5g channel: 149 ~ 161
            if any([int(i) in range(36, 149), int(i) in range(162, 166)]):
                self.log.info('Wireless channel {} of 5G should not be scanned for indo wireless.'.format(i))
                return False
        return True

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


wireless_indo = IndoRegulation()


def preparation(**kwargs):
    log = kwargs.get("log")
    log.info('start check_wireless_card')
    wireless_indo.switch_user('admin')
    result = wireless_indo.wireless.check_wireless_card()
    update_case_result(result, 'check_wireless_card', **kwargs)
    if not result:
        wireless_indo.restore_default_settings()
        return False
    del_wireless = wireless_indo.delete_wireless_profile()
    if not del_wireless:
        wireless_indo.restore_default_settings()
        return False


def configure_regsitry(**kwargs):
    log = kwargs.get("log")
    log.info('start configure_regsitry')
    result = wireless_indo.configure_registry()
    update_case_result(result, 'configure_regsitry', **kwargs)
    if not result:
        wireless_indo.restore_default_settings()
        return False


def reboot(**kwargs):
    log = kwargs.get("log")
    log.info('start reboot')
    wireless_indo.reboot()


def check_indo_wireless_5g(**kwargs):
    log = kwargs.get("log")
    log.info('start check_indo_wireless_5g')
    result = wireless_indo.wireless.indo_wireless_channels_5g_check()
    update_case_result(result, 'check_indo_wireless_5g', **kwargs)
    if not result:
        wireless_indo.restore_default_settings()
        return False


def scan_indo_wireless_ap(**kwargs):
    log = kwargs.get("log")
    log.info('start scan_indo_wireless_ap')
    result = wireless_indo.scan_indo_wireless_ap()
    update_case_result(result, 'scan_indo_wireless_ap', **kwargs)
    if not result:
        wireless_indo.restore_default_settings()
        return False


def set_wireless(**kwargs):
    log = kwargs.get("log")
    log.info('start set_wireless')
    wireless_indo.wireless.wired_wireless_switch('off')
    time.sleep(1)
    open_result = wireless_indo.open_network_wireless_dialog()
    update_case_result(open_result, 'open_network_wireless_dialog', **kwargs)
    if not open_result:
        pyautogui.screenshot(wireless_indo.img_path + 'open_network_dialog_for_indo_case.png')
        time.sleep(1)
        wireless_indo.restore_default_settings()
        return False
    add_result = wireless_indo.add_wireless_profiles(['R1-TC_5G_n'])
    update_case_result(add_result, 'add_wireless_profiles', **kwargs)
    if not add_result:
        pyautogui.screenshot(wireless_indo.img_path + 'add_wireless_profiles_for_indo_case.png')
        time.sleep(1)
        wireless_indo.restore_default_settings()
        return False
    wireless_indo.close_control_panel('apply')


def check_connected_wireless(**kwargs):
    log = kwargs.get("log")
    log.info('start check_connected_wireless')
    result = wireless_indo.check_connected_SSID('R1-TC_5G_n')
    update_case_result(result, 'check_connected_wireless', **kwargs)
    if not result:
        wireless_indo.restore_default_settings()
        return False


def restore_environment(**kwargs):
    log = kwargs.get("log")
    log.info('start restore_environment')
    wireless_indo.restore_default_settings()


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
                  "configure_regsitry",
                  "reboot",
                  "check_indo_wireless_5g",
                  "scan_indo_wireless_ap",
                  "set_wireless",
                  "check_connected_wireless",
                  "restore_environment"
                  )

    common_function.case_steps_run_control(steps_list, __name__, case_name=case_name, log=wireless_indo.log,
                                           report_file=report_file)
