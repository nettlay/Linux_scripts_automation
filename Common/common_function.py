import datetime
import os, sys
import time
import platform
import re
import subprocess
import socket
import copy
import yaml
import pyautogui
from Common import file_transfer

pyautogui.FAILSAFE = False
import traceback
import cv2
import shutil
import pymouse, pykeyboard
from Common.file_transfer import FTPUtils
from Common.file_operator import YamlOperator
from Common.log import log, get_current_dir
from Common.exception import MemoryNotSufficient

mouse = pymouse.PyMouse()
kb = pykeyboard.PyKeyboard()
if 'windows' in platform.platform().lower():
    __OS = 'Windows'
    import win32api
    import win32con
else:
    __OS = 'Linux'


def collect_report():
    """
    collect report and send to ALM server for automated return result to ALM
    alm need addition.yml(case<->alm information), ip.yml(cases result)
    :return:
    #By: balance
    """
    # expect only ip.yml exist in test_report
    global_conf = YamlOperator(get_current_dir('Test_Data', 'td_common', 'global_config.yml')).read()
    ftp_svr = global_conf['alm_ftp']['server']
    ftp_user = global_conf['alm_ftp']['username']
    ftp_pass = global_conf['alm_ftp']['password']
    ftp_path = global_conf['alm_ftp']['report_path']
    result_file = get_folder_items(get_current_dir('Test_Report'), file_only=True, filter_name='.yaml')[0]
    log.info(f'[common][collect result]Get result file: {result_file}')
    prefix = time.strftime("test_%m%d%H%M%S", time.localtime())
    log.info('[common][collect result]Copy additional.yml and ip.yml to test report')
    shutil.copy(get_current_dir('Test_Data', 'additional.yml'),
                get_current_dir('Test_Report', '{}_add.yml'.format(prefix)))
    shutil.copy(get_current_dir('Test_Report', result_file),
                get_current_dir('Test_Report', '{}_result.yml'.format(prefix)))
    try:
        ftp = file_transfer.FTPUtils(ftp_svr, ftp_user, ftp_pass)
        ftp.change_dir(ftp_path)
        ftp.upload_file(get_current_dir('Test_Report', '{}_result.yml'.format(prefix)), '{}_result.yml'.format(prefix))
        ftp.upload_file(get_current_dir('Test_Report', '{}_add.yml'.format(prefix)), '{}_add.yml'.format(prefix))
        ftp.close()
        log.info('[common][collect result]upload report to ftp server')
    except:
        log.error('[common][collect result]FTP Fail Exception:\n{}'.format(traceback.format_exc()))


def export_profile():
    os.popen('mclient export root {}'.format(get_current_dir('Test_Data', 'profile.xml')))


def import_profile():
    os.popen('mclient import {}'.format(get_current_dir('Test_Data', 'profile.xml')))


def get_vdi_user():
    return 'autotest1'


# Function author: Nick
def now():
    now_time = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    return now_time


# Function author: Nick
def get_ip():
    if __OS == 'Linux':
        wired_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/eth0/IPv4/status")
        if wired_status == "1":
            sys_eth0_ip = subprocess.getoutput("ifconfig | grep eth0 -A 1 | grep -i 'inet'")
            result = re.search(r"(?i)(?:inet|inet addr)[: ]([\\.\d]+)", sys_eth0_ip)
            try:
                assert result, "Get eth0 ip fail"
                eth0_ip = result.group(1)
                return eth0_ip
            except AssertionError as e:
                pass

        wireless_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/wlan0/IPv4/status")
        if wireless_status == "1":
            sys_wlan0_ip = subprocess.getoutput("ifconfig | grep wlan0 -A 1 | grep -i 'inet'")
            result = re.search(r"(?i)(?:inet|inet addr)[: ]([\\.\d]+)", sys_wlan0_ip)
            try:
                assert result, "Get eth0 ip fail"
                wlan0_ip = result.group(1)
                return wlan0_ip
            except AssertionError as e:
                pass

        sys_eth1_ip = subprocess.getoutput("ifconfig | grep eth1 -A 1 | grep -i 'inet'")
        result = re.search(r"(?i)(?:inet|inet addr)[: ]([\\.\d]+)", sys_eth1_ip)
        if result:
            return result.group(1)
        else:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
    else:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip


