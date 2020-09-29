# case_name: verify copying files via FTP at ThinPro local with specified fiber
# nick.lu

import subprocess
import traceback
from Common.log import *
from Common import common_function as cf
from Common import file_transfer


def check_fiber_exist():
    fiber = subprocess.getoutput("ifconfig | grep -i eth1")
    if fiber:
        return True
    else:
        return False


def check_fiber_network_connected():
    fiber_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/eth1/IPv4/status")
    if fiber_status == "1":
        return True
    else:
        return False


def start(case_name, **kwargs):
    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)

    if not check_fiber_exist():
        log.error("not found fiber card on thin client")
        pre_check_report = {'step_name': 'check_fiber_exist',
                            'result': 'Fail',
                            'expect': 'has fiber card on thin client',
                            'actual': 'not found fiber card on thin client',
                            'note': ''}
        cf.update_cases_result(report_file, case_name, pre_check_report)
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("found fiber card on thin client")

    if not check_fiber_network_connected():
        log.error("fiber card not connect to network")
        pre_check_report = {'step_name': 'check_fiber_network_connected',
                            'result': 'Fail',
                            'expect': 'fiber card connect to network',
                            'actual': 'fiber card not connect to network',
                            'note': ''}
        cf.update_cases_result(report_file, case_name, pre_check_report)
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("fiber card connect to network")

    log.info("start download big file from ftp")
    save_file_name = cf.get_current_dir("Test_Report/300m")
    try:
        ftp = file_transfer.FTPUtils(server="ostestftp.sh.dto", username="anonymous", password="123")
        ftp.download_file(file_name="300m.dd.gz", save_as_name=save_file_name)
    except:
        log.error(traceback.format_exc())
        download_report = {'step_name': 'download file from ftp',
                            'result': 'Fail',
                            'expect': 'download file from ftp success',
                            'actual': 'fail',
                            'note': '{}'.format(traceback.format_exc())}
        cf.update_cases_result(report_file, case_name, download_report)
        if os.path.exists(save_file_name):
            os.remove(save_file_name)
        log.error("{:+^80}".format("test case fail"))
        return False

    log.info("check download file on thinpro")
    if not os.path.exists(save_file_name):
        log.error("download '300m.dd.gz' from ftp fail")
        download_report = {'step_name': 'download file from ftp',
                           'result': 'Fail',
                           'expect': 'download file from ftp success',
                           'actual': 'not found the saved download file',
                           'note': ''}
        cf.update_cases_result(report_file, case_name, download_report)
        log.error("{:+^80}".format("test case fail"))
        return False
    log.info("download '300m.dd.gz' from ftp success")
    download_report = {'step_name': 'download big file from ftp',
                       'result': 'Pass',
                       'expect': 'download big file from ftp success',
                       'actual': 'download big file from ftp success',
                       'note': ''}
    cf.update_cases_result(report_file, case_name, download_report)
    log.info("remove download file")
    os.remove(save_file_name)
    log.info("{:+^80}".format("test case success"))
    return True

