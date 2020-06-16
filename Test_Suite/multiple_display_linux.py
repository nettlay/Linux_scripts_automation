import os
import yaml
from Test_Script.ts_multiple_display import display_function
from Common import picture_operator
from Common import vdi_connection
from Common.log import Logger
from Common import common_function
import time

case_names = ['[1]01.t730_2 monitors_DP 1920x1200 60_Landscape 2x1_citrix_win10_p1',
              '[2]02.t628_2 monitors_VGA 1920x1200 60+DVI 3840x2140 60_L left 2x2_RDP_Win10_p1',
              '[1]01.Mt31_3 monitors_LCD 1600x900 60+HDMI 1920x1200 30+Type-c 1920x1200 60_L left 3x1_view_rdp win10_p1'
              ]

result_file = os.path.join(common_function.get_current_dir(),
                           r'Test_Report',
                           '{}.yaml'.format(common_function.get_ip()))
log = Logger()
test_data = os.path.join(common_function.get_current_dir(), 'Test_Data')
config = os.path.join(test_data, 'td_multiple_display', 'vdi_server_config.yml')
with open(config) as f:
    vdi_config = yaml.safe_load(f)


def generate_pic_name(case_name):
    name_split = case_name.split('.')[1].split('_', 1)
    if name_split[0].lower().startswith('mt'):
        name = 'mtc_' + name_split[1] + '.png'
    else:
        name = 'dtc_' + name_split[1] + '.png'
    return name


def check_layout(source):
    temp_pic = picture_operator.capture_screen('temp.png')
    if temp_pic:
        return picture_operator.compare_picture_auto_collect(temp_pic, source)


def start(case_name=case_names[0], **kwargs):
    log.info('Begin to start test {}'.format(case_name))
    common_function.new_cases_result(result_file, case_name)
    pic_name = generate_pic_name(case_name)
    parameters = display_function.analyze_name(case_name)
    log.info('analyze parameter from case name')
    display_function.LinuxTools().generate_profile(parameters['layout'], parameters['monitors'])
    log.info('generate xml file')
    display_function.LinuxTools().set_local_resolution()
    log.info('set local resolution')
    user = common_function.get_vdi_user()
    log.info('get valid user : {}'.format(user))
    if parameters['vdi'].upper() == 'RDP':
        conn = vdi_connection.RDPLinux(user=user)
    elif parameters['vdi'].upper() == 'VIEW':
        conn = vdi_connection.ViewLinux(user=user)
    elif parameters['vdi'].upper() == 'CITRIX':
        conn = vdi_connection.CitrixLinux(user=user)
    else:
        conn = None
    log.info('init connection instance')
    if conn:
        # VDI Test
        conn_flag = False
        for count in range(2):
            if conn.logon(parameters['session']):
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
                                                              '{}_pic'.format(parameters['vdi']),
                                                              pic_name))
                if pic_sim >= 0.99:
                    log.info('check layout pass')
                    steps = {
                        'step_name': 'check vdi layout',
                        'result': 'Pass',
                        'expect': 'similarity > 99%',  # can be string or pic path
                        # 'actual': 'img/{}.jpg'.format(case_name),  # can be string or pic path
                        'actual': 'layout and resolution set correctly： {}'.format(pic_sim),
                        'note': ''}
                    common_function.update_cases_result(result_file, case_name, steps)
                else:
                    log.error('check layout Fail, autual: {}'.format(pic_sim))
                    picture_operator.save_from_data('"{}"'.format(common_function.get_current_dir() +
                                                                  '/Test_Report/img/{}.png'.format(case_name)),
                                                    diff_res)
                    picture_operator.capture_screen('"{}"'.format(common_function.get_current_dir() +
                                                                  '/Test_Report/img/{}.jpg'.format(case_name)))
                    steps = {
                        'step_name': 'check vdi layout',
                        'result': 'Fail',
                        'expect': 'similarity > 99%',  # can be string or pic path
                        'actual': 'img/{}.jpg'.format(case_name),  # can be string or pic path
                        'note': 'actual result: {}'.format(pic_sim)}
                    common_function.update_cases_result(result_file, case_name, steps)
                conn.logoff()
                break
            else:
                log.warning('logon fail in cycle {}'.format(count))
                # wait 2min try again
                time.sleep(120)
                continue
        if not conn_flag:
            log.warning('logon fail, and try count finished')
            steps = {
                'step_name': 'logon vdi',
                'result': 'Fail',
                'expect': '',  # can be string or pic path
                'actual': 'Fail to logon within 6 mins',  # can be string or pic path
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
    else:
        if check_layout(os.path.join(test_data, 'td_multiple_display', 'local_pic', pic_name)) >= 0.99:
            steps = {
                'step_name': 'check local layout',
                'result': 'Pass',
                'expect': 'similarity > 99%',  # can be string or pic path
                'actual': 'layout and resolution set correctly',
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
        else:
            picture_operator.capture_screen(os.path.join(common_function.get_current_dir(),
                                                         'Test_Report',
                                                         'img/{}.jpg'.format(case_name)))
            steps = {
                'step_name': 'check layout',
                'result': 'Fail',
                'expect': 'similarity > 99%',  # can be string or pic path
                'actual': 'img/{}.jpg'.format(case_name),  # can be string or pic path
                'note': ''}
            common_function.update_cases_result(result_file, case_name, steps)
            return
