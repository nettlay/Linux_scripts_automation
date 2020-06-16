from Common import common_function
from Common import report
from Test_Script.ts_precheck.precheck_function import SwitchThinProMode


class ConfigureCheck:

    def __init__(self):
        # self.target_os = common_function.load_global_parameters()['os'].strip()
        self.command_smartzero = 'dpkg -l | grep zero'
        self.string_zero = ['hptc-smart-zero-config', 'Configures ThinPro as Smart Zero during installation']
        self.log = common_function.log()
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
                print('SmartZero configuration is correct.')
                self.log.info('SmartZero configuration is correct.')
                return True
            else:
                print('SmartZero configuration is not correct.')
                self.log.info('SmartZero configuration is not correct.')
                return False
        else:
            # print('Fail to check SmartZero configuration. Current os is {}.'.format(current_os))
            # self.log.info('Fail to check SmartZero configuration. Current os is {}.'.format(current_os))
            # return False
            print('Skip SmartZero configuration check. Current os is {}.'.format(current_os))
            self.log.info('Skip SmartZero configuration check. Current os is {}.'.format(current_os))
            return False
        # else:
        #     print('Skip SmartZero configuration check for target os {}.'.format(self.target_os))
        #     self.log.info('Skip SmartZero configuration check for target os {}.'.format(self.target_os))
        #     return False


def start(case_name, **kwargs):
    SwitchThinProMode(switch_to='admin')
    report1 = report.Report(case_name)
    configure_check = ConfigureCheck()
    result = configure_check.check()
    if result is True:
        report1.reporter('Check smartzero configuration', 'Pass', 'smartzero', 'smartzero', 'none')
    elif result is False:
        report1.reporter('Check smartzero configuration', 'Fail', 'smartzero', 'not smartzero', 'none')
    else:
        report1.reporter('Check smartzero configuration', 'Fail', 'smartzero', 'fail to get target os', 'none')
    report1.generate()
