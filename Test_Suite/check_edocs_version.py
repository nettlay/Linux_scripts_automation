from Common.common_function import *
from Common.tool import get_root_path
from Test_Script.ts_precheck.precheck_function import SwitchThinProMode


def start(case_name, **kwargs):
    SwitchThinProMode(switch_to='admin')
    # ip = get_ip()
    ip = check_ip_yaml()
    path = get_root_path("Test_Report/{}.yaml".format(ip))
    filename = "check_edocs_version"
    new_cases_result(path, case_name)
    with os.popen('dpkg -l|grep docs') as f:
        rs = f.read()
        if 'hptc-regulatory-docs' in rs.lower():
            steps = {'step_name': filename,
                     'result': 'PASS',
                     'expect': 'hptc-regulatory-docs',  # can be string or pic path
                     'actual': 'hptc-regulatory-docs',  # can be string or pic path
                     'note': ''}
        elif 'no packages' in rs.lower():
            steps = {'step_name': filename,
                     'result': 'Fail',
                     'expect': 'hptc-regulatory-docs',  # can be string or pic path
                     'actual': 'No packages found matching hptc-regulatory-docs',  # can be string or pic path
                     'note': 'not install'}
        else:
            steps = {'step_name': filename,
                     'result': 'Fail',
                     'expect': 'No packages found matching hptc-regulatory-docs',  # can be string or pic path
                     'actual': '{}'.format(rs),  # can be string or pic path
                     'note': 'no key message'}
        update_cases_result(path, case_name, steps)


if __name__ == "__main__":
    start()