def get_ip_from_yml():
    report_path = get_current_dir('Test_Report')
    files = os.walk(report_path)
    for file in files:
        if '.yaml' in file.lower():
            ip_addr = file.split('.').remove[-1]
            return '.'.join(ip_addr)
    return 'null'


# Function author: justin
def check_ip_yaml():
    ip_yaml_path = get_current_dir('Test_Data', 'ip.yml')
    if os.path.exists(ip_yaml_path):
        with open(ip_yaml_path, encoding='utf-8') as f:
            ip = yaml.safe_load(f)
            if ip:
                return ip[0]
            else:
                return '127.0.0.1'
    else:
        f = open(ip_yaml_path, 'w')
        f.close()
        with open(ip_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump([get_ip()], f, default_flow_style=False)
        return get_ip()


def get_platform():
    if __OS == 'Linux':
        platform = subprocess.getoutput('/usr/bin/hptc-hwsw-id --hw')
        if platform == '':
            log.info('Platform is empty.')
        return platform
    else:
        return False


def command_line(command):
    output = os.popen(command).readlines()
    return output


def load_global_parameters():
    # path = r'{}/Test_Data/additional.yml'.format(get_current_dir())
    path = os.path.join(get_current_dir(), 'Test_Data', 'additional.yml')
    data_dic = yaml.safe_load(open(path))
    return data_dic


def os_configuration():
    if __OS == 'Linux':
        os_config = subprocess.getoutput('mclient --quiet get tmp/SystemInfo/general/ProductConfig')
        if os_config.strip() == 'zero':
            return 'smart_zero'
        elif os_config.strip() == 'standard':
            return 'thinpro'
    else:
        pass


def argv_filter(argv_list):
    """
    input like: ["./././common_function.py", "site1", "//15.83.240.98/automation", "123456", "456789", "t630_config2"]
    return: site1 ('15.83.240.98', 'automation') 123456 456789 ['t630_config2']
    """
    argv_li = copy.deepcopy(argv_list[1:])
    length = len(argv_li)
    filter_list = []
    get_index_0 = lambda a: a[0] if a else " "
    if length == 5:
        path = "/".join(argv_li[1].split("\\"))
        path_list = re.findall(r".?.?(\d+\.\d+\.\d+\.\d+)/?(.*)", path, re.S)
        path_list = get_index_0(path_list)
        argv_li[1] = path_list
        filter_list = argv_li
    else:
        argv_str = " " + " ".join(argv_li) + " "
        filter_list.append(get_index_0(re.findall(r"-s[ite]{0,3}? (.*?) ", argv_str, re.S)))
        res = re.findall(r"-p[ath]{0,3}? (.*?) ", argv_str, re.S)
        if res:
            path = "/".join(res[0].split("\\"))
            filter_list.append(get_index_0(re.findall(r".?.?(\d+\.\d+\.\d+\.\d+)/?(.*)", path, re.S)))
        else:
            filter_list.append(("", ""))
        filter_list.append(get_index_0(re.findall("-u[ser]{0,3}? (.*?) ", argv_str, re.S)))
        filter_list.append(get_index_0(re.findall("-pass[word]{0,4}? (.*?) ", argv_str, re.S)))
        filter_list.append(get_index_0(re.findall("-config (.*?) ", argv_str, re.S)))
    return filter_list


def new_cases_result(file, case_name):
    result = [{'case_name': case_name,
               'uut_name': check_ip_yaml(),
               'result': 'Fail',
               'steps': []
               }]
    if not os.path.exists(file):
        f = open(file, 'w')
        f.close()
    with open(file, 'r') as f:
        current_report = yaml.safe_load(f)
    if isinstance(current_report, list):
        for report in current_report:
            if report['case_name'] == case_name:
                return
        current_report.extend(result)
    else:
        current_report = result

    with open(file, 'w') as f:
        yaml.safe_dump(current_report, f)


def update_cases_result(file, case_name, step):
    with open(file, 'r') as f:
        current_report = yaml.safe_load(f)
    for report in current_report:
        if report['case_name'] == case_name:
            report['steps'].append(step)
            case_status = True
            for sub_step in report['steps']:
                if sub_step['result'].upper() == 'FAIL':
                    case_status = False
                    break
            if case_status:
                report['result'] = 'Pass'
            else:
                report['result'] = 'Fail'
            break

    with open(file, 'w') as f:
        yaml.safe_dump(current_report, f)


def add_windows_user(username, password, group='users'):
    # Default group is Users
    os.system('net user /delete {}'.format(username))
    os.system('net user /add {} {}'.format(username, password))
    if group == 'Administrators':
        os.system('net localgroup Administrators {} /add'.format(username))
        return True
    else:
        return True


def switch_user(username="Admin", password="Admin", domain=""):
    """
    Before program, Please Add HKLM\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon
    To Registry exclusions of Write Filter
    """
    root = win32con.HKEY_LOCAL_MACHINE
    key = win32api.RegOpenKeyEx(root, 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon', 0,
                                win32con.KEY_ALL_ACCESS | win32con.KEY_WOW64_64KEY | win32con.KEY_WRITE)
    win32api.RegSetValueEx(key, "DefaultUserName", 0, win32con.REG_SZ, username)
    win32api.RegSetValueEx(key, "DefaultPassWord", 0, win32con.REG_SZ, password)
    if domain != "":
        win32api.RegSetValueEx(key, "DefaultDomain", 0, win32con.REG_SZ, domain)


def get_folder_items(path, **kwargs):
    """
    get folder items without recursion
    :param path: str, path like './Test_Report' or '/root/PycharmProjects/linux_automation_script2/Common'
    :return:
    """
    safe_mode = kwargs.get("safe_mode", True)
    filter_name = kwargs.get("filter_name", "")
    file_only = kwargs.get("file_only", False)
    file_path = "/".join(os.path.realpath(path).split("\\"))
    if not os.path.exists(file_path) and safe_mode:
        os.makedirs(file_path)
    file_list = os.listdir(file_path)
    if filter_name:
        filter_name_list = []
        for i in file_list:
            if filter_name.upper() in i.upper():
                filter_name_list.append(i)
        file_list = filter_name_list
    if file_only:
        for i in copy.deepcopy(file_list):
            dir_path = file_path + "/{}".format(i)
            if os.path.isdir(dir_path):
                file_list.remove(i)
    return file_list


def get_folder_items_recursion(path, **kwargs):
    file_list = get_folder_items(path, **kwargs)
    all_file = []
    for i in file_list:
        new_path = os.path.join(path, i)
        if "__pycache__" in new_path:
            continue
        elif os.path.isdir(new_path):
            all_file = all_file + get_folder_items_recursion(new_path, **kwargs)
        else:
            all_file.append(i)
    return all_file


# Function author: justin
def add_to_startup_script(i):
    with open('/writable/root/auto_start_setup.sh', 'a') as s:
        res = get_folder_items(get_current_dir(), file_only=True)
        if i in res:
            s.write("{}\n".format(get_current_dir() + '/' + i))
        elif '/' in i:
            s.write("{}\n".format(i))
    time.sleep(0.2)
    os.system("chmod 777 /writable/root/auto_start_setup.sh")
    time.sleep(0.2)


# Function author: justin
def add_linux_script_startup(script_name):
    src = '/root/auto_start_setup.sh'
    src_auto = get_current_dir("Test_Utility/auto.service")
    dst_auto = "/etc/systemd/system/auto.service"
    dst_wants = "/etc/systemd/system/multi-user.target.wants/auto.service"
    if os.path.exists(src):
        os.remove(src)
    os.system("fsunlock")
    time.sleep(0.2)
    with open('/etc/init/auto-run-automation-script.conf', 'w+') as f:
        f.write("start on lazy-start-40\nscript\n")
        f.write("\t/writable/root/auto_start_setup.sh\nend script\n")
    time.sleep(0.5)
    os.system("chmod 777 /etc/init/auto-run-automation-script.conf")
    os.system('fsunlock')
    time.sleep(0.1)
    bash_script = "#! /bin/bash\nsource /etc/environment\nsource /etc/profile\nexec 2>/root/log.log\nsleep 50\nexport DISPLAY=:0\nfsunlock\ncd /root\n"
    with open('/writable/root/auto_start_setup.sh', 'w+') as s:
        s.write(bash_script)
        res = get_folder_items(get_current_dir(), file_only=True)
        if type(script_name) == list:
            for i in script_name:

                if i in res:
                    s.write("sudo {}\n".format(os.path.join(get_current_dir(), i)))
                elif '/' in i:
                    s.write("sudo {}\n".format(i))
        else:
            if script_name in res:
                s.write("sudo {}\n".format(os.path.join(get_current_dir(), script_name)))
            elif '/' in script_name:
                s.write("sudo {}\n".format(script_name))
    time.sleep(0.2)
    os.system("chmod 777 /writable/root/auto_start_setup.sh")
    time.sleep(0.2)
    if not os.path.exists(dst_auto):
        shutil.copyfile(src_auto, dst_auto)
        time.sleep(1)
        os.system("ln -s {} {}".format(dst_auto, dst_wants))
    return False


# Function author: justin
def linux_rm_startup_script(name=''):
    os.system("fsunlock")
    time.sleep(0.2)
    if name:
        if type(name) == list:
            for s in name:
                batch_rm_startup_script(s)
        else:
            batch_rm_startup_script(name)
    else:
        os.system("rm /etc/init/auto-run-automation-script.conf")
        os.system("rm /writable/root/auto_start_setup.sh")
    time.sleep(0.1)


# Function author: justin
def batch_rm_startup_script(name):
    if '/' in name:
        with open('/root/auto_start_setup.sh', 'r') as f:
            lis = f.readlines()
            print(lis)
            for i in lis:
                if i.strip('\n').split('/') == name.split('/'):
                    print(i.strip('\n').split('/'), name.split('/'))
                    lis.remove(i)
        with open('/root/auto_start_setup.sh', 'w') as f:
            print(lis)
            for i in lis:
                f.write(i)
    else:
        os.system('sed -i "/{}/d" /root/auto_start_setup.sh'.format(name))


def open_window(name):
    log.info("start move mouse")
    pyautogui.moveTo(100, 1)
    time.sleep(1)
    log.info("start send ctrl alt s")
    pyautogui.hotkey('ctrl', 'alt', 's')
    time.sleep(5)
    log.info("start type {}".format(name))
    pyautogui.typewrite(name)
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(3)
    log.info("end")


def open_window_with_check(name, picture):
    pyautogui.moveTo(1, 1)
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'alt', 's')
    time.sleep(2)
    pyautogui.typewrite(name)
    time.sleep(2)
    pyautogui.press('enter')
    if check_window("F", picture):
        return True
    else:
        return False


