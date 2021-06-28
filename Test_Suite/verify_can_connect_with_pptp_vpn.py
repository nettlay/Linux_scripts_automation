import os
import subprocess
import time
import pyautogui
from Common import common_function
from Common.picture_operator import wait_element
from Test_Script.ts_network import network_setting, network


class PPTPVPN:

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

    def set_pptp_vpn(self, profile='profile_1', auto_start='enable'):
        try:
            result = self.vpn.set_vpn('pptp', profile=profile, auto_start=auto_start)
            return result
        except Exception as e:
            self.log.error(e)
            return 'exception'

    def check_vpn_result(self):
        get_result = self.vpn.get_vpn_ip('pptp')
        if not get_result:
            return False
        else:
            self.log.info('Get vpn ip {}.'.format(get_result))
        trace_result = self.vpn.trace_route()
        if not trace_result:
            return False
        else:
            self.log.info('Trace successfully.')
        return get_result, trace_result

    @staticmethod
    def reboot():
        pyautogui.hotkey('ctrl', 'alt', 's')
        time.sleep(1)
        pyautogui.typewrite('reboot', interval=0.25)
        pyautogui.hotkey('enter')
        time.sleep(1)
        pyautogui.hotkey('enter')
        time.sleep(5)

    def restore_default_settings(self):
        self.vpn.clear_vpn()

    def deal_with_unexpected(self, screenshot_name):
        pyautogui.screenshot(self.img_path + screenshot_name)
        time.sleep(1)
        self.restore_default_settings()

    def find_vpn_connection_error(self, wait=60):
        count = 0
        now_time = time.time()
        time_gap = 0
        while time_gap <= wait and count < 2:
            time_gap = time.time() - now_time
            result = self.wait_pictures("vpn_error")
            if not result:
                time.sleep(3)
                continue
            count += 1
            button_pos = self.wait_pictures("ok")
            if button_pos and count < 2:
                pyautogui.click(result[0])
            elif count < 2:
                pyautogui.hotkey('enter')
            else:
                pyautogui.hotkey("right")
                time.sleep(2)
                pyautogui.hotkey('enter')
            time.sleep(5)
        if count < 2:
            return False
        self.log.info("Find Error Times: {}".format(count))
        return True


pptp_vpn = PPTPVPN()


def preparation(**kwargs):
    log = kwargs.get("log")
    log.info('start preparation')
    if not pptp_vpn.switch_user('admin'):
        return False
    if not pptp_vpn.vpn.clear_vpn():
        return False
    update_case_result(True, 'preparation for switch user and clear vpn', **kwargs)


def configure_pptp_vpn(**kwargs):
    log = kwargs.get("log")
    log.info('start configure_pptp_vpn')
    open_result = pptp_vpn.open_network_vpn_dialog()
    update_case_result(open_result, 'open_network_vpn_dialog', **kwargs)
    if not open_result:
        pptp_vpn.deal_with_unexpected('fail_open_network_vpn_dialog.png')
        return False
    set_result = pptp_vpn.set_pptp_vpn()
    update_case_result(open_result, 'set_pptp_vpn', **kwargs)
    if not set_result:
        pptp_vpn.deal_with_unexpected('fail_set_pptp_vpn.png')
        return False
    pptp_vpn.close_control_panel('Apply')


def check_configure_pptp_vpn_result(**kwargs):
    log = kwargs.get("log")
    log.info('start check_configure_pptp_vpn_result')
    check_result = False
    if not pptp_vpn.find_vpn_connection_error():
        check_result = pptp_vpn.check_vpn_result()
    update_case_result(check_result, 'check_configure_pptp_vpn_result', **kwargs)
    if not check_result:
        pptp_vpn.deal_with_unexpected('fail_check_pptp_vpn_result.png')
        return False


def reboot(**kwargs):
    log = kwargs.get("log")
    log.info('start reboot')
    pptp_vpn.reboot()


def check_pptp_vpn_result_reboot(**kwargs):
    log = kwargs.get("log")
    log.info('start check_pptp_vpn_result_reboot')
    check_result = False
    if not pptp_vpn.find_vpn_connection_error():
        check_result = pptp_vpn.check_vpn_result()
    update_case_result(check_result, 'check_pptp_vpn_result_reboot', **kwargs)
    if not check_result:
        pptp_vpn.deal_with_unexpected('fail_check_pptp_vpn_result_reboot.png')
        return False


def restore_environment(**kwargs):
    log = kwargs.get("log")
    log.info('start restore_environment')
    pptp_vpn.restore_default_settings()


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
                  "configure_pptp_vpn",
                  "check_configure_pptp_vpn_result",
                  "reboot",
                  "check_pptp_vpn_result_reboot",
                  "restore_environment"
                  )

    common_function.case_steps_run_control(steps_list, __name__, case_name=case_name, log=pptp_vpn.log,
                                           report_file=report_file)

