import time
import traceback
import os
import yaml
from Common.common_function import add_linux_script_startup, get_current_dir, update_cases_result, load_data_from_ftp, \
    get_platform, export_profile, memory_check, show_desktop, get_global_config, need_reboot, reboot_command, \
    change_reboot_status, SwitchThinProMode
from Common.log import log
from Common.file_transfer import FTPUtils
from Common import email_tool
from Common.picture_operator import capture_screen
from Common.file_operator import YamlOperator
from Common.common_function import prepare_for_framework, get_report_base_name, check_water_mark, collect_report
from settings import *
from Common.exception import MemoryNotSufficient
from Common.support_design_report_style import zip_file_name,get_report_number,get_report_value

os.environ['LD_LIBRARY_PATH'] = "/usr/lib/x86_64-linux-gnu/"
os.environ['SHLVL'] = "7"
MEMORY_LIMIT = int(get_global_config("memory_limit"))


def main():
    # show_desktop()
    if os.path.exists(get_current_dir('flag.txt')):
        with open(get_current_dir('flag.txt')) as f:
            test_flag = f.read()
            if 'TEST FINISHED' in test_flag.upper():
                return
    if not os.path.exists('time.txt'):
        with open('time.txt', 'w') as f:
            f.write(time.ctime())
    prepare_for_framework()
    additional_path = get_current_dir('Test_Data', 'additional.yml')
    file_obj = YamlOperator(additional_path)
    content = file_obj.read()
    site = content.get('AutoDash_Site')
    if not site:
        load_data_from_ftp()
        script_name = os.path.basename(__file__).split('.')[0]
        add_linux_script_startup([script_name])
        check_water_mark()
    path = get_current_dir('reboot.txt')
    if not os.path.exists(path):
        with open(path, 'w+') as f:
            f.write("0")
        time.sleep(5)
        if os.path.exists(path):
            SwitchThinProMode("admin")
            os.popen('reboot')
            time.sleep(30)
    if not os.path.exists(get_current_dir('Test_Report')):
        os.mkdir(get_current_dir('Test_Report'))
    test_data_path = os.path.join(get_current_dir(), 'Test_Data')
    with open(get_current_dir('flag.txt'), 'w') as f:
        f.write('testing')
    if not os.path.exists(os.path.join(test_data_path, 'script.yml')):
        log.info('script.yml not exist, please check if no cases planned')
        with open(get_current_dir('flag.txt'), 'w') as f:
            f.write('test finished')
        return
    with open(os.path.join(test_data_path, 'script.yml'), 'r') as f:
        scripts = yaml.safe_load(f)
    with open(os.path.join(test_data_path, 'additional.yml'), 'r') as f:
        additional = yaml.safe_load(f)
    for script in scripts:
        script_name, script_status = list(script.items())[0]
        if script_status.upper() == 'NORUN':
            log.info('Begin to Test case {}'.format(script_name))
            try:
                if need_reboot() == 1:
                    change_reboot_status(0)
                    reboot_command()
                memory_check(limit=MEMORY_LIMIT)
                globals()[script_name.split('__')[0]].start(
                    case_name=script_name.split('__')[1], kwargs=additional)
                script[script_name] = 'Finished'
                with open(os.path.join(test_data_path, 'script.yml'), 'w') as f:
                    yaml.safe_dump(scripts, f)
            except MemoryNotSufficient as e:
                log.debug(e)
                log.debug("start reboot")
                reboot_command()
            except:
                with open(get_current_dir('Test_Report', 'debug.log'), 'a') as f:
                    f.write(traceback.format_exc())
                capture_screen(get_current_dir('Test_Report', 'img', '{}.jpg'.format(script_name.split('__')[1]),))
                script[script_name] = 'Finished'
                with open(os.path.join(test_data_path, 'script.yml'), 'w') as f:
                    yaml.safe_dump(scripts, f)
                steps = {
                    'step_name': 'case exception',
                    'result': 'Fail',
                    'expect': '',  # can be string or pic path
                    'actual': 'img/{}.jpg'.format(script_name.split('__')[1]),
                    'note': traceback.format_exc()}
                base_name = get_report_base_name()
                report_file = get_current_dir('Test_Report', base_name)
                # result_file = get_current_dir(r'Test_Report', '{}.yaml'.format(check_ip_yaml()))
                update_cases_result(report_file, script_name.split('__')[1], steps)
        else:
            log.info('Test case {} status is Finished, Skip test'.format(script_name))
    if os.path.exists(path):
        if need_reboot() == 0:
            change_reboot_status(9)
            log.info("Start Reboot before Report")
            reboot_command()
        else:
            os.remove(path)
    if site:
        share_folder = content.get('share_folder')
        host = share_folder.split('/')[0]
        folder_path = '/'.join(share_folder.split('/')[1:])
        user = content.get('user')
        password = content.get('password')
        flag_path = '/{}/{}.txt'.format(folder_path, site)
        log.info('end_flag: {}'.format(flag_path))

        with open(get_current_dir('{}.txt'.format(site)), 'w') as f:
            f.write('test finished')
        ftp = FTPUtils(host, user, password)
        ftp.ftp.cwd('ThinPro_Automation_Site')
        local_folder = get_current_dir('Test_Report')
        ftp_folder = r'/{}/Test_Report'.format(folder_path)

        num = 0
        while True:
            try:

                ftp = FTPUtils(host, user, password)
                log.info('upload Test_Report folder to ftp')
                log.info(local_folder)
                log.info(ftp_folder)
                ftp.new_dir(ftp_folder)
                local_report = get_current_dir('Test_Report', '{}.yaml'.format(site))
                ftp_report = '/{}/Test_Report/{}.yaml'.format(folder_path, site)
                ftp.upload_file(local_report, ftp_report)
                ftp.upload_file(get_current_dir(r"{}.txt".format(site)), flag_path)
                break
            except:
                if num > 30:
                    traceback.print_exc()
                    break
                else:
                    num += 5
                    time.sleep(5)
    else:
        with open(get_current_dir('flag.txt'), 'w') as f:
            f.write('test finished')
        with open('time.txt') as f:
            start = f.read()
        end = time.ctime()
        report = email_tool.GenerateReport(start, end)
        report.generate()
        file = email_tool.zip_dir()
        log.info('zipped file name: {}'.format(file_obj))
        additional_email = additional.get('email') if additional.get('email') else ''
        email_tool.send_mail(recipient=['ecsrdtcqaautomation@hp.com', additional_email],
                             subject='Automation Report Linux {}'.format(
                                 zip_file_name(get_report_number(), get_report_value())),
                             attachment=file)
        os.remove(file)
        os.remove('time.txt')
        try:
            collect_report()
        except Exception as e:
            print(e)
            log.error(e)


if __name__ == '__main__':
    try:
        if not os.path.exists(get_current_dir('Test_Data', 'profile.xml')):
            export_profile()
        main()
        if os.path.exists(get_current_dir('Test_Data', 'profile.xml')):
            os.popen('rm {}'.format(get_current_dir('Test_Data', 'profile.xml')))
    except:
        log.error(traceback.format_exc())
