from Test_Script.ts_network.network_setting import *
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.common_function import new_cases_result, update_cases_result, get_current_dir, check_ip_yaml
from Common.picture_operator import capture_screen


def wl_pic(picture):
    return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "wireless", picture)


def case_pic(picture):
    return os.path.join(cf.get_current_dir(), "Test_Data", "td_network", "verify_wl_add_edit_delete", picture)


def check_wl(picture):
    for i in range(2):
        time.sleep(10)
        cf.open_window("Wireless Statistics")
        time.sleep(5)
        if wait_element(case_pic("{}".format(picture)), rate=0.99):
            return True
        else:
            pyautogui.click(wait_element(case_pic("ssid"), offset=(10, 10))[0], interval=0.5)
            time.sleep(5)
            if wait_element(case_pic("{}".format(picture)), rate=0.99):
                return True
        if i == 0:
            log.info('not found the {} icon will try again after 5s'.format(picture))
            close_wl_statistics()
        time.sleep(5)
    return False


def close_wl_statistics():
    os.system("wmctrl -c 'Wireless Statistics'")


def add_wl(wireless, ssid, case_name, result_file):
    log.info('start add wireless profile {}'.format(ssid))
    wireless.add(ssid=ssid)
    wireless.apply_and_ok()
    icon = wait_element(wl_pic("_move_mouse"), offset=(0, 10))
    tool.click(icon[0][0], icon[0][1], num=2)
    if wait_element(wl_pic("_{}".format(ssid))):
        log.info("wireless profile {} add success".format(ssid))
        steps = {
            'step_name': 'check all the configurations could be saved -- add',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+add1.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check all the configurations could be saved -- add',
            'result': 'Fail',
            'expect': 'saved',
            'actual': 'no exists',
            'note': '{}'.format(error_pic)}
        update_cases_result(result_file, case_name, steps)
        wireless.wl_set_apply()
        return False
    wireless.wl_set_apply()
    time.sleep(25)
    if check_wl("add_res"):
        log.info('new wireless profile connection success')
        steps = {
            'step_name': 'check could successful connect to specified AP -- add',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+add2.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check could successful connect to specified AP -- add',
            'result': 'Fail',
            'expect': 'connect',
            'actual': 'disconnect',
            'note': '{}'.format(error_pic)}
        update_cases_result(result_file, case_name, steps)
        close_wl_statistics()
        reset_setting(wireless, ssid)
        return False
    close_wl_statistics()


def edit_wl(wireless, ssid, edit_value_dict, case_name, result_file):
    log.info('start edit wireless profile {}'.format(ssid))
    if wireless.edit(ssid, edit_value_dict):
        wireless.apply_and_ok()
    icon = wait_element(wl_pic("_move_mouse"), offset=(0, 10))
    tool.click(icon[0][0], icon[0][1], num=2)
    if "ssid" in edit_value_dict.keys():
        ssid1 = edit_value_dict["ssid"]
    else:
        ssid1 = ssid
    if wait_element(wl_pic("_{}".format(ssid1))):
        log.info("wireless profile {} edit success".format(ssid))
        steps = {
            'step_name': 'check all the configurations could be saved -- edit',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+edit1.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check all the configurations could be saved -- edit',
            'result': 'Fail',
            'expect': 'saved',
            'actual': 'no exists',
            'note': '{}'.format(error_pic)}
        update_cases_result(result_file, case_name, steps)
        reset_setting(wireless, ssid1)
        wireless.wl_set_apply()
        return False
    wireless.wl_set_apply()
    time.sleep(25)
    if check_wl("edit_res"):
        log.info('edited wireless connection success')
        steps = {
            'step_name': 'check could successful connect to specified AP -- edit',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+edit2.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check could successful connect to specified AP -- edit',
            'result': 'Fail',
            'expect': 'connect',
            'actual': 'disconnect',
            'note': '{}'.format(error_pic)}
        update_cases_result(result_file, case_name, steps)
        close_wl_statistics()
        reset_setting(wireless, ssid)
        return False
    close_wl_statistics()


def delete_wl(wireless, ssid, case_name, result_file):
    log.info('start delete wireless profile {}'.format(ssid))
    wireless.delete(ssid=ssid)
    icon = wait_element(wl_pic("_move_mouse"), offset=(0, 10))
    tool.click(icon[0][0], icon[0][1], num=2)
    if not wait_element(wl_pic("_{}".format(ssid))):
        log.info("wireless profile {} delete success".format(ssid))
        steps = {
            'step_name': 'check selected profile could be deleted',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+delete1.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check selected profile could be deleted',
            'result': 'Fail',
            'expect': 'deleted',
            'actual': 'exists',
            'note': '{}'.format(error_pic)}
        update_cases_result(result_file, case_name, steps)
        wireless.wl_set_apply()
        reset_setting(wireless, ssid)
        return False
    wireless.wl_set_apply()
    time.sleep(25)
    if not check_wl("edit_res"):
        log.info('deleted wireless connection disconnection success')
        steps = {
            'step_name': 'check thinpro will disconnect from the wireless network',
            'result': 'Pass',
            'expect': '',
            'actual': '',
            'note': ''}
        update_cases_result(result_file, case_name, steps)
    else:
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}+delete2.png'.format(case_name))
        capture_screen(error_pic)
        steps = {
            'step_name': 'check thinpro will disconnect from the wireless network',
            'result': 'Fail',
            'expect': 'disconnect',
            'actual': 'connect',
            'note': '{}'.format(error_pic)}
        update_cases_result(result_file, case_name, steps)
        close_wl_statistics()
        reset_setting(wireless, ssid)
        return False
    close_wl_statistics()


def reset_setting(wireless, ssid):
    wireless.delete(ssid=ssid)
    wireless.wl_set_apply()


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
        if add_wl(wireless, "R1-TC_5G_n", case_name, result_file) is False:
            wireless.close_control_panel()
            return
        edit_value_dict = {"ssid": "R1-TC_2.4G_n_WPA2P", "authentication": "WPA/WPA2-PSK", "password": "neoware1234"}
        if edit_wl(wireless, "R1-TC_5G_n", edit_value_dict, case_name, result_file) is False:
            wireless.close_control_panel()
            return
        if delete_wl(wireless, "R1-TC_2.4G_n_WPA2P", case_name, result_file):
            wireless.close_control_panel()
            return
        reset_setting(wireless, 'R1-TC_5G_n')
        reset_setting(wireless, 'R1-TC_2.4G_n_WPA2P')
        wireless.close_control_panel()
    except:
        log.error(traceback.format_exc())
        error_pic = os.path.join(get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        os.system("wmctrl -c 'Control Panel'")