def close_window():
    time.sleep(3)
    pyautogui.hotkey('ctrl', 'alt', 'f4')


def close_window_with_check(picture):
    time.sleep(3)
    pyautogui.hotkey('ctrl', 'alt', 'f4')
    if check_window("T", picture):
        return True
    else:
        return False


def check_window(runflag, picture):
    count = 0
    time.sleep(3)
    if runflag == "F":
        while count <= 5:
            system_window = pyautogui.locateOnScreen(picture)
            print(system_window)
            if system_window is not None:
                log.info("window opens successfully")
                return True
            else:
                log.info("window opens failed!")
                count += 1
                time.sleep(1)
                if count == 6:
                    return False
    else:
        while count <= 5:
            system_window = pyautogui.locateOnScreen(picture)
            print(system_window)
            if system_window is None:
                log.info("window closes successfully")
                return True
            else:
                log.info("window closes failed!")
                count += 1
                if count == 6:
                    return False


def delete_folder(top):
    import os
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def show_desktop():
    time.sleep(20)
    pyautogui.hotkey('ctrl', 'alt', 'end')


def logoff():
    show_desktop()
    time.sleep(1)
    pyautogui.rightClick()
    time.sleep(1)
    pyautogui.hotkey("up")
    time.sleep(1)
    pyautogui.hotkey("enter")
    time.sleep(1)
    pyautogui.hotkey("enter")
    time.sleep(1)
    pyautogui.hotkey("enter")


