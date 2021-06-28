import os
import shutil
import pymouse
from Test_Script.ts_multiple_display import display_function
from Common import picture_operator
from Common import vdi_connection
from Common.log import log
from Common import common_function
from Common.performance_tool import *
import traceback
import gc
import pyautogui
mouse = pymouse.PyMouse()


"""
Test Steps:
record_case: False
get_pic_name: False
analyze_case_name: False
set_bg: False
check_local: False
logon: False
check_vdi: False
logoff: False
"""


def set_resolution_success():
    path = "/root/debug.log"
    if not os.path.exists(path):
        return True
    with open(path) as f:
        content = f.read()
    if "Unknown mode" in content:
        return False
    return True


case_names = ['[1]01.t730_2 monitors_DP 1920x1200 60_Landscape 2x1_rdp_rdp win10_p1_display_matrix']

session, rdp_server, user = "", "", ""


def generate_pic_name(case_name):
    name_split = case_name.split('_')
    # name_split.remove(name_split[0])
    # name_split.remove(name_split[-1])
    # name_split.remove(name_split[-1])
    list(filter(lambda x: name_split.remove(name_split[x]), [0, -1, -1, -1]))
    name = '{}.png'.format('_'.join(name_split)).replace(' ', '_').replace('monitor', 'm')
    return name


def generate_local_name(case_name):
    name_split = case_name.split('_')
    list(filter(lambda x: name_split.remove(name_split[x]), [0, -1, -1, -1, -1, -1]))
    name = '{}.png'.format('_'.join(name_split)).replace(' ', '_').replace('monitor', 'm')
    return name


def check_layout(source):
    temp_pic = picture_operator.capture_screen(os.path.join(common_function.get_current_dir(), 'temp.png'), auto_fix=True)
    if temp_pic:
        flag = False
        if not os.path.exists(source):
            flag = True
        return [*picture_operator.compare_picture_auto_collect(temp_pic, source, auto_fix=True), flag]


