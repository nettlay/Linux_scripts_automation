from Test_Script.ts_network.network_setting import *
from Test_Script.ts_network.network import ping_server
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.common_function import new_cases_result, update_cases_result, get_current_dir, check_ip_yaml
from Common.picture_operator import capture_screen


def wl_pic(picture):
    return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "wireless", picture)


def case_pic(picture):
    return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "verify_wl_band_option", picture)


def check_wl(picture):
    for i in range(2):
        cf.open_window("Wireless Statistics")
        time.sleep(5)
        if wait_element(case_pic("{}".format(picture)), rate=0.99):
            return True
        else:
            pyautogui.click(wait_element(case_pic("ssid"), offset=(10, 10))[0], interval=0.5)
            time.sleep(5)
            if wait_element(case_pic("{}".format(picture)), rate=0.99):
                return True
        close_wl_statistics()
        if i == 0:
            log.info('not found the {} icon will try again after 5s'.format(picture))
        time.sleep(5)
    return False


def close_wl_statistics():
    os.system("wmctrl -c 'Wireless Statistics'")


def connect_result(case_name, result_file, step):
    if check_wl("R1-Linux-roaming"):
        log.info('connection success')
        steps = {
            'step_name': '{} check could successful connect to specified AP'.format(step),
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
        close_wl_statistics()
        return True
    else:
        log.info('connection fail')
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}_{}.png'.format(case_name, step))
        capture_screen(error_pic)
        steps = {
            'step_name': '{} check could successful connect to specified AP'.format(step),
            'result': 'Fail',
            'expect': 'connect',
            'actual': 'disconnect',
            'note': '{}'.format(error_pic)}
        update_cases_result(result_file, case_name, steps)
        close_wl_statistics()
        return False


