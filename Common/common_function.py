import datetime
import logging
import os
import platform
import re
import subprocess
import sys
import socket
import copy
import yaml

if 'windows' in platform.platform().lower():
    __OS = 'Windows'
    import win32api
    import win32con
else:
    __OS = 'Linux'


# Function author: Balance
def get_current_dir():
    if os.path.dirname(sys.argv[0]) == '':
        return os.getcwd()
    else:
        return os.path.dirname(sys.argv[0])


def get_vdi_user():
    return 'autotest1'


# Function author: Nick
def now():
    now_time = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    return now_time


# Function author: Nick
def log():
    logger = logging.getLogger()
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    if not os.path.exists(os.path.join(get_current_dir(), 'Test_Report')):
        os.makedirs(os.path.join(get_current_dir(), 'Test_Report', 'log'))
    else:
        if not os.path.exists(os.path.join(get_current_dir(), 'Test_Report', 'log')):
            os.mkdir(os.path.join(get_current_dir(), 'Test_Report', 'log'))
    log_name = now() + '.log'
    file = os.path.join(get_current_dir(), 'Test_Report', 'log', log_name)
    if not logger.handlers:
        # StreamHandler
        stream_handler = logging.StreamHandler(sys.stdout)
        # stream_handler.setLevel(level=logging.ERROR)    # only show log.error message
        stream_handler.setLevel(level=logging.INFO)  # show log.info and log.error message
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # FileHandler
        file_handler = logging.FileHandler(file, mode='a')
        file_handler.setLevel(level=logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


# Function author: Nick
def get_ip():
    if __OS == 'Linux':
        wired_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/eth0/IPv4/status")
        if wired_status == "1":
            sys_eth0_ip = subprocess.getoutput("ifconfig | grep eth0 -A 1 | grep -i 'inet addr'")
            eth0_ip = sys_eth0_ip.strip().split()[1].split(":")[1]
            return eth0_ip

        wireless_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/wlan0/IPv4/status")
        if wireless_status == "1":
            sys_wlan0_ip = subprocess.getoutput("ifconfig | grep wlan0 -A 1 | grep -i 'inet addr'")
            wlan0_ip = sys_wlan0_ip.strip().split()[1].split(":")[1]
            return wlan0_ip
        else:
            with os.popen("ifconfig") as f:
                string = f.read()
                eth0_ip = re.findall("eth0.*?addr.*?(\d+\.\d+\.\d+\.\d+).*?lo", string, re.S)
                if eth0_ip:
                    eth0_ip = eth0_ip[0]
                else:
                    eth0_ip = get_ip_from_yml()
            return eth0_ip
    else:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip


def get_ip_from_yml():
    report_path = os.path.join(get_current_dir(), 'Test_Report')
    files = os.walk(report_path)
    for file in files:
        if '.yaml' in file.lower():
            ip_addr = file.split('.').remove[-1]
            return '.'.join(ip_addr)
    return 'null'


def get_platform():
    if __OS == 'Linux':
        platform = subprocess.getoutput('/usr/bin/hptc-hwsw-id --hw')
        if platform == '':
            log().info('Platform is empty.')
        return platform
    else:
        pass


def command_line(command):
    output = os.popen(command).readlines()
    return output


def load_global_parameters():
    # path = r'{}/Test_Data/additional.yml'.format(get_current_dir())
    path = os.path.join(get_current_dir(), 'Test_Data', 'all_additional.yml')
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
    argvs = sys.argv
    if argvs[1:]:
        site, host_list, user, password, *params = argv_filter(argvs)
        file = os.path.join(os.path.split(file)[0], "{}.yaml".format(site))
    result = [{'case_name': case_name,
               'uut_name': get_ip(),
               'result': 'Pass',
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


def update_cases_result(file, case_name, steps):
    argvs = sys.argv
    if argvs[1:]:
        site, host_list, user, password, *params = argv_filter(argvs)
        file = os.path.join(os.path.split(file)[0], "{}.yaml".format(site))
    with open(file, 'r') as f:
        current_report = yaml.safe_load(f)
    for report in current_report:
        if report['case_name'] == case_name:
            report['steps'].append(steps)
            if steps['result'].upper() == 'FAIL':
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
