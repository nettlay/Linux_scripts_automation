import os
import subprocess
import time
import requests
from Common import common_function
from Common.log import log
from Test_Suite.verify_network_via_http_proxy import ProxyTest


class NoProxyTest(ProxyTest):
    def __init__(self, protocol_name='noproxy', bypass_setting=False):
        super().__init__(protocol_name, bypass_setting)

    def set_no_proxy(self, fill_all_protocol, bypass_text, case_name, report_file):
        log.info('set bypass: {}'.format(bypass_text))
        steps = {
            'step_name': 'set {} {}'.format(self.protocol, bypass_text),
            'result': 'Fail',
            'expect': 'icon can be recognised',
            'actual': '',
            'note': ''}
        proxy_list = ['http', 'ftp', 'https']
        t = self.dns.open_dns()
        if not t:
            log.info('Failed to recognise DNS icon')
            steps['actual'] = 'Failed to recognise DNS icon'
            common_function.update_cases_result(report_file, case_name, steps)
            self.dns.close_dns()
            return
        if fill_all_protocol:
            for i in proxy_list:
                proxy_text = self.get_proxy_server('proxy3').replace(self.protocol, 'http')
                t2 = self.dns.set_value(i, proxy_text)
                if not t2:
                    log.info('Failed to recognise {} icon'.format(i))
                    steps['actual'] = 'Failed to recognise {} icon'.format(i)
                    common_function.update_cases_result(report_file, case_name, steps)
                    self.dns.close_dns()
                    return
        t3 = self.dns.set_value(self.protocol, bypass_text)
        time.sleep(5)
        if not t3:
            log.info('Failed to recognise noproxy icon')
            steps['actual'] = 'Failed to recognise noproxy icon'
            common_function.update_cases_result(report_file, case_name, steps)
            self.dns.close_dns()
            return
        t4 = self.dns.close_dns()
        if not t4:
            log.info('Failed to recognise apply icon')
            steps['actual'] = 'Failed to recognise apply icon'
            common_function.update_cases_result(report_file, case_name, steps)
            return
        log.info('proxy set successfully')
        steps['actual'] = 'proxy set successfully'
        steps['result'] = 'Pass'
        common_function.update_cases_result(report_file, case_name, steps)
        return True

    def website_test(self, url, flag, case_name, report_file):
        if flag:
            expect = 200
            msg = "verify {} can be accessed".format(url)
        else:
            expect = 'Error'
            msg = "verify {} can not be accessed".format(url)
        steps = {
            'step_name': "test {}".format(url),
            'result': '',
            'expect': 'status code should be {}'.format(expect),
            'actual': '',
            'note': ''}
        log.info(msg)
        log.info('current ip: {}'.format(common_function.get_ip()))
        log.info('get status code from {}'.format(url))
        data = self.get_website_response()
        actual = 'status code is {}'.format(data)
        log.info(actual)
        if data == expect:
            s = 'Pass'
            rs = True
        else:
            s = 'Fail'
            rs = False
        log.info('test {}'.format(s))
        steps['result'] = s
        steps['actual'] = actual
        common_function.update_cases_result(report_file, case_name, steps)
        return rs

    @staticmethod
    def website_test222(bypass_text, accessed_list, not_accessed_list, case_name, report_file):
        log.info('wait 10s')
        time.sleep(10)
        rs = False
        steps = {
            'step_name': "test no proxy: ".format(bypass_text),
            'result': '',
            'expect': 'status code should be 200',
            'actual': '',
            'note': ''}
        for j in accessed_list:
            log.info("verify {} can be accessed".format(j))
            log.info('get data from {}'.format(j))
            try:
                data = requests.get(j, timeout=5).status_code
            except Exception:
                data = 'Error'
            log.info('status code is: {}'.format(data))

            if data == 200:
                s = 'Pass'
                rs = True
            else:
                s = 'Fail'
                rs = False
            log.info('test {}'.format(s))
            steps['result'] = s
            common_function.update_cases_result(report_file, case_name, steps)
        for i in not_accessed_list:
            log.info("verify {} can not be accessed".format(i))
            log.info('get data from {}'.format(i))
            try:
                data = requests.get(i, timeout=5).status_code
            except Exception:
                data = 'Error'
            log.info('status code is: {}'.format(data))
            steps = {
                'step_name': "verify {} can not be accessed".format(i),
                'result': '',
                'expect': 'status code should be Error',
                'actual': data,
                'note': ''}
            if data == 'Error':
                s = 'Pass'
                rs = True
            else:
                s = 'Fail'
                rs = False
            log.info('test {}'.format(s))
            steps['result'] = s
            common_function.update_cases_result(report_file, case_name, steps)
        return rs

    def set_proxy_bypass(self, proxy_text, case_name, report_file):
        steps = {
            'step_name': "set {}: {}".format(self.protocol, proxy_text),
            'result': 'Fail',
            'expect': 'icon can be recognised',
            'actual': '',
            'note': ''}
        t = self.dns.open_dns()
        if not t:
            steps['actual'] = 'Failed to recognise DNS icon'
            common_function.update_cases_result(report_file, case_name, steps)
            return
        t2 = self.dns.set_value(self.protocol, proxy_text)
        if not t2:
            steps['actual'] = 'Failed to recognise {} icon'.format(self.protocol)
            common_function.update_cases_result(report_file, case_name, steps)
            return
        t4 = self.dns.close_dns()
        if not t4:
            steps['actual'] = 'Failed to recognise apply icon'
            common_function.update_cases_result(report_file, case_name, steps)
            return
        self.reboot()

    def reset_env_last(self):
        log.info('restore env default after the last step')
        # common_function.import_profile()
        self.dns.open_dns()
        for i in ['http', 'ftp', 'https']:
            self.dns.clear_text(i)
        self.dns.clear_text(self.protocol)
        self.dns.close_dns()
        subprocess.run('reboot')
        time.sleep(10)