def local_start(case_name, result_file, test_data, local_pic_name):
    """
    make sure mouse position will not affect testing
    """
    pic_min_sim = 0.99
    x, y = mouse.position()
    if x >= y > 200:
        pyautogui.moveTo(200, 200)
    elif 200 > x >= y:
        pyautogui.moveTo(x + 20, y + 20)
    else:
        pyautogui.moveTo(250, 250)
    time.sleep(20)
    # check local resolution
    pic_sim, diff_res, first_collect_flag = check_layout(os.path.join(test_data, 'td_multiple_display', 'local_pic', local_pic_name))
    if "1_ms" in local_pic_name:
        log.info("Change Sim to 0.93")
        pic_min_sim = 0.93
    if pic_sim >= pic_min_sim:
        steps = {
            'step_name': 'check local layout',
            'result': 'Pass',
            'expect': 'similarity > 99%',  # can be string or pic path
            'actual': 'layout and resolution set correctly',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
        return True, first_collect_flag
    else:
        if not os.path.exists(common_function.get_current_dir('Test_Report', 'img')):
            os.mkdir(common_function.get_current_dir('Test_Report', 'img'))
        try:
            common_function.check_free_memory()
            picture_operator.save_from_data('{}'.format(common_function.get_current_dir('Test_Report', 'img',
                                                                                        '{}.png'.format(case_name))),
                                            diff_res)
            save_path = common_function.get_current_dir('Test_Report', 'img', '{}.jpg'.format(case_name))

            shutil.copy(common_function.get_current_dir('temp.png'),
                        save_path)
            common_function.check_free_memory("after")
        except AssertionError as e:
            raise e
        except:
            save_fail_path = common_function.get_current_dir('Test_Report', 'img', 'save_fail_{}.txt'.format(case_name))
            f = open(save_fail_path, "w")
            f.close()
        finally:
            log.debug(gc.garbage)
            gc.collect()

        steps = {
            'step_name': 'check local layout',
            'result': 'Fail',
            'expect': 'similarity > 99%',  # can be string or pic path
            'actual': 'img/{}.png'.format(case_name),  # can be string or pic path
            'note': 'actual similarity: {}'.format(pic_sim)}
        common_function.update_cases_result(result_file, case_name, steps)
        return False, first_collect_flag


def check_fresh_rate(case_name, result_file, parameters):
    res = display_function.LinuxTools.check_fresh_rate(parameters.get("monitors"))
    # check fresh rate ---------------------------------------------------------------------------------
    if res:
        steps = {
            'step_name': 'check local fresh rate',
            'result': 'Pass',
            'expect': '{}'.format(parameters.get("monitors")),  # can be string or pic path
            'actual': '{}'.format(res),
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
    else:
        steps = {
            'step_name': 'check local fresh rate',
            'result': 'Fail',
            'expect': '{}'.format(parameters.get("monitors")),  # can be string or pic path
            'actual': '{}'.format(display_function.LinuxTools.get_fresh_rate()),  # can be string or pic path
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
    # # check fresh rate end ------------------------------------------------------------------------------


def remote_start(case_name, result_file, test_data, pic_name, user_manager, parameters, performance):
    global session, rdp_server, user
    if parameters['vdi'].upper() == 'RDP':
        session = parameters.get('session')
        rdp_server = user_manager.get_a_available_key(session.lower())
        conn = vdi_connection.RDPLinux(user=user, parameters=parameters, rdp_server=rdp_server)
    elif parameters['vdi'].upper() == 'VIEW':
        conn = vdi_connection.ViewLinux(user=user, parameters=parameters)
    elif parameters['vdi'].upper() == 'CITRIX':
        conn = vdi_connection.CitrixLinux(user=user, parameters=parameters)
    else:
        conn = None
    log.info('init connection instance')
    first_collect_flag = False
    if conn:
        # VDI Test
        conn_flag = False
        for count in range(2):
            logon = conn.logon(parameters['session'])
            if logon is True:
                pymouse.PyMouse().click(1, 1)
                log.info('successfully logon session: {}'.format(parameters['session']))
                steps = {
                    'step_name': 'logon vdi',
                    'result': 'Pass',
                    'expect': '',  # can be string or pic path
                    'actual': 'logon successfully',
                    'note': ''}
                common_function.update_cases_result(result_file, case_name, steps)
                conn_flag = True
                pic_sim, diff_res, first_collect_flag = check_layout(os.path.join(test_data,
                                                              'td_multiple_display',
                                                              '{}_pic'.format(parameters['vdi']).lower(),
                                                              pic_name))
                if pic_sim >= 0.99:
                    log.info('check layout pass')
                    steps = {
                        'step_name': 'check vdi layout',
                        'result': 'Pass',
                        'expect': 'similarity > 99%',  # can be string or pic path
                        'actual': 'layout and resolution set correctly： {}'.format(pic_sim),
                        'note': ''}
                    common_function.update_cases_result(result_file, case_name, steps)
                else:
                    log.error('check layout Fail, autual: {}'.format(pic_sim))
                    shutil.copy(common_function.get_current_dir('temp.png'),
                                common_function.get_current_dir('Test_Report', 'img', '{}.jpg'.format(case_name)))
                    steps = {
                        'step_name': 'check vdi layout',
                        'result': 'Fail',
                        'expect': 'similarity > 99%',  # can be string or pic path
                        'actual': 'img/{}.png'.format(case_name),  # can be string or pic path
                        'note': 'actual result: {}'.format(pic_sim)}
                    common_function.update_cases_result(result_file, case_name, steps)
                    if not os.path.exists(common_function.get_current_dir('Test_Report', 'img')):
                        os.mkdir(common_function.get_current_dir('Test_Report', 'img'))
                    try:
                        common_function.check_free_memory("beforeremote")
                        picture_operator.save_from_data(
                            '{}'.format(common_function.get_current_dir('Test_Report', 'img',
                                                                        '{}.png'.format(
                                                                            case_name))),
                            diff_res)
                        common_function.check_free_memory("afterremote")
                    except:
                        save_fail_path = common_function.get_current_dir('Test_Report', 'img', 'save_fail_remote_{}.txt'.format(case_name))
                        f = open(save_fail_path, "w")
                        f.write(traceback.format_exc())
                        f.close()
                    finally:
                        log.debug(gc.garbage)
                        gc.collect()

                log.info("collecting performance data")
                path = "{}/Test_Report/performance/".format(common_function.get_current_dir())
                if not os.path.exists(path):
                    os.makedirs(path)
                performance.file = path + "{}.txt".format("".join(case_name.split("_")[2:-4]).replace(" ", ""))
                performance.start()
                conn.logoff()
                break
            elif isinstance(logon, str):
                log.warning('logon fail in cycle {}'.format(count))
                # wait 2min try again
                time.sleep(120)
                if not user:
                    log.info("user get none before, try to get a new user")
                    user = user_manager.get_a_available_key()
                    conn.user = user
                if parameters['vdi'].upper() == 'RDP' and not rdp_server:
                    log.info("try to get rdp_server")
                    session = parameters.get('session')
                    rdp_server = user_manager.get_a_available_key(session.lower())
                    conn.server = rdp_server
                    conn.domain_list = [rdp_server]
                continue
            else:
                log.error("logon fail in cycle {}& white list can't catch it, break!".format(count))
                break

        if not conn_flag:
            log.error('logon fail, and try count finished')
            steps = {
                'step_name': 'logon vdi',
                'result': 'Fail',
                'expect': '',  # can be string or pic path
                'actual': 'Fail to logon within 6 mins',  # can be string or pic path
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
            return False, first_collect_flag
    return True, first_collect_flag


def start(case_name=case_names[0], **kwargs):
    global user, rdp_server
    wait_time = 30
    time_path = common_function.get_current_dir("time_temp.txt")
    log.info("Start Wait {}".format(wait_time))
    if os.path.exists(time_path):
        with open(time_path, "r") as f:
            now_time = f.read()
    else:
        with open(time_path, "w") as f:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            f.write(now_time)
    current_time = time.time()
    before_time = time.mktime(time.strptime(now_time, "%Y-%m-%d %H:%M:%S"))
    if current_time - before_time > 3600:
        os.remove(time_path)
        common_function.reboot_command()
    common_function.SwitchThinProMode("user")
    query_list = ["xen", 'freerdp', "view", "firefox"]
    shadow_dict = {}
    for i in query_list:
        d = vdi_connection.query_item_id(i)
        shadow_dict.update(d)
    vdi_connection.hide_desktop_icon(id_dict=shadow_dict)
    common_function.cache_collection(3)
    case_name = case_name.lower()
    result_file = os.path.join(common_function.get_current_dir(),
                               r'Test_Report',
                               '{}.yaml'.format(common_function.check_ip_yaml()))
    user_manager = vdi_connection.MultiUserManger()
    performance = Performance.get_system_obj()
    test_data = os.path.join(common_function.get_current_dir(), 'Test_Data')
    # --------------- pre define --------------------------
    log.info('Begin to start test {}'.format(case_name))
    common_function.new_cases_result(result_file, case_name)
    pic_name = generate_pic_name(case_name)
    local_pic_name = generate_local_name(case_name)
    parameters = display_function.analyze_name(case_name)
    parameters = display_function.check_resolution_support(parameters)
    log.info('analyze parameter from case name')
    # display_function.LinuxTools().generate_profile(parameters['layout'], parameters['monitors'])
    display_function.set_display_profile(parameters)
    log.info('generate xml file')
    log.info('set local resolution, Wait 20s for background refresh')
    display_function.LinuxTools().set_local_resolution()
    log.debug("check local resolution set success")
    if not set_resolution_success() and common_function.need_reboot() != -1:
        common_function.change_reboot_status(-1)
        common_function.reboot_command()
    common_function.change_reboot_status(0)
    display_function.set_background()
    log.info('set local background success')
    flag, first_collect_flag = local_start(case_name, result_file, test_data, local_pic_name)
    if not flag:
        return False
    # check fresh rate-----------------------------------------------
    check_fresh_rate(case_name, result_file, parameters)
    # check fresh rate end-------------------------------------------
    user = user_manager.get_a_available_key()
    log.info('get valid user : {}'.format(user))
    remote_collect_flag = False
    try:
        flag, remote_collect_flag = remote_start(case_name, result_file, test_data, pic_name, user_manager, parameters, performance)
    except:
        debug_path = common_function.get_current_dir("Test_Report/debug.log")
        with open(debug_path, "a") as f:
            traceback.print_exc(file=f)
        traceback.print_exc()
        steps = {
            'step_name': 'case exception',
            'result': 'Fail',
            'expect': '',  # can be string or pic path
            'actual': 'img/{}.jpg'.format(case_name),
            'note': traceback.format_exc()}
        common_function.update_cases_result(result_file, case_name, steps)
    finally:
        log.info('try to reset user')
        if user:
            user_manager.reset_key(user)
        if parameters['vdi'].upper() == 'RDP' and rdp_server:
            user_manager.reset_key(rdp_server, key=session.lower())
        if first_collect_flag or remote_collect_flag:
            steps = {
                'step_name': "Cannot find template PIC",
                'result': 'Fail',
                'expect': '',  # can be string or pic path
                'actual': '',
                'note': 'This case has no pic in library'}
            common_function.update_cases_result(result_file, case_name, steps)
        log.debug(gc.garbage)
        gc.collect()