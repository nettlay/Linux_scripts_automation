import os
import time
import traceback
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common import picture_operator, common_function, tool, log, vdi_connection
from Common.domain import add_domain_with_check, domain_login, leave_domain_with_check
from Test_Script.ts_power_manager.common_function import linux_check_locked
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
import pyautogui

log = log.Logger()


steps_list = (
    "join_tc_domain",
    "add_domain_result",
    "login_domain_user",
    "login_remote",
    "verify_two_account",
    "login_two_accounts",
    "verify_remote_only",
    "reset_all_settings",
    "last_step"
)


def check_icon(p):
    path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager',
                        'verify_domain_users', '{}'.format(p))
    if linux_check_locked(path=path):
        return True


def join_tc_domain(*args, **kwargs):
    log.info('1.join the tc/pc to domain')
    add_domain_with_check(1, user_name='justin.zhao', password="Shanghai2010", domain_name='sh.dto')
    time.sleep(5)
    log.info('delete vdi on the desktop')
    vdi_connection.VDIConnection('autotest').delete_vdi('freerdp')
    log.info('reboot the TC')
    user_manager = kwargs.get("user_manager")
    user = kwargs.get('user')
    server = kwargs.get('rdp_server')
    reset_key(user_manager, user, server)
    common_function.reboot()
    time.sleep(15)


def add_domain_result(*args, **kwargs):
    log.info('check the result of step join tc domain')
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    if check_icon('domain_login_user') or check_icon('domain_login_pwd'):
        steps = {
            'step_name': 'verify add domain and reboot success',
            'result': 'Pass',
            'expect': 'add domain success',
            'actual': 'success',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
    else:
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', 'verify_add_domain_result.png')
        picture_operator.capture_screen(error_pic)
        steps = {
            'step_name': 'verify add domain and reboot success',
            'result': 'Fail',
            'expect': 'add domain success',
            'actual': 'fail',
            'note': '{}'.format(error_pic)}
        common_function.update_cases_result(result_file, case_name, steps)
        domain_login(user_name='!#$%^', password="Shanghai2010")
        reset_all_settings(num=0)
        return False


def login_domain_user(*args, **kwargs):
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    log.info('2.1. Login with  !#$%^  Shanghai2010')
    time.sleep(10)
    domain_login(user_name='!#$%^', password="Shanghai2010")
    time.sleep(5)
    if check_account('start') or check_account('domain_icon'):
        steps = {
            'step_name': 'login domain account success',
            'result': 'Pass',
            'expect': 'login success',
            'actual': 'success',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
    else:
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', 'login_domain_user_result.png')
        picture_operator.capture_screen(error_pic)
        steps = {
            'step_name': 'login domain account success',
            'result': 'Fail',
            'expect': 'login success',
            'actual': 'fail',
            'note': '{}'.format(error_pic)}
        common_function.update_cases_result(result_file, case_name, steps)
        reset_all_settings(num=0)
        return False


def login_remote(*args, **kwargs):
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    log.info('2.2. Start a remote session with your SH account.')
    SwitchThinProMode(switch_to='user')
    conn = kwargs.get('conn')
    if start_remote('logon', conn=conn):
        steps = {
            'step_name': 'login a remote session (RDP)',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
    else:
        log.info('remote session login fail')
        steps = {
            'step_name': 'login a remote session (RDP)',
            'result': 'Fail',
            'expect': 'login success',
            'actual': 'vdi login fail',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
        reset_all_settings(num=0)
        return False


def sw_user(p):
    path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager',
                        'verify_domain_users', '{}'.format(p))
    power_icon = picture_operator.wait_element(path, offset=(10, 10))
    print(power_icon)
    if power_icon:
        tool.click(power_icon[0][0], power_icon[0][1], 3)


def lock_screen():
    log.info('lock the screen')
    SwitchThinProMode(switch_to='user')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'alt', 'l')
    time.sleep(2)
    size = common_function.screen_resolution()
    tool.click(int(size[0] / 2), int(size[1] / 2), 1)
    return True


def check_account(p):
    log.info('check icon {} whether shown'.format(p))
    if check_icon(p):
        return True


def unlock_screen(user, password):
    log.info('Try  {}  {}  to unlock screen'.format(user, password))
    if check_icon('wran_error'):
        pyautogui.press('enter')
        time.sleep(2)
    sw_user('unlock')
    pyautogui.typewrite(user)
    time.sleep(1)
    pyautogui.press("tab")
    time.sleep(1)
    pyautogui.typewrite(password)
    time.sleep(1)
    pyautogui.press("enter")


def require_pass_domain_users():
    log.info('Uncheck "Require password for domain users')
    SwitchThinProMode(switch_to='admin')
    power_m = PowerManagerFactory("ScreenSaver")
    power_m.ScreenSaver.open_power_manager_from_control_panel()
    power_m.ScreenSaver.switch()
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_domain_users, radio="off")
    power_m.ScreenSaver.apply()
    time.sleep(3)
    power_m.ScreenSaver.close_all_power_manager()


def reset_require_pass_domain_users():
    try:
        SwitchThinProMode(switch_to='admin')
        power_m = PowerManagerFactory("ScreenSaver")
        power_m.ScreenSaver.open_power_manager_from_control_panel()
        power_m.ScreenSaver.switch()
        power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
        power_m.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_domain_users, radio="on")
        power_m.ScreenSaver.apply()
        time.sleep(3)
        power_m.ScreenSaver.close_all_power_manager()
    except:
        log.info('reset require password domain user fail')


