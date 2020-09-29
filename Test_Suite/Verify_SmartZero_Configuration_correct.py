from Common import common_function
from Test_Script.ts_precheck.precheck_function import SwitchThinProMode
from Test_Script.ts_precheck import network_function
from Common.tool import get_root_path


class ConfigureCheck:

    def __init__(self):
        # self.target_os = common_function.load_global_parameters()['os'].strip()
        self.command_smartzero = 'dpkg -l | grep zero'
        self.string_zero = ['hptc-smart-zero-config', 'Configures ThinPro as Smart Zero during installation']
        self.log = common_function.log
        self.log.info("-" * 60)
        self.log.info("case name: verify smartzero configuration correct")

    def check(self):
        current_os = common_function.os_configuration()
        if current_os.lower() == 'smart_zero':
            output = common_function.command_line(self.command_smartzero)[0]
            string_match = 0
            for string in self.string_zero:
                if string in output:
                    string_match += 1
            if string_match == len(self.string_zero):
                self.log.info('SmartZero configuration is correct.')
                return 'pass'
            else:
                self.log.info('SmartZero configuration is not correct.')
                return 'fail'
        else:
            # print('Fail to check SmartZero configuration. Current os is {}.'.format(current_os))
            # self.log.info('Fail to check SmartZero configuration. Current os is {}.'.format(current_os))
            # return False
            self.log.info('Skip SmartZero configuration check. Current os is {}.'.format(current_os))
            return 'NA'
        # else:
        #     print('Skip SmartZero configuration check for target os {}.'.format(self.target_os))
        #     self.log.info('Skip SmartZero configuration check for target os {}.'.format(self.target_os))
        #     return False


def start(case_name, **kwargs):
    SwitchThinProMode(switch_to='admin')
    # report_file = network_function.system_ip() + '.yaml'
    ip = common_function.check_ip_yaml()
    report_file = get_root_path("Test_Report/{}.yaml".format(ip))
    common_function.new_cases_result(report_file, case_name)  # new report
    configure_check = ConfigureCheck()
    result = configure_check.check()
    if result == 'pass':
        step1 = {'step_name': 'Check smartzero configuration',
                 'result': 'Pass',
                 'expect': 'smartzero',
                 'actual': 'smartzero',
                 'note': 'none'}
    elif result == 'NA':
        step1 = {'step_name': 'Check smartzero configuration',
                 'result': 'Fail',
                 'expect': 'current os',
                 'actual': 'current os is not smartzero',
                 'note': 'none'}
    else:
        step1 = {'step_name': 'Check smartzero configuration',
                 'result': 'Fail',
                 'expect': 'smartzero',
                 'actual': 'fail to get target os',
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step1)
