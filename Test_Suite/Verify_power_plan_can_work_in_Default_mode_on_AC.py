import traceback
from Test_Script.ts_power_manager.common_function import PrepareWakeUp
from Test_Script.ts_power_manager.screensaver import ScreenSaver
import os
from Common import log, common_function
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.picture_operator import capture_screen, wait_element
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory


log = log.Logger()


def check_ac_default_value():
    power_manager = PowerManagerFactory("AC")
    power_manager.AC.open_power_manager_from_control_panel()
    power_manager.AC.switch()
    path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager', 'verify_ac_default_value',
                        'sleep_time')
    if wait_element(path):
        sleep = '30'
    else:
        sleep = ''
    log.info('get default value on AC sleep after:{}'.format(sleep))
    power_manager.AC.close_all_power_manager()
    return sleep


def start(case_name, **kwargs):
    try:
        result_file = os.path.join(common_function.get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(common_function.check_ip_yaml()))
        log.info('Begin to start test {}'.format(case_name))
        common_function.new_cases_result(result_file, case_name)
        SwitchThinProMode(switch_to='admin')
        sleep_time = check_ac_default_value()
        if sleep_time == '30':
            steps = {
                'step_name': 'check the default value on AC',
                'result': 'Pass',
                'expect': '30',
                'actual': '30',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'check the default value on AC',
                'result': 'Fail',
                'expect': '30',
                'actual': 'The default value is wrong',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
            log.info('case {} is end'.format(case_name))
            return False
        with PrepareWakeUp(time=1810) as w:
            w.wait(1810)
        to_os = ScreenSaver()
        to_os.resume_lock_screen_by_mouse()
        last_time_gap = int(w.get_max_time_gap())
        if last_time_gap > 5:
            steps = {
                'step_name': 'check the os go to verify_s3_work afer 30 minutes',
                'result': 'Pass',
                'expect': 'sleep',
                'actual': 'it is go to sleep',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'check the os go to verify_s3_work afer 30 minutes',
                'result': 'Fail',
                'expect': 'sleep',
                'actual': 'it is not go to sleep',
                'note': 'time gap: {}, must more than 5'.format(last_time_gap)}
            common_function.update_cases_result(result_file, case_name, steps)
            return False
        if last_time_gap > 5:
            steps = {
                'step_name': 'check the os wake up',
                'result': 'Pass',
                'expect': 'wake up',
                'actual': 'System can wake up immediately',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'check the os wake up',
                'result': 'Fail',
                'expect': 'wake up',
                'actual': 'System not wake up immediately',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
        log.info('case {} is end'.format(case_name))
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name.replace(' ', '_')))
        capture_screen(error_pic)
        pass