def add_wl(wireless, ssid, case_name, result_file):
    log.info('start add wireless profile {}'.format(ssid))
    wireless.add(ssid=ssid)
    wireless.apply_and_ok()
    icon = wait_element(wl_pic("_move_mouse"), offset=(0, 10))
    tool.click(icon[0][0], icon[0][1], num=2)
    if wait_element(wl_pic("_{}".format('R1-Linux-roaming'))):
        log.info("wireless profile {} add success".format(ssid))
    else:
        log.info("wireless profile {} add fail".format(ssid))
    # wireless.close_control_panel(option="apply")
    wireless.wl_set_apply()
    time.sleep(25)
    log.info('step1.1 check new wireless profile connection result')
    if connect_result(case_name, result_file, 'step1.1'):
        pass
    else:
        close_wl_statistics()
        return False
    log.info("step1.2 ping any other host, ex.15.83.240.98")
    ping_res = ping_server(ip="15.83.240.98")
    if ping_res:
        steps = {
            'step_name': 'step1.2 check ping "15.83.240.98" result',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        steps = {
            'step_name': 'step1.2 check ping "15.83.240.98" result',
            'result': 'Fail',
            'expect': 'ping success',
            'actual': 'ping result {}'.format(ping_res),
            'note': ''}
        update_cases_result(result_file, case_name, steps)
        return False
    wireless_info = wireless.connected_wireless_info()
    if 'busy' in wireless_info['channel']:
        time.sleep(5)
        wireless_info = wireless.connected_wireless_info()
    print(wireless_info)
    log.info('step2 check channel value (check the AP works at 2.4G frequency)')
    if int(wireless_info['channel']) <= 13:
        steps = {
            'step_name': 'step2 check the AP works at 2.4G frequency',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        steps = {
            'step_name': 'step2 check the AP works at 2.4G frequency',
            'result': 'Fail',
            'expect': '1-13',
            'actual': '{}'.format(wireless_info['channel']),
            'note': ''}
        update_cases_result(result_file, case_name, steps)
        wireless.close_control_panel()
        return False


def edit_wl_band_5g(wireless, ssid, edit_value_dict, case_name, result_file):
    log.info('step3 start edit wireless profile {} wireless band to 5G'.format(ssid))
    if wireless.edit(ssid, edit_value_dict):
        wireless.apply_and_ok()
    # wireless.close_control_panel(option="apply")
    wireless.wl_set_apply()
    time.sleep(25)
    if connect_result(case_name, result_file, 'step3'):
        pass
    else:
        close_wl_statistics()
        return False
    wireless_info = wireless.connected_wireless_info()
    if 'busy' in wireless_info['channel']:
        time.sleep(5)
        wireless_info = wireless.connected_wireless_info()
    print(wireless_info)
    log.info('step4 check channel value (check the AP works at 5G frequency)')
    if int(wireless_info['channel']) >= 36:
        steps = {
            'step_name': 'step4 check the AP works at 5G frequency',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        steps = {
            'step_name': 'step4 check the AP works at 5G frequency',
            'result': 'Fail',
            'expect': '>=36',
            'actual': '{}'.format(wireless_info['channel']),
            'note': ''}
        update_cases_result(result_file, case_name, steps)
        wireless.close_control_panel()
        return False


def edit_wl_band_auto(wireless, ssid, edit_value_dict, case_name, result_file):
    log.info('step5 start edit wireless profile {} wireless band to auto'.format(ssid))
    if wireless.edit(ssid, edit_value_dict):
        wireless.apply_and_ok()
    # wireless.close_control_panel(option="apply")
    wireless.wl_set_apply()
    time.sleep(30)
    if connect_result(case_name, result_file, 'step5'):
        pass
    else:
        close_wl_statistics()
        return False
    wireless_info = wireless.connected_wireless_info()
    if 'busy' in wireless_info['channel']:
        time.sleep(5)
        wireless_info = wireless.connected_wireless_info()
    print(wireless_info)
    log.info('step6 check channel value (check TC connect to any one of the two R1-Linux-roaming APs)')
    if int(wireless_info['channel']) >= 36:
        steps = {
            'step_name': 'step6 check TC connect to any one of the two R1-Linux-roaming APs',
            'result': 'Pass',
            'expect': '2.4G or 5G',
            'actual': '5G',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    elif 1 <= int(wireless_info['channel']) <= 13:
        steps = {
            'step_name': 'step6 check TC connect to any one of the two R1-Linux-roaming APs',
            'result': 'Pass',
            'expect': '2.4G or 5G',
            'actual': '2.4G',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        steps = {
            'step_name': 'step6 check TC connect to any one of the two R1-Linux-roaming APs',
            'result': 'Pass',
            'expect': '2.4G or 5G',
            'actual': 'none',
            'note': 'channel: {}'.format(wireless_info['channel'])}
        update_cases_result(result_file, case_name, steps)
        wireless.close_control_panel()
        return False


def delete_wl(wireless, ssid):
    log.info('start delete wireless profile {}'.format(ssid))
    wireless.delete(ssid=ssid)
    wireless.wl_set_apply()
    # wireless.close_control_panel(option="apply")


def start(case_name, **kwargs):
    try:
        result_file = os.path.join(get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(check_ip_yaml()))
        log.info('Begin to start test {}'.format(case_name))
        new_cases_result(result_file, case_name)
        SwitchThinProMode(switch_to='admin')
        wireless = Wireless()
        wireless.wired_wireless_switch('off')
        time.sleep(5)
        wireless.open_network()
        wireless.switch_to_wireless_tab()
        if add_wl(wireless, "R1-Linux-roaming_2.4G", case_name, result_file) is False:
            delete_wl(wireless, "R1-Linux-roaming")
            wireless.close_control_panel()
            return False
        edit_value_dict = {"wireless band": "5GHz"}
        if edit_wl_band_5g(wireless, "R1-Linux-roaming", edit_value_dict, case_name, result_file) is False:
            delete_wl(wireless, "R1-Linux-roaming")
            wireless.close_control_panel()
            return False
        time.sleep(5)
        edit_value_dict = {"wireless band": "Auto"}
        if edit_wl_band_auto(wireless, "R1-Linux-roaming", edit_value_dict, case_name, result_file) is False:
            delete_wl(wireless, "R1-Linux-roaming")
            wireless.close_control_panel()
            return False
        delete_wl(wireless, "R1-Linux-roaming")
        wireless.close_control_panel()
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        wireless = Wireless()
        delete_wl(wireless, "R1-Linux-roaming")
        os.system("wmctrl -c 'Control Panel'")

