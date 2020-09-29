from Test_Script.ts_network.network_setting import *
from Test_Script.ts_network.network import ping_server
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.common_function import new_cases_result, update_cases_result, get_current_dir, check_ip_yaml, get_ip
import time
import os


def case_pic(picture, ip_mode=''):
    return os.path.join(cf.get_current_dir(), "Test_Data", "td_network",
                        "wired_dynamic_ip_and_static_ip", ip_mode, picture)


def check_fiber_exist():
    fiber_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/eth1/IPv4/status")
    if fiber_status == "1":
        return True
    else:
        return False


def get_ip_mask_gateway():
    ip = os.popen('mclient --quiet get root/Network/Wired/IPAddress').read()
    mask = os.popen('mclient --quiet get root/Network/Wired/SubnetMask').read()
    gateway = os.popen('mclient --quiet get root/Network/Wired/DefaultGateway').read()
    return ip.strip(), mask.strip(), gateway.strip()


def dynamic_ip_check(case_name, result_file, wired):
    log.info("set connection method -> automatic")
    wired.open_network_wired_dialog()
    wired.set_dynamic_ip()
    time.sleep(5)
    log.info("open network wired check current connection method")
    wired.open_network_wired_dialog()
    res = wait_element(case_pic("connection_method", ip_mode='dynamic'))
    if res:
        steps = {
            'step_name': 'check dynamic connection method set success',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        method = get_connection_method()
        steps = {
            'step_name': 'check dynamic connection method set success',
            'result': 'Fail',
            'expect': '',
            'actual': 'the connection method automatic',
            'note': 'connection method {}'.format(method)}
        update_cases_result(result_file, case_name, steps)
        wired.close_control_panel()
        return False
    wired.close_control_panel()


def dynamic_ip_ping(case_name, result_file):
    log.info("ping any other available host, ex.15.83.240.98")
    ping_res = ping_server(ip="15.83.240.98")
    if ping_res:
        steps = {
            'step_name': 'check ping "15.83.240.98" result',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        steps = {
            'step_name': 'check ping "15.83.240.98" result',
            'result': 'Fail',
            'expect': 'ping success',
            'actual': 'ping result {}'.format(ping_res),
            'note': ''}
        update_cases_result(result_file, case_name, steps)
        return False


def static_ip_check(case_name, result_file, wired, ip, mask, gateway):
    log.info("set connection method -> static: IP Address, Subnet Mask, Default Gateway")
    log.info('static ip mode:ip({}), mask({}), gateway({})'.format(ip, mask, gateway))
    wired.open_network_wired_dialog()
    wired.set_static_ip(ip, mask, gateway)
    time.sleep(5)
    log.info("open network wired check current connection method")
    wired.open_network_wired_dialog()
    res = wait_element(case_pic("connection_method", ip_mode='static'))
    if res:
        current_ip, current_mask, current_gateway = get_ip_mask_gateway()
        if [current_ip, current_mask, current_gateway] == [ip, mask, gateway]:
            steps = {
                'step_name': 'check static connection method set success',
                'result': 'Pass',
                'expect': '',
                'actual': '',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'check static connection method set success',
                'result': 'Fail',
                'expect': '',
                'actual': 'ip:{}, mask:{}, gateway:{}'.format(ip, mask, gateway),
                'note': 'ip:{}, mask:{}, gateway:{}'.format(current_ip, current_mask, current_gateway)}
            update_cases_result(result_file, case_name, steps)
            wired.close_control_panel()
            return False
    else:
        method = get_connection_method()
        steps = {
            'step_name': 'check static connection method set success',
            'result': 'Fail',
            'expect': '',
            'actual': 'the connection method static',
            'note': 'connection method {}'.format(method)}
        update_cases_result(result_file, case_name, steps)
        wired.close_control_panel()
        return False
    wired.close_control_panel()


def static_ip_ping(case_name, result_file):
    log.info("ping any other available host, ex.15.83.240.98")
    ping_res = ping_server(ip="15.83.240.98")
    if ping_res:
        steps = {
            'step_name': 'check ping "15.83.240.98" result',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        steps = {
            'step_name': 'check ping "15.83.240.98" result',
            'result': 'Fail',
            'expect': 'ping success',
            'actual': 'ping result {}'.format(ping_res),
            'note': ''}
        update_cases_result(result_file, case_name, steps)
        return False


def get_connection_method():
    return os.popen('mclient --quiet get root/Network/Wired/Method').read()


def reset_connection_method(method):
    os.system("mclient --quiet set root/Network/Wired/Method {}".format(method))
    os.system("mclient commit")
    time.sleep(2)


def start(case_name, **kwargs):
    try:
        log.info('Begin to start case {}'.format(case_name))
        result_file = os.path.join(get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(check_ip_yaml()))
        new_cases_result(result_file, case_name)
        SwitchThinProMode(switch_to='admin')
        if not check_fiber_exist():
            log.error("not found fiber card on thin client")
            pre_check_report = {'step_name': 'check_fiber_exist',
                                'result': 'Fail',
                                'expect': 'has fiber card on thin client',
                                'actual': 'not found fiber card on thin client',
                                'note': ''}
            cf.update_cases_result(result_file, case_name, pre_check_report)
            log.error("test case {} fail".format(case_name))
            return False
        default_method = get_connection_method()
        wired = Wired()
        if dynamic_ip_check(case_name, result_file, wired) is False:
            reset_connection_method(default_method)
            return
        if dynamic_ip_ping(case_name, result_file) is False:
            reset_connection_method(default_method)
            return
        ip = get_ip()
        mask = wired.get_mask('eth0')
        gateway = wired.gateway()
        if static_ip_check(case_name, result_file, wired, ip, mask, gateway) is False:
            reset_connection_method(default_method)
            return
        if static_ip_ping(case_name, result_file) is False:
            reset_connection_method(default_method)
            return
    except:
        log.debug(traceback.format_exc(),
                  get_current_dir('Test_Report', 'img', '{}.png'.format(case_name)))
        os.system("wmctrl -c 'Control Panel'")