def start_remote(lg, **kwargs):
    conn = kwargs.get('conn')
    if lg == 'logon':
        log.info('Switch to user mode to start remote session')
        return conn.logon("fasdfs")
    else:
        log.info('logoff remote session')
        res = conn.logoff()
        return res


def reset_key(user_manager, user, rdp_server):
    user_manager.reset_key(user)
    user_manager.reset_key(rdp_server, key='rdp win10')


def verify_two_account(*args, **kwargs):
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    log.info('verify two accounts art listed')
    lock_screen()
    if check_account('with_vdi'):
        steps = {
            'step_name': 'verify two accounts art listed',
            'result': 'Pass',
            'expect': 'correct',
            'actual': 'correct',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
    else:
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', 'verify_domain_and_rdp_two_account_are_listed.png')
        picture_operator.capture_screen(error_pic)
        steps = {
            'step_name': 'verify two accounts art listed',
            'result': 'Fail',
            'expect': 'correct',
            'actual': 'wrong',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
        reset_all_settings(num=0)
        return False


def login_two_accounts(*args, **kwargs):
    user = kwargs.get('user')
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    log.info('verify both can unlock screen')
    flag = ''
    d = {r'sh\{}'.format(user): 'Shanghai2010', 'sh.dto\!#$%^': 'Shanghai2010'}
    for i, j in d.items():
        unlock_screen(i, j)
        if check_account('wran_error'):
            flag += i
            pyautogui.press('enter')
            continue
        if i != 'sh.dto\!#$%^':
            lock_screen()
    # unlock_screen(r'sh.dto\!#$%^', 'Shanghai2010')
    log.info('flag value:{}'.format(flag))
    if flag == '':
        steps = {
            'step_name': 'try login with two accounts',
            'result': 'Pass',
            'expect': 'success',
            'actual': 'success',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
    else:
        steps = {
            'step_name': 'try longin with two accounts',
            'result': 'Fail',
            'expect': 'success',
            'actual': '{} fail'.format(flag),
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
        reset_all_settings(num=0)
        return False


def verify_remote_only(*args, **kwargs):
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    user = kwargs.get('user')
    conn = kwargs.get('conn')
    start_remote('', conn=conn)
    time.sleep(5)
    log.info("verify only remote session's account is listed")
    require_pass_domain_users()
    SwitchThinProMode(switch_to='user')
    start_remote('logon', conn=conn)
    lock_screen()
    if check_account('no_vdi'):
        steps = {
            'step_name': "only one remote session's account is listed",
            'result': 'Pass',
            'expect': 'success',
            'actual': 'success',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
        unlock_screen(r'sh\{}'.format(user), 'Shanghai2010')
    else:
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}+verify_remote_only.png'.format(case_name))
        picture_operator.capture_screen(error_pic)
        steps = {
            'step_name': "only one remote session's account is listed",
            'result': 'Fail',
            'expect': 'success',
            'actual': 'fail',
            'note': '{}'.format(error_pic)}
        common_function.update_cases_result(result_file, case_name, steps)
        unlock_screen(r'sh.dto\!#$%^', 'Shanghai2010')
    start_remote('', conn=conn)


def reset_all_settings(*args, **kwargs):
    log.info('reset all settings')
    num = kwargs.get('num', 15)
    user_manager = kwargs.get("user_manager")
    user = kwargs.get('user')
    server = kwargs.get('rdp_server')
    conn = kwargs.get('conn')
    if not check_icon('start') and not check_icon('unlock'):
        pyautogui.press('enter')
        unlock_screen(r'sh.dto\!#$%^', 'Shanghai2010')
        time.sleep(5)
        if check_icon('locked'):
            unlock_screen('root', '1')
    if check_icon('unlock'):
        unlock_screen(r'sh.dto\!#$%^', 'Shanghai2010')
        time.sleep(5)
        if check_icon('locked'):
            unlock_screen('root', '1')
    start_remote('', conn=conn)
    reset_key(user_manager, user, server)
    reset_require_pass_domain_users()
    if not leave_domain_with_check():
        common_function.import_profile()
        os.system('reboot')
    else:
        common_function.import_profile()
    time.sleep(num)


def last_step(*args, **kwargs):
    user_manager = kwargs.get("user_manager")
    case_name = kwargs.get("case_name")
    user = kwargs.get('user')
    server = kwargs.get('rdp_server')
    reset_key(user_manager, user, server)
    common_function.import_profile()
    log.info('test case {} is end'.format(case_name))


def start(case_name, **kwargs):
    try:
        log.info('Begin to start test {}'.format(case_name))
        user_manager = vdi_connection.MultiUserManger()
        user = user_manager.get_a_available_key()
        rdp_server = user_manager.get_a_available_key('rdp win10')
        conn = vdi_connection.RDPLinux(user=user, rdp_server=rdp_server)
        log.info('user: {}, rdp_server: {}'.format(user, rdp_server))
        report_file = os.path.join(common_function.get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(common_function.check_ip_yaml()))
        common_function.new_cases_result(report_file, case_name)
        common_function.case_steps_run_control(steps_list, __name__, case_name=case_name, log=log,
                                               report_file=report_file, user=user, rdp_server=rdp_server,
                                               conn=conn, user_manager=user_manager)
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        picture_operator.capture_screen(error_pic)
        reset_all_settings(num=0)
        return False
