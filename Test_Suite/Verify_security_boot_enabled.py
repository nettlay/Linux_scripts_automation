from Common import common_function
from Test_Script.ts_precheck import network_function
import yaml
import os
import subprocess
from Test_Script.ts_precheck.precheck_function import SwitchThinProMode
from Common.tool import get_root_path
from Common.common_function import *


class SecurityBoot:
    def __init__(self):
        self.para = common_function.load_global_parameters()
        self.target_platform = self.para['platform']
        self.current_path = common_function.get_current_dir()
        self.log = common_function.log
        self.log.info("-" * 60)
        self.log.info("case name: Verify_security_boot_enabled")

    def security_boot_platform_list(self):
        path = self.current_path + '/Test_Data/User_Defined_Data/td_precheck/check_security_boot.yml'
        data_lst = yaml.safe_load(open(path))
        return data_lst

    def security_boot_value_lst(self, platform_type):
        if os.path.exists('{}/Test_Data/td_precheck/bios.txt'.format(self.current_path)):
            os.system('rm {}/Test_Data/td_precheck/bios.txt'.format(self.current_path))
        os.system('hptc-bios-cfg -G {}/Test_Data/td_precheck/bios.txt'.format(self.current_path))
        if platform_type == 'DTC':
            secure_boot_key_name = 'Secure Boot'
            secure_boot_value_items = 2
        elif platform_type == 'MTC':
            secure_boot_key_name = 'Configure Legacy Support and Secure Boot'
            secure_boot_value_items = 3
        else:
            self.log.info('Invalid platform type {}.'.format(platform_type))
            return False
        secure_boot_row = subprocess.getoutput('grep ^\"{0}\" {1}/Test_Data/td_precheck/bios.txt -n -a | cut -f1 -d:'.format(
            secure_boot_key_name, self.current_path))
        secure_boot_content_command = 'sed -n \'{0}, {1}p\' {2}/Test_Data/td_precheck/bios.txt'.format(int(secure_boot_row) + 1,
                                                                                           int(secure_boot_row) +
                                                                                           secure_boot_value_items,
                                                                                           self.current_path)
        secure_boot_content_lst = os.popen(secure_boot_content_command).readlines()
        return secure_boot_content_lst

    def check_security_boot(self, platform_type):
        platform_lst = self.security_boot_platform_list()
        current_platform = common_function.get_platform()
        if not current_platform:
            return 'current platform is empty'
        if not self.target_platform == current_platform.upper():
            self.log.info('Target platform is not match with current platform. Current is {}.'.format(current_platform))
            return 'platform mismatch'
        if self.target_platform not in platform_lst:
            self.log.info('Skip checking security boot for target platform {}.'.format(self.target_platform))
            return 'skip checking'
        else:
            secure_boot_value_lst = self.security_boot_value_lst(platform_type)
            if secure_boot_value_lst:
                for element in secure_boot_value_lst:
                    if not element:
                        continue
                    if '*' not in element:
                        continue
                    element = element.strip()
                    if platform_type == 'DTC':
                        if '*Enable' in element:
                            self.log.info('Security boot check PASS for platform {0}, it is {1}'.format(self.target_platform,
                                                                                                        element))
                            return True
                        elif '*Disable' in element:
                            self.log.info('Security boot check Fail for platform {0}, it is {1}'.format(self.target_platform,
                                                                                                        element))
                            return '*Disable'
                        else:
                            self.log.info('Invalid value {} for Security Boot.'.format(element))
                            return 'invalid value for Security Boot'
                    elif platform_type == 'MTC':
                        if '*' in element:
                            if 'Secure Boot Enable' in element:
                                self.log.info('Security boot check PASS for platform {0}. It is enabled'.format
                                              (self.target_platform))
                                return True
                            else:
                                self.log.info('Security boot check Fail for platform {0}. It is disabled'.format
                                              (self.target_platform))
                                return 'secure boot disabled'
                        else:
                            continue
                self.log.error('Invalid security boot check.')
                return 'invalid secure boot check'
            else:
                self.log.info('Failed to get Security Boot value.')
                return 'fail to get secure boot value'


def start(case_name, **kwargs):
    SwitchThinProMode(switch_to='admin')
    # report_file = network_function.system_ip() + '.yaml'
    # ip = common_function.check_ip_yaml()
    # report_file = get_root_path("Test_Report/{}.yaml".format(ip))
    base_name = get_report_base_name()
    report_file = get_current_dir('Test_Report', base_name)
    common_function.new_cases_result(report_file, case_name)  # new report
    security_boot = SecurityBoot()
    current_platform = common_function.get_platform()
    if current_platform[0] == 't':
        platform_type = 'DTC'
    elif current_platform[0] == 'm':
        platform_type = 'MTC'
    else:
        step1 = {'step_name': 'Check platform type',
                 'result': 'Fail',
                 'expect': 'DTC or MTC',
                 'actual': 'invalid platform type',
                 'note': 'none'}
        common_function.update_cases_result(report_file, case_name, step1)
        return
    check_result = security_boot.check_security_boot(platform_type)
    if check_result is True:
        step2 = {'step_name': 'Check whether security boot enabled or not',
                 'result': 'Pass',
                 'expect': 'Enable',
                 'actual': 'Disable',
                 'note': 'none'}
    elif check_result == 'skip checking':
        step2 = {'step_name': 'Check whether security boot enabled or not',
                 'result': 'Fail',
                 'expect': 'Skip checking security boot',
                 'actual': 'Skip checking security boot for platform {}'.format(security_boot.target_platform),
                 'note': 'none'}
    else:
        step2 = {'step_name': 'Check whether security boot enabled or not',
                 'result': 'Fail',
                 'expect': 'Enable',
                 'actual': check_result,
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step2)