def reboot():
    show_desktop()
    time.sleep(1)
    pyautogui.rightClick()
    time.sleep(1)
    pyautogui.hotkey("up")
    time.sleep(1)
    pyautogui.hotkey("enter")
    time.sleep(1)
    pyautogui.hotkey("down")
    time.sleep(1)
    pyautogui.hotkey("down")
    time.sleep(1)
    pyautogui.hotkey("enter")
    time.sleep(1)
    pyautogui.hotkey("enter")


def get_position(img, region=None, similaity=0.97,base_dir = os.path.join(get_current_dir(), 'Test_Data', 'td_power_manager', 'AD')):
    # img=os.path.join(os.getcwd(),"Test_Data","import_cert_and_lunch_firefox",img)
    if base_dir:
        img = os.path.join(base_dir, img)
    # print(img)
    count = 5
    count1 = count
    while count:
        part_img = cv2.imread(img, 0)
        w, h = part_img.shape[::-1]
        if region is None:
            pyautogui.screenshot().save("temp.png")
            full_img = cv2.imread("temp.png", 0)
            res = cv2.matchTemplate(part_img, full_img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > similaity:
                # print("find :" + img + " with similaity " + str(max_val) + " in full screen")
                log.info("find :" + img + " with similaity " + str(max_val) + " in full screen")
                return (max_loc[0], max_loc[1], w, h), (int(max_loc[0] + w / 2), int(max_loc[1] + h / 2))
            else:
                # print("Not find :" + img + " with similaity " + str(max_val) + "in region:" + str(region))
                log.info("Not find :" + img + " with similaity " + str(max_val) + "in region:" + str(region))
        else:
            pyautogui.screenshot(region=region).save("temp.png")
            full_img = cv2.imread("temp.png", 0)
            res = cv2.matchTemplate(part_img, full_img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > similaity:
                # print("find :"+img+" with similaity "+str(max_val)+"in region:"+str(region))
                log.info("find :" + img + " with similaity " + str(max_val) + "in region:" + str(region))
                return (max_loc[0], max_loc[1], w, h), (int(max_loc[0] + w / 2), int(max_loc[1] + h / 2))
            else:
                # print("Not find :" + img + " with similaity " + str(max_val) + "in region:" + str(region))
                log.info("Not find :" + img + " with similaity " + str(max_val) + "in region:" + str(region))

        count = count - 1
        # print("can not find :" + img + " :wait 1s repeat")
        log.info("can not find :" + img + " :wait 1s repeat")
    # print("can not find " + img + " in "+str(count1)+" repeats")
    log.info("can not find " + img + " in " + str(count1) + " repeats")
    return False


class SwitchThinProMode:
    """
    switch thinpro to admin mode or user mode
    SwitchThinProMode(switch_to='admin')
    """

    def __init__(self, switch_to, **kwargs):

        self.switch_to = str(switch_to).lower()
        self.password = kwargs.get("password", "1")
        self.switch_mode()

    @staticmethod
    def current_mode():
        s = os.path.exists('/var/run/hptc-admin')
        if s:
            return 'admin'
        else:
            return 'user'

    @staticmethod
    def judge_has_root_pw():
        s = subprocess.call("hptc-passwd-default --root --check >/dev/null 2>&1", shell=True)
        if s:
            return True
        else:
            return False

    def switch_mode(self):
        if self.switch_to == 'user':
            if self.current_mode() == 'user':
                log.info("now is user mode")
                return True
            if self.current_mode() == 'admin':
                for _ in range(3):
                    os.popen('hptc-switch-admin')
                    time.sleep(2)
                    if self.current_mode() == 'user':
                        log.info("switch to user mode success")
                        return True
                    log.error("switch to user fail, try again")
                    time.sleep(2)
                else:
                    log.error("switch to user mode fail")
                    return False

        if self.switch_to == 'admin':
            if self.current_mode() == 'admin':
                log.info("now is admin mode")
                return True
            if self.current_mode() == 'user':
                log.info("change mode user")
                if self.judge_has_root_pw():
                    os.popen('hptc-switch-admin')
                    time.sleep(3)
                    # kb.type_string(self.password)
                    # time.sleep(1)
                    # kb.tap_key(kb.enter_key)
                    pyautogui.typewrite(self.password)
                    time.sleep(2)
                    pyautogui.press('enter')
                    time.sleep(2)
                    if self.current_mode() == 'admin':
                        log.info("switch to admin mode success")
                        return True
                    else:
                        kb.tap_key(kb.enter_key)
                        time.sleep(1)
                        kb.type_string('root')
                        time.sleep(1)
                        kb.tap_key(kb.tab_key)
                        time.sleep(1)
                        kb.type_string(self.password)
                        time.sleep(1)
                        kb.tap_key(kb.enter_key)
                        time.sleep(1)
                        if self.current_mode() == 'admin':
                            log.info("switch to admin mode success")
                            return True
                        else:
                            log.info("switch to admin mode fail")
                            return False

                if not self.judge_has_root_pw():
                    os.popen('hptc-switch-admin')
                    time.sleep(2)
                    kb.type_string(self.password)
                    time.sleep(1)
                    kb.tap_key(kb.tab_key)
                    time.sleep(1)
                    kb.type_string(self.password)
                    time.sleep(1)
                    kb.tap_key(kb.enter_key)
                    time.sleep(2)
                    if self.current_mode() == 'admin':
                        log.info("switch to admin mode success")
                        return True
                    else:
                        log.error("switch to admin mode fail")
                        return False


def screen_resolution():
    return pyautogui.size()


def case_steps_run_control(steps_list, name, *args, **kwargs):
    case_steps_file = os.path.join(get_current_dir(), "{}_case_steps.yml".format(name))
    if not os.path.exists(case_steps_file):
        list_dict = {}
        for s in steps_list:
            list_dict[s] = "norun"
        steps_yml = YamlOperator(case_steps_file)
        steps_yml.write(list_dict)

    steps_yml = YamlOperator(case_steps_file)
    for step in steps_list:
        steps_dict = steps_yml.read()
        for key, value in steps_dict.items():
            if step == key and value.lower() != "finished":
                steps_dict[key] = "finished"
                steps_yml.write(steps_dict)
                result = getattr(sys.modules[name], step)(*args, **kwargs)
                # result = eval(key)
                if result is False:
                    os.remove(case_steps_file)
                    return False
        if steps_list.index(step) == len(steps_list) - 1:
            os.remove(case_steps_file)
            return True


def load_data_from_ftp():
    file_obj = YamlOperator(get_current_dir('Test_Data', 'td_common', 'global_config.yml'))
    content = file_obj.read()
    ftp_server = content['td_ftp']['server']
    ftp_user = content['td_ftp']['username']
    ftp_passwd = content['td_ftp']['password']
    td_path = content['td_ftp']['td_path']
    try:
        ftp = FTPUtils(ftp_server, ftp_user, ftp_passwd)
        ftp.change_dir(td_path)
        folders = ftp.get_item_list('')
        for folder in folders:
            if not ftp.is_item_file(folder):
                ftp.download_dir(folder, get_current_dir(folder))
        ftp.close()
    except:
        log.error('ftp exception:\n{}'.format(traceback.format_exc()))


def prepare_for_framework():
    file_path = get_current_dir('Test_Data', 'additional.yml')
    file_obj = YamlOperator(file_path)
    content = file_obj.read()
    site = content.get('AutoDash_Site')
    if site:
        return
    else:
        user_defined_data = get_current_dir('Test_Data', 'User_Defined_Data')
        if os.path.exists(user_defined_data):
            log.info('removing {}'.format(user_defined_data))
            shutil.rmtree(user_defined_data)
            time.sleep(3)
        for k, v in content.items():
            if 'User_Defined_Data'.upper() in str(k).upper():
                log.info('will download user data')
                break
        else:
            log.info('no uer defined data to be download')
            return
        file = get_current_dir('Test_Data', 'ftp_config.yaml')
        fo = YamlOperator(file)
        ftp_para = fo.read()
        for k, v in content.items():
            if 'User_Defined_Data'.upper() in str(k).upper():
                source = str(v)
                linux_path = source.replace('\\', '/')
                host = linux_path.split('/')[2]
                for each in ftp_para:
                    ip = each.get('ip')
                    user = each.get('user')
                    password = each.get('password')
                    if ip == host:
                        break
                else:
                    log.info('ftp_config.yaml has no parameters for {}'.format(host))
                    continue
                log.info('download user data from {} to UUT'.format(host))
                last_level_folder = os.path.split(linux_path)[1]
                folder_path = '/'.join(linux_path.split('/')[3:])
                if last_level_folder.upper() in ['USER_DEFINED_DATA']:
                    dst = get_current_dir('Test_Data', last_level_folder)
                else:
                    dst = get_current_dir('Test_Data', 'User_Defined_Data', last_level_folder)
                n = 0
                while True:
                    try:
                        log.info('download {} to {}'.format(source, dst))
                        ftp = FTPUtils(host, user, password)
                        ftp.download_dir(folder_path, dst)
                        break
                    except:
                        if n > 30:
                            log.info(traceback.format_exc())
                            break
                        else:
                            n += 5
                            time.sleep(5)


class Run_App():
    def __init__(self, path, shell=False):
        self.app_path = path
        self.instance: subprocess.Popen = None
        self.shell = shell

    def start(self):
        self.instance = subprocess.Popen(self.app_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         shell=self.shell)
        time.sleep(2)

    def check_status(self):
        if self.check_instance():
            if self.instance.poll() is None:
                log.info("instance is running")
                return True
            else:
                log.info("instance have end")
                return False

    def stop(self):
        if self.check_instance():
            if self.app_path == "gpedit.msc":
                subprocess.Popen('taskkill /im "mmc.exe" /f')
                return
            if self.app_path == "osk.exe":
                subprocess.Popen('taskkill /im "osk.exe" /f')
                return
            if self.app_path == "C:\Windows\system32\mstsc.exe":
                subprocess.Popen('taskkill /im "mstsc.exe" /f')
                return
            self.instance.terminate()

    def get_stdout(self):
        if self.check_instance():
            return self.instance.stdout.read()

    def get_error(self):
        if self.check_instance():
            return self.instance.stderr.read()

    def wait(self):
        if self.check_instance():
            self.instance.wait()

    def get_pid(self):
        if self.check_instance():
            return self.instance.pid

    def check_instance(self):
        if self.instance:
            log.info("instance exist")
            return True
        else:
            log.info("instance is None")
            return False


def import_cert(cert="ROOTCA.pem"):
    time.sleep(1)
    log.info("start import certificate")
    rootca_pem_1 = os.path.exists("/etc/ssl/certs/ROOTCA.pem")
    if rootca_pem_1:
        log.info("certificate is already exist")
        return True
    else:
        log.info("certificate not exist, start install cert")
        shutil.copy(os.path.join(get_current_dir(), 'Test_Utility', 'ROOTCA.pem'),
                    '/usr/local/share/ca-certificates/ROOTCA.pem')
        time.sleep(0.2)
        c = os.path.exists("/usr/local/share/ca-certificates/{}".format(cert))
        if not c:
            log.error('copy cert fail')
            return False
        log.info('copy cert success')
        subprocess.getstatusoutput("/usr/bin/hptc-cert-mgr --apply")
        time.sleep(4)
        rootca_pem_2 = os.path.exists("/etc/ssl/certs/ROOTCA.pem")
        if not rootca_pem_2:
            log.error('install certificates fail')
            return False
        else:
            log.info('install certificates success')
            time.sleep(1)
            return True


def get_report_base_name():
    additional_path = get_current_dir('Test_Data', 'additional.yml')
    if os.path.exists(additional_path):
        file_obj = YamlOperator(additional_path)
        content = file_obj.read()
        site = content.get('AutoDash_Site')
    else:
        site = None
    if site:
        base_name = '{}.yaml'.format(site)
    else:
        base_name = '{}.yaml'.format(check_ip_yaml())
    return base_name


def check_free_memory(status="before"):
    os.system(f"echo {status}: >> free.txt")
    os.system("free >> free.txt")


def log_cache(dtype="-k",  relative_path="free.txt"):
    """
    command: free
    relative_path: path start from the project
     -b, --bytes         show output in bytes
         --kilo          show output in kilobytes
         --mega          show output in megabytes
         --giga          show output in gigabytes
         --tera          show output in terabytes
         --peta          show output in petabytes
    -k, --kibi          show output in kibibytes
    -m, --mebi          show output in mebibytes
    -g, --gibi          show output in gibibytes
         --tebi          show output in tebibytes
         --pebi          show output in pebibytes
    -h, --human         show human-readable output
         --si            use powers of 1000 not 1024

    """
    path = get_current_dir(relative_path)
    os.system(f"free {dtype} >> {path}")
    return path


def cache_collection(level: int = 1):
    """
    params: level, int,
        0: not release cache
        1: release page cache
        2: release both dentries and inodes cache
        3: release both 1 and 2
    """
    os.system(f"echo {level} > /proc/sys/vm/drop_caches")


def memory_check(dtype="-m", limit: int = 300, strict_mode=True):
    """
    check memeory > limit
    raise ValueError if strict_mode is Ture else return False
    """
    try:
        res = os.popen(f"free {dtype}").readlines()
        line_name = res[0]
        line_value = res[1]
        index = line_name.index("available")
        available_str = line_value[index: index + len("available")].strip("kbgyteKBGYTE ")
        avail = float(available_str)
        print(avail)
    except Exception as e:
        log.error(e)
        return -1
    if avail < limit and strict_mode:
        raise MemoryNotSufficient("current Memory is not sufficient! Current: {}".format(avail))
    elif avail < limit:
        return False
    return True


def get_global_config(*keys):
    """
    :params: keys, tuple
    if key not exist, raise ValueError
    """
    file_dict = {}
    path = get_current_dir('Test_Data/td_common/global_config.yml')
    if os.path.exists(path):
        file_obj = YamlOperator(path)
        file_dict = file_obj.read()
    else:
        log.warning("Not Exist {}".format(path))
    if not keys:
        return file_dict
    new_value = copy.deepcopy(file_dict)
    for i in keys:
        value = new_value.get(i, None) if isinstance(new_value, dict) else None
        if not value:
            index = keys.index(i)
            raise ValueError("Key not Exist, origin: {}".format(" -> ".join(keys[:index+1])))
        new_value = value
    return new_value


def check_water_mark():
    path = "/usr/lib/hptc-watermark"
    if os.path.exists(path):
        os.system("rm -r {}".format(path))
        os.system("reboot")
        time.sleep(10)


def reboot_command():
    os.system("reboot")
    time.sleep(15)


def change_reboot_status(status=1):
    path = get_current_dir("reboot.txt")
    with open(path, "w") as f:
        f.write(str(status))


def need_reboot() -> int:
    """
     0: not need reboot
     another: need reboot
     """
    path = get_current_dir("reboot.txt")
    if not os.path.exists(path):
        return 0
    with open(path, "r") as f:
        res = f.read().strip()
    if not res:
        return 0
    return int(res)
