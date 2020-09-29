from Test_Script.ts_network.network_proxy_class import ProxyTest
from Common import common_function
from Test_Script.ts_network import network_steps


def clear_proxy(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    proxy_test = kwargs.get('obj')
    rs = network_steps.clear_proxy(proxy_test, case_name, report_file)
    if rs:
        proxy_test.reboot()
    else:
        proxy_test.reset_env_halfway()
    return rs


def access_website_before(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    proxy_test = kwargs.get('obj')
    rs = network_steps.access_website_before(proxy_test, case_name, report_file)
    if rs:
        proxy_test.reboot()
    else:
        proxy_test.reset_env_halfway()
    return rs


def set_proxy1(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    proxy_test = kwargs.get('obj')
    rs = network_steps.set_proxy1(proxy_test, case_name, report_file)
    if rs:
        proxy_test.reboot()
    else:
        proxy_test.reset_env_halfway()
    return rs


def access_website_after(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    proxy_test = kwargs.get('obj')
    rs = network_steps.access_website_after(proxy_test, case_name, report_file)
    proxy_test.reset_env_last()
    return rs


def finish(**kwargs):
    proxy_test = kwargs.get('obj')
    return network_steps.finish(proxy_test)


def start(case_name, kwargs):
    steps_list = (
        "clear_proxy",
        "access_website_before",
        "set_proxy1",
        "access_website_after",
        "finish"
    )
    https_test = ProxyTest('https')
    result_file = common_function.get_current_dir(r'Test_Report', '{}.yaml'.format(common_function.check_ip_yaml()))
    common_function.new_cases_result(result_file, case_name)
    common_function.case_steps_run_control(steps_list, __name__, case_name=case_name,
                                           report_file=result_file, obj=https_test)
