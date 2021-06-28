from Common.log import log
from Common import common_function


def clear_proxy(proxy_test, case_name, report_file):
    protocol_name = proxy_test.protocol
    msg = 'step - - clear {} proxy'.format(protocol_name)
    log.info(msg)
    steps = {
        'step_name': '',
        'result': '',
        'expect': '',
        'actual': '',
        'note': ''}
    if proxy_test.set_proxy(''):
        step_rs = 'Pass'
        fun_rs = True
        msg2 = 'succeed to clear proxy'
    else:
        step_rs = 'Fail'
        fun_rs = False
        msg2 = 'Failed to clear proxy'
    msg3 = 'network panel can be edit'
    steps['step_name'] = msg
    steps['actual'] = msg2
    steps['expect'] = msg3
    steps['result'] = step_rs
    log.info('test {}'.format(step_rs))
    common_function.update_cases_result(report_file, case_name, steps)
    return fun_rs


def access_website_before(proxy_test, case_name, report_file):
    msg = 'step - - access website before setting proxy'
    log.info(msg)
    steps = {
        'step_name': '',
        'result': '',
        'expect': '',
        'actual': '',
        'note': ''}
    url = proxy_test.host_name
    if not proxy_test.access_website():
        step_rs = 'Pass'
        fun_rs = True
        msg2 = 'failed to access {}'.format(url)
    else:
        step_rs = 'Fail'
        fun_rs = False
        msg2 = 'succeed to access {}'.format(url)
    msg3 = '{} can not be accessed'.format(url)
    steps['step_name'] = msg
    steps['actual'] = msg2
    steps['expect'] = msg3
    steps['result'] = step_rs
    log.info('test {}'.format(step_rs))
    common_function.update_cases_result(report_file, case_name, steps)
    # if fun_rs:
    #     proxy_test.reboot()
    # else:
    #     proxy_test.reset_env_halfway()
    return fun_rs


def set_proxy_common(proxy_test, proxy_server, case_name, report_file):
    protocol_name = proxy_test.protocol
    msg = 'step - - set {} proxy to {}'.format(protocol_name, proxy_server)
    log.info(msg)
    steps = {
        'step_name': '',
        'result': '',
        'expect': '',
        'actual': '',
        'note': ''}
    if proxy_test.set_proxy(proxy_server):
        step_rs = 'Pass'
        fun_rs = True
        msg2 = 'succeed to clear http proxy'
    else:
        step_rs = 'Fail'
        fun_rs = False
        msg2 = 'Failed to clear http proxy'
    msg3 = 'network panel can be edit'
    steps['step_name'] = msg
    steps['actual'] = msg2
    steps['expect'] = msg3
    steps['result'] = step_rs
    log.info('test {}'.format(step_rs))
    common_function.update_cases_result(report_file, case_name, steps)
    # if fun_rs:
    #     proxy_test.reboot()
    # else:
    #     proxy_test.reset_env_halfway()
    return fun_rs


def set_proxy1(proxy_test, case_name, report_file):
    proxy_server = proxy_test.get_proxy_server('proxy1')
    return set_proxy_common(proxy_test, proxy_server, case_name, report_file)


def set_proxy2(proxy_test, case_name, report_file):
    proxy_server = proxy_test.get_proxy_server_ftp('proxy2')
    return set_proxy_common(proxy_test, proxy_server, case_name, report_file)


def access_website_after(proxy_test, case_name, report_file):
    msg = 'step - - access website after setting proxy'
    log.info(msg)
    steps = {
        'step_name': '',
        'result': '',
        'expect': '',
        'actual': '',
        'note': ''}
    url = proxy_test.host_name
    if proxy_test.access_website():
        step_rs = 'Pass'
        fun_rs = True
        msg2 = 'succeed to access {}'.format(url)
    else:
        step_rs = 'Fail'
        fun_rs = False
        msg2 = 'failed to access {}'.format(url)
    msg3 = '{} can be accessed'.format(url)
    steps['step_name'] = msg
    steps['actual'] = msg2
    steps['expect'] = msg3
    steps['result'] = step_rs
    log.info('test {}'.format(step_rs))
    common_function.update_cases_result(report_file, case_name, steps)
    return fun_rs
    # if fun_rs:
    #     proxy_test.reboot()
    # else:
    #     proxy_test.reset_env_halfway()
    # return fun_rs


def access_ftp(proxy_test, case_name, report_file):
    msg = 'step - - access ftp'
    log.info(msg)
    steps = {
        'step_name': '',
        'result': '',
        'expect': '',
        'actual': '',
        'note': ''}
    url = proxy_test.host_name
    if proxy_test.access_ftp():
        step_rs = 'Pass'
        fun_rs = True
        msg2 = 'succeed to access {}'.format(url)
    else:
        step_rs = 'Fail'
        fun_rs = False
        msg2 = 'failed to access {}'.format(url)
    msg3 = '{} can be accessed'.format(url)
    steps['step_name'] = msg
    steps['actual'] = msg2
    steps['expect'] = msg3
    steps['result'] = step_rs
    log.info('test {}'.format(step_rs))
    common_function.update_cases_result(report_file, case_name, steps)
    # if fun_rs:
    #     proxy_test.reboot()
    # else:
    #     proxy_test.reset_env_halfway()
    return fun_rs


def finish(proxy_test):
    proxy_test.finish()
