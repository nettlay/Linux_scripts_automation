import traceback
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
from Common.common_function import get_platform, new_cases_result, update_cases_result
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.picture_operator import capture_screen, wait_element
from Common import log, common_function
import os
import re
import time

log = log.Logger()


def get_cup_mode():
    path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager', 'verify_ac_default_value',
                        'ondemand')
    if wait_element(path):
        cpu_mode = 'ondemand'
    else:
        cpu_mode = 'performance'
    log.info('get cpu mode:{}'.format(cpu_mode))
    return cpu_mode


def linux_get_cpu_mhz(mode):
    cpu_list = []
    for i in range(3):
        res1 = os.popen('cat /proc/cpuinfo | grep -i cpu').read()
        cpu_mhz = re.findall("cpu MHz		: (.*?)cpu cores", res1, re.S)
        cpu_mhz_list = []
        for j in cpu_mhz:
            cpu_mhz_list.append(float(j.strip('\n')))
        log.info("current cpu mhz list:{}".format(cpu_mhz_list))
        cpu_list.extend(cpu_mhz_list)
        time.sleep(3)
    if mode == "ondemand":
        log.info('get ondemand mode cpu mhz:{}'.format(min(cpu_list)))
        return min(cpu_list)
    else:
        log.info('get performance mode cpu mhz:{}'.format(max(cpu_list)))
        return max(cpu_list)


def select_mode(select, power_manager):
    if select == 'ondemand':
        power_manager.Battery.set(pms=pms.Battery.Normal.CPU_mode, selected=pms.Battery.Select.ondemand)
    else:
        power_manager.Battery.set(pms=pms.Battery.Normal.CPU_mode, selected=pms.Battery.Select.performance)
    power_manager.Battery.apply()
    time.sleep(2)
    log.info('switch cpu mode to {}'.format(select))


def verify_cpu_mhz(mode, case_name, power_manager):
    try:
        if mode == 'ondemand':
            low_mhz = linux_get_cpu_mhz(mode)
            select_mode('performance', power_manager)
            time.sleep(15)
            high_mhz = linux_get_cpu_mhz('performance')
            log.info("ondemand mode:{}, performance mode:{}".format(low_mhz, high_mhz))
            return [high_mhz, low_mhz]
        else:
            high_mhz = linux_get_cpu_mhz(mode)
            select_mode('ondemand', power_manager)
            time.sleep(15)
            low_mhz = linux_get_cpu_mhz('ondemand')
            log.info("performance mode:{}, ondemand mode:{}".format(high_mhz, low_mhz))
            return [high_mhz, low_mhz]
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        os.system("wmctrl -c 'Control Panel'")
        return '0'


def reset_settings(select, power_manager):
    # os.system("mclient --quiet set root/Power/default/AC/cpuMode {}".format(mode))
    # os.system("mclient commit")
    select_mode(select, power_manager)


def start(case_name, **kwargs):
    try:
        result_file = os.path.join(common_function.get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(common_function.check_ip_yaml()))
        log.info('Begin to start test {}'.format(case_name))
        new_cases_result(result_file, case_name)
        SwitchThinProMode(switch_to='admin')
        if 'mt' not in get_platform().lower():
            log.warning('There is no need to run this case on DTC')
            step1 = {'step_name': 'check current platform',
                     'result': 'Fail',
                     'expect': '',
                     'actual': '',
                     'note': 'current platform is not mtc, skip the case'}
            common_function.update_cases_result(result_file, case_name, step1)
            return
        power_manager = PowerManagerFactory("Battery")
        power_manager.Battery.open_power_manager_from_control_panel()
        power_manager.Battery.switch()
        default_mode = get_cup_mode()
        cpu_mhz_list = []
        loop_result = []
        for i in range(3):
            cpu_mode = get_cup_mode()
            value = verify_cpu_mhz(cpu_mode, case_name, power_manager)
            cpu_mhz_list.append(abs(float(value[0]) - float(value[1])))
            loop_result.append(value)
            time.sleep(2)
        reset_settings(default_mode, power_manager)
        power_manager.Battery.close_all_power_manager()
        log.info('cpu mhz list: {}'.format(cpu_mhz_list))
        value = max(cpu_mhz_list)
        if default_mode == 'ondemand':
            steps = {
                'step_name': 'verify the cpu run with ondemand on Battery',
                'result': 'Pass',
                'expect': 'ondemand',
                'actual': 'ondemand',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'verify the cpu run with ondemand on Battery',
                'result': 'Fail',
                'expect': 'ondemand',
                'actual': '{}'.format(default_mode),
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        if float(value) > 500:
            steps = {
                'step_name': 'check the cpu mhz',
                'result': 'Pass',
                'expect': '>500',
                'actual': '{}'.format(value),
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'check the cpu mhz',
                'result': 'Fail',
                'expect': '>500',
                'actual': '{}'.format(value),
                'note': 'loop 3 times result:{}'.format(loop_result)}
            update_cases_result(result_file, case_name, steps)
        log.info('{} end'.format(case_name))
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        os.system("wmctrl -c 'Control Panel'")
        pass