def set_bypass_baidu(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    no_proxy_test = kwargs.get('obj')
    bypass_text = 'http://www.baidu.com'
    if no_proxy_test.set_no_proxy(True, bypass_text, case_name, report_file):
        no_proxy_test.reboot()
    else:
        no_proxy_test.reset_env_halfway()
        return False


def test_bypass_baidu(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    no_proxy_test = kwargs.get('obj')
    a = ['http://www.google.com']
    n = ['http://www.baidu.com']
    for url in a:
        if not no_proxy_test.website_test(url, True, case_name, report_file):
            no_proxy_test.reset_env_halfway()
            return False
    for url in n:
        if not no_proxy_test.website_test(url, False, case_name, report_file):
            no_proxy_test.reset_env_halfway()
            return False
    return True


def set_bypass_baidu_google(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    no_proxy_test = kwargs.get('obj')
    bypass_text = 'http://www.baidu.com,http://www.google.com'
    if no_proxy_test.set_no_proxy(False, bypass_text, case_name, report_file):
        no_proxy_test.reboot()
    else:
        no_proxy_test.reset_env_halfway()
        return False


def test_bypass_baidu_google(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    no_proxy_test = kwargs.get('obj')
    a = ['http://www.youtube.com']
    n = ['http://www.baidu.com', 'http://www.google.com']
    for url in a:
        if not no_proxy_test.website_test(url, True, case_name, report_file):
            no_proxy_test.reset_env_halfway()
            return False
    for url in n:
        if not no_proxy_test.website_test(url, False, case_name, report_file):
            no_proxy_test.reset_env_halfway()
            return False
    return True


def set_bypass_contain_baidu(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    no_proxy_test = kwargs.get('obj')
    bypass_text = '.baidu.com'
    if no_proxy_test.set_no_proxy(False, bypass_text, case_name, report_file):
        no_proxy_test.reboot()
    else:
        no_proxy_test.reset_env_halfway()
        return False


def test_bypass_contain_baidu(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    no_proxy_test = kwargs.get('obj')
    a = ['http://www.youtube.com']
    n = ['http://www.baidu.com', 'http://map.baidu.com']
    for url in a:
        if not no_proxy_test.website_test(url, True, case_name, report_file):
            no_proxy_test.reset_env_halfway()
            return False
    for url in n:
        if not no_proxy_test.website_test(url, False, case_name, report_file):
            no_proxy_test.reset_env_halfway()
            return False
    no_proxy_test.reset_env_last()
    return True


def finish(**kwargs):
    log.info('pave the way for the finish')


def start(case_name, kwargs):
    steps_list = (
        "set_bypass_baidu",
        "test_bypass_baidu",
        "set_bypass_baidu_google",
        "test_bypass_baidu_google",
        "set_bypass_contain_baidu",
        "test_bypass_contain_baidu",
        "finish"
    )
    no_proxy_test = NoProxyTest()
    result_file = common_function.get_current_dir(r'Test_Report', '{}.yaml'.format(common_function.check_ip_yaml()))
    common_function.new_cases_result(result_file, case_name)
    # no_proxy_test.tp.switch_mode()
    common_function.case_steps_run_control(steps_list, __name__, case_name=case_name, log=log,
                                           report_file=result_file, obj=no_proxy_test)
