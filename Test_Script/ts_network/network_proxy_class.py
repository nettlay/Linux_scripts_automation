import os
import subprocess
import time
import traceback

import requests
import webbrowser
from Common import common_function
from Common.file_operator import YamlOperator
from Common.log import log
from Common.file_transfer import FTPUtils
from Test_Script.ts_network import network_setting


class ProxyTest:
    def __init__(self, protocol_name, bypass_setting=False):
        self.protocol = protocol_name
        self.bypass_setting = bypass_setting
        self.dns = network_setting.DNS()
        self.tp = common_function.SwitchThinProMode('admin')

    @property
    def parameters(self):
        f = YamlOperator(common_function.get_current_dir('Test_Data', 'td_network',  'network_profile_info.yml'))
        return f.read()

    @property
    def host_name(self):
        return '{}://{}'.format(self.protocol, self.parameters.get('proxy').get('host_name'))

    @staticmethod
    def reboot():
        log.info('reboot system')
        subprocess.run('reboot')
        time.sleep(10)

    @staticmethod
    def open_web(url):
        webbrowser.open(url)

    def get_proxy_server(self, proxy_name):
        return 'http://{}'.format(self.parameters.get('proxy').get(proxy_name))

    def get_proxy_server_ftp(self, proxy_name):
        return 'ftp://{}'.format(self.parameters.get('proxy').get(proxy_name))

    def set_proxy(self, proxy_server):
        log.info('set proxy')
        t = self.dns.open_dns()
        if not t:
            log.info('Failed to recognise DNS icon')
            self.dns.close_dns()
            return
        t2 = self.dns.set_value(self.protocol, proxy_server)
        if not t2:
            log.info('Failed to recognise {} icon'.format(self.protocol))
            self.dns.close_dns()
            return
        if self.bypass_setting:
            t3 = self.dns.set_value('noproxy', self.bypass_setting)
        else:
            t3 = self.dns.clear_text('noproxy')
        if not t3:
            log.info('Failed to recognise noproxy icon')
            self.dns.close_dns()
            return
        t4 = self.dns.close_dns()
        if not t4:
            log.info('Failed to recognise apply icon')
            return
        log.info('proxy set successfully')
        return True

    def get_website_response(self):
        log.info('get data from {}'.format(self.host_name))
        # try:
        #     data_temp = requests.get(self.host_name, timeout=5).status_code
        # except Exception:
        #     data_temp = 'Error'
        #     log.info(traceback.format_exc())
        # if data_temp == 200:
        #     data = data_temp
        # else:
        #     data = 'Error'
        # return data
        file = common_function.get_current_dir('index.html')
        if os.path.exists(file):
            os.remove(file)
        cmd = 'wget -T 5 -t 2 {}'.format(self.host_name)
        log.info(cmd)
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
        for i in range(5):
            if os.path.exists(file):
                status = 200
                time.sleep(5)
                log.info('remove {}'.format(file))
                os.remove(file)
                break
        else:
            status = 0
        return status

    def access_website(self):
        log.info('current ip: {}'.format(common_function.get_ip()))
        expect = 200
        data = self.get_website_response()
        log.info('status code is: {}'.format(data))
        if data == expect:
            rs = True
        else:
            rs = False
        return rs

    @staticmethod
    def access_ftp():
        log.info('download file from ftp')
        try:
            ftp = FTPUtils('15.83.240.53', 'autotest1', 'Shanghai2010')
        except:
            log.info('cannot logon ftp')
            return False
        pic_name = 'iisstart.png'
        pic_path = common_function.get_current_dir('Test_Report', pic_name)
        try:
            ftp.download_file('/{}'.format(pic_name), pic_path)
        except:
            log.info(traceback.format_exc())
        for i in range(10):
            if os.path.exists(pic_path):
                rs = True
                break
            else:
                time.sleep(1)
        else:
            rs = False
        return rs

    def clear_proxy(self):
        self.dns.open_dns()
        return self.dns.clear_text(self.protocol)

    def reset_env_halfway(self):
        log.info('restore env default in halfway')
        self.dns.open_dns()
        self.dns.clear_text(self.protocol)
        self.dns.close_dns()
        subprocess.run('reboot')

    def reset_env_last(self):
        log.info('restore env default after the last step')
        # common_function.import_profile()
        self.dns.open_dns()
        self.dns.clear_text(self.protocol)
        self.dns.close_dns()
        subprocess.run('reboot')
        time.sleep(10)

    @staticmethod
    def finish():
        log.info('pave the way for the finish')


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
