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
    temp_pic = picture_operator.capture_screen(os.path.join(common_function.get_current_dir(), 'temp.png'))
    if temp_pic:
        return picture_operator.compare_picture_auto_collect(temp_pic, source)


def local_start(case_name, result_file, test_data, local_pic_name):
    time.sleep(20)
    # check local resolution
    pic_sim, diff_res = check_layout(os.path.join(test_data, 'td_multiple_display', 'local_pic', local_pic_name))

    if pic_sim >= 0.99:
        steps = {
            'step_name': 'check local layout',
            'result': 'Pass',
            'expect': 'similarity > 99%',  # can be string or pic path
            'actual': 'layout and resolution set correctly',
            'note': ''}
        common_function.update_cases_result(result_file, case_name, steps)
        return True
    else:
        if not os.path.exists(common_function.get_current_dir('Test_Report', 'img')):
            os.mkdir(common_function.get_current_dir('Test_Report', 'img'))
        try:
            picture_operator.save_from_data('{}'.format(common_function.get_current_dir('Test_Report', 'img',
                                                                                        '{}.png'.format(case_name))),
                                            diff_res)
            shutil.copy(common_function.get_current_dir('temp.png'),
                        common_function.get_current_dir('Test_Report', 'img', '{}.jpg'.format(case_name)))
        except:
            pass
        steps = {
            'step_name': 'check local layout',
            'result': 'Fail',
            'expect': 'similarity > 99%',  # can be string or pic path
            'actual': 'img/{}.png'.format(case_name),  # can be string or pic path
            'note': 'actual similarity: {}'.format(pic_sim)}
        common_function.update_cases_result(result_file, case_name, steps)
        return False


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
        log.info('try to reset user with local test')
        if user:
            user_manager.reset_key(user)
        if parameters['vdi'].upper() == 'RDP' and rdp_server:
            user_manager.reset_key(rdp_server, key=session.lower())
    log.info('init connection instance')
    if conn:
        # VDI Test
        conn_flag = False
        for count in range(2):
            logon = conn.logon(parameters['session'])
            if logon and not isinstance(logon, str):
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
                pic_sim, diff_res = check_layout(os.path.join(test_data,
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
                        picture_operator.save_from_data(
                            '{}'.format(common_function.get_current_dir('Test_Report', 'img',
                                                                        '{}.png'.format(
                                                                            case_name))),
                            diff_res)
                    except:
                        pass

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
            return False
        return True


def start(case_name=case_names[0], **kwargs):
    global user, rdp_server
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
    log.info('analyze parameter from case name')
    display_function.set_background()
    log.info('set local background success')
    # display_function.LinuxTools().generate_profile(parameters['layout'], parameters['monitors'])
    display_function.set_display_profile(parameters)
    log.info('generate xml file')
    display_function.LinuxTools().set_local_resolution()
    log.info('set local resolution, Wait 20s for background refresh')
    flag = local_start(case_name, result_file, test_data, local_pic_name)
    if not flag:
        return False
    # check fresh rate-----------------------------------------------
    check_fresh_rate(case_name, result_file, parameters)
    # check fresh rate end-------------------------------------------
    user = user_manager.get_a_available_key()
    log.info('get valid user : {}'.format(user))
    try:
        return remote_start(case_name, result_file, test_data, pic_name, user_manager, parameters, performance)
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
