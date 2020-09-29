import os
import subprocess
import time
import pyautogui
from Common import common_function
from Common.picture_operator import wait_element
from Test_Script.ts_network import network_setting, network


class EditPPTPVPN:

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
        self.vpn = network_setting.VPN()

    def wait_pictures(self, pic_folder_name, pic_folder_path='default'):
        '''
        Wait a desired picture. If exists, return its coordinate.
        :param pic_folder_name: folder name of pictures. e.g. 'right_down_corner'
        :param pic_folder_path: default is self.path + '/Test_Data/td_network/vpn/{}'.format(pic_folder_name)
        :return: tuple of coordinate. e.g. ()
        '''
        if pic_folder_path.upper() == 'DEFAULT':
            pic_folder = self.path + '/Test_Data/td_network/vpn/{}'.format(pic_folder_name)
        else:
            pic_folder = pic_folder_path
        result = wait_element(pic_folder, rate=0.97)
        if result:
            return result[0], result[1]
        else:
            self.log.info('Not found {} picture.'.format(pic_folder_name))
            return False

    def wait_pictures_timeout(self, pic_folder_name, loop=3):
        count = 0
        for i in range(loop):
            time.sleep(1)
            pic = self.wait_pictures(pic_folder_name)
            if pic:
                self.log.info('Find {}.'.format(pic_folder_name))
                return pic
            else:
                count += 1
        if count == 3:
            self.log.info('Fail to find {} after {} loops'.format(pic_folder_name, loop))
            return False

    def switch_user(self, user_mode):
        '''
        :param: user_mode: e.g. 'admin' or 'user'
        '''
        result = False
        if user_mode.upper() == 'ADMIN':
            result = common_function.SwitchThinProMode('admin')
        elif user_mode.upper() == 'USER':
            result = common_function.SwitchThinProMode('user')
        else:
            self.log.info('invalid user_mode {}'.format(user_mode))
        return result

    def close_control_panel(self, option='Discard'):
        """
        Close control panel with Apply or Discard option.
        :param option: options for save or discard. e.g. 'Discard'
        :return: none
        """
        subprocess.getoutput("wmctrl -c 'Control Panel'")
        time.sleep(1)
        if option.upper() == 'DISCARD':
            btn_discard = self.wait_pictures('discard', pic_folder_path=self.path + '/Test_Data/td_network/common/discard')
            if btn_discard:
                pyautogui.click(btn_discard[0])
                time.sleep(1)
        else:
            pyautogui.hotkey('enter')
            time.sleep(1)

    def open_network_vpn_dialog(self):
        self.close_control_panel()
        pyautogui.hotkey('ctrl', 'alt', 's')
        time.sleep(1)
        pyautogui.typewrite('network', interval=0.25)
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(1)
        result = self.wait_pictures('_vpn_tab')
        if result:
            pyautogui.click(result[0])
            self.log.info('open_network_vpn_dialog successfully.')
            return True
        else:
            return False

    def set_pptp_vpn(self, profile='profile_1', auto_start='disable'):
        try:
            result = self.vpn.set_vpn('pptp', profile=profile, auto_start=auto_start)
            return result
        except Exception as e:
            self.log.error(e)
            return 'exception'

    def pptp_vpn_connection(self, profile):
        open_result = self.open_network_vpn_dialog()
        if not open_result:
            self.deal_with_unexpected('fail_open_network_vpn_dialog_{}.png'.format(profile))
            return False
        set_result = self.set_pptp_vpn(profile=profile)
        if set_result is not True:
            self.deal_with_unexpected('fail_set_pptp_vpn_{}.png'.format(profile))
            return False
        self.close_control_panel('Apply')
        return True

    def restore_default_settings(self):
        self.vpn.clear_vpn()

    def deal_with_unexpected(self, screenshot_name):
        pyautogui.screenshot(self.img_path + screenshot_name)
        time.sleep(1)
        self.restore_default_settings()

    @staticmethod
    def update_case_result(result, step_name, report_file, case_name):
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
    pptp_vpn = EditPPTPVPN()
    switch_result = pptp_vpn.switch_user('admin')
    pptp_vpn.update_case_result(switch_result, 'switch_user', report_file, case_name)
    if not switch_result:
        pptp_vpn.deal_with_unexpected('fail_switch_admin.png')
        return False
    configure_result = pptp_vpn.pptp_vpn_connection('profile_1')
    pptp_vpn.update_case_result(configure_result, 'pptp_vpn_connection_create', report_file, case_name)
    if not configure_result:
        pptp_vpn.deal_with_unexpected('fail_pptp_vpn_connection_create.png')
        return False
    edit_result = pptp_vpn.pptp_vpn_connection('profile_edit')
    pptp_vpn.update_case_result(edit_result, 'pptp_vpn_connection_edit', report_file, case_name)
    if not edit_result:
        pptp_vpn.deal_with_unexpected('fail_pptp_vpn_connection_edit.png')
        return False
    if not pptp_vpn.open_network_vpn_dialog():
        pptp_vpn.log.info('Failt to open_network_vpn_dialog after edit')
        pptp_vpn.deal_with_unexpected('fail_open_network_vpn_dialog_after_edit.png')
        return False
    user_name = pptp_vpn.wait_pictures('user_name_empty_pptp')
    if user_name:
        pptp_vpn.update_case_result(True, 'check_pptp_vpn_connection_edit', report_file, case_name)
    else:
        pptp_vpn.update_case_result(False, 'check_pptp_vpn_connection_edit', report_file, case_name)
    pptp_vpn.close_control_panel()
    pptp_vpn.restore_default_settings()

