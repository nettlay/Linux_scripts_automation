from Test_Script.ts_network.network_setting import *
from Test_Script.ts_network.network import ping_server
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.picture_operator import capture_screen
from Common import vdi_connection, common_function as cf
import time
import os


steps_list = (
    "step1_1",
    "step1_2",
    "step2",
    "step3"
)


def case_pic(picture):
    return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "dns_server_and_domain", picture)


def edit_tls_version(user, tls_version='1.2'):
    rdp_id = vdi_connection.VDIConnection(user).vdi_connection_id('freerdp')
    os.system("mclient --quiet set root/ConnectionType/freerdp/connections/{}/tlsVersion {}".format(rdp_id, tls_version))
    os.system("mclient commit")
    time.sleep(5)


def vdi_setting():
    setting_file = os.path.join(cf.get_current_dir(), "Test_Data", "td_common", "thinpro_registry.yml")
    return YamlOperator(setting_file).read()


def step1_1(*args, **kwargs):
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    # cf.add_linux_script_startup('/root/run.sh')
    dns = DNS()
    dns.open_dns()
    dns.dns_set_server('15.83.244.81')
    dns.dns_set_domain('tcqa.hp')
    dns.close_dns()
    time.sleep(5)
    dns.open_dns()
    domain = wait_element(case_pic('domain'))
    server = wait_element(case_pic('server'))
    dns.close_dns()
    if domain and server:
        log.info('Settings could be applied')
        steps = {
            'step_name': 'check Settings could be applied',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        cf.update_cases_result(result_file, case_name, steps)
    else:
        log.info('no apply')
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+step1_1.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check Settings could be applied',
            'result': 'Fail',
            'expect': '',
            'actual': '',
            'note': '{}'.format(error_pic)}
        cf.update_cases_result(result_file, case_name, steps)
        return False
    os.system("mclient --quiet set root/auto-update/enableOnBootup 0")
    os.system("mclient commit")
    log.info('start to reboot the TC')
    os.system('reboot')
    time.sleep(20)


def step1_2(*args, **kwargs):
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    dns = DNS()
    dns.open_dns()
    domain = wait_element(case_pic('domain'))
    server = wait_element(case_pic('server'))
    dns.close_dns()
    if domain and server:
        log.info('nothing lost after reboot')
        steps = {
            'step_name': 'check nothing lost after reboot',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        cf.update_cases_result(result_file, case_name, steps)
    else:
        log.info('not lost')
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+step1_2.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check nothing lost after reboot',
            'result': 'Fail',
            'expect': '',
            'actual': '',
            'note': '{}'.format(error_pic)}
        cf.update_cases_result(result_file, case_name, steps)
        return False


def step2(*args, **kwargs):
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    ping_res = ping_server(ip="auto-update")
    if ping_res:
        steps = {
            'step_name': 'check ping auto-update result',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        cf.update_cases_result(result_file, case_name, steps)
    else:
        log.info('not lost')
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+step2.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check ping auto-update result',
            'result': 'Fail',
            'expect': '',
            'actual': '',
            'note': '{}'.format(error_pic)}
        cf.update_cases_result(result_file, case_name, steps)
        return False


def step3(*args, **kwargs):
    case_name = kwargs.get("case_name")
    result_file = kwargs.get("report_file")
    user = 'testadmin'
    rdp_server = 'auto-update.tcqa.hp'
    domain = 'tcqa'
    log.info('start step3 login RDP {} {}'.format(user, rdp_server))
    settings = vdi_setting()["set"]["RDP"]["additional_DNS_Server_and_Search_Domain_works_step3"]
    conn = vdi_connection.RDPLinux(user=user, domain=domain, rdp_server=rdp_server, setting=settings)
    logon_res = conn.logon("fasdfs")
    start_menu = wait_element(case_pic('vdi_start_menu'))
    tool.click(start_menu[0][0], start_menu[0][1])
    logoff = wait_element(case_pic('vdi_logoff'))
    tool.click(logoff[0][0], logoff[0][1])
    edit_tls_version(user)
    if logon_res:
        log.info('vdi rdp login success')
        steps = {
            'step_name': 'check login RDP to auto-update.tcqa.hp',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        cf.update_cases_result(result_file, case_name, steps)
    else:
        log.info('vdi rdp login fail')
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+step2.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check ping auto-update result',
            'result': 'Fail',
            'expect': '',
            'actual': '',
            'note': '{}'.format(error_pic)}
        cf.update_cases_result(result_file, case_name, steps)
        return False


def start(case_name, **kwargs):
    try:
        log.info('Begin to start case {}'.format(case_name))
        result_file = os.path.join(get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(cf.check_ip_yaml()))
        cf.new_cases_result(result_file, case_name)
        SwitchThinProMode(switch_to='admin')
        cf.case_steps_run_control(steps_list, __name__, case_name=case_name, log=log,
                                               report_file=result_file)
        cf.import_profile()
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        cf.import_profile()
        os.system("wmctrl -c 'Control Panel'")
