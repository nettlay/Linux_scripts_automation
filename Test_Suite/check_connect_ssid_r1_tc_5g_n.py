# case name: check connectivity with the SSID R1-TC_5G_n
# Author: nick.lu
import subprocess
import traceback
from Common.log import *
from Common import common_function as cf
from Test_Script.ts_network import network_setting, network


def connect_wireless(wireless, ssid):
    try:
        log.info("start connect wireless {}".format(ssid))
        wireless.open_network()
        wireless.switch_to_wireless_tab()
        res = wireless.add(ssid=ssid, static_ip=True, click=True)
        wireless.apply_and_ok()
        wireless.apply()
        wireless.close_control_panel()
        return res
    except:
        log.error(traceback.format_exc())
        return False


def step_1_2(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    ssid = kwargs.get("ssid")
    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)

    cf.SwitchThinProMode("admin")
    wireless = network_setting.Wireless()
    wireless.close_control_panel()
    if not wireless.check_wireless_card():
        try:
            wireless.restore_wireless()
        except Exception as e:
            log.error(traceback.print_exc())
            traceback.print_exc()
            raise e
        finally:
            wireless.close_control_panel()
        time.sleep(3)
        if not wireless.check_wireless_card():
            log.error("not found the wireless card on thin client")
            report = {'step_name': 'check wireless card',
                      'result': 'fail',
                      'expect': "thin client has wireless card",
                      'actual': "not found wireless card on thin client",
                      'note': ''}
            cf.update_cases_result(report_file, case_name, report)
            log.error("{:+^80}".format("test case fail"))
            wireless.restore_wireless()
            return False
    ssid_list = ["R1-Linux-5N_thinpro_store", "R1-Linux-5N_ssl_store", "R1-Linux-AC"]
    if ssid in ssid_list:                                         # import ROOTCA.cer
        if not cf.import_cert():
            log.error("import cert fail")
            report = {'step_name': 'import cert',
                      'result': 'fail',
                      'expect': "import cert success",
                      'actual': "import cert fail",
                      'note': ''}
            cf.update_cases_result(report_file, case_name, report)
            log.error("{:+^80}".format("test case fail"))
            wireless.restore_wireless()
            return False
    if ssid == "R1-Linux-2.4N":
        folder = subprocess.getoutput("ls /media")
        rootca_path = os.path.join("/media", folder, "Certs", "ROOTCA.cer")
        cert_8021x = os.path.join("/media", folder, "Certs", "802.1X.pfx")
        if not os.path.exists(rootca_path) or not os.path.exists(cert_8021x):
            log.error("not found the cert 'ROOTCA.cer' or '802.1X.pfx' in /media/{}/Certs".format(format(folder)))
            report = {'step_name': "check cert 'ROOTCA.cer' and '802.1X.pfx'",
                      'result': 'fail',
                      'expect': "found 'ROOTCA.cer' and '802.1X.pfx' in USB store",
                      'actual': "not found the cert 'ROOTCA.cer' or '802.1X.pfx' in /media/.../Certs",
                      'note': ''}
            cf.update_cases_result(report_file, case_name, report)
            log.error("{:+^80}".format("test case fail"))
            wireless.restore_wireless()
            return False

    wired = network_setting.Wired()
    if wired.check_wired_is_connected():
        wired.set_wired_and_wireless_simultaneously()
        wired.disable_eth0()

    wireless.del_wireless_profile_from_reg()
    con_res = connect_wireless(wireless=wireless, ssid=ssid)
    if con_res is False or con_res:                            # connect wireless
        log.error("add wireless {} profile fail".format(ssid))
        wireless.close_control_panel()
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        if not wired.check_wired_is_connected():
            wired.enable_eth0()
            log.info("wait connect wired")
            time.sleep(10)
        report = {'step_name': 'add wireless ' + ssid + ' profile fail',
                  'result': 'fail',
                  'expect': "connect wireless success",
                  'actual': "connect wireless fail, time out",
                  'note': f'{con_res}'}
        cf.update_cases_result(report_file, case_name, report)
        wireless.restore_wireless()
        return False

    for i in range(24):
        log.info("wait connect wireless {}...".format(ssid))
        time.sleep(5)
        if wireless.check_wireless_connected():
            log.info("wireless connect success")
            break
    else:
        log.error("connect wireless time out")
        report = {'step_name': 'connect wireless',
                  'result': 'fail',
                  'expect': "connect wireless success",
                  'actual': "connect wireless fail, time out",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        wired.enable_eth0()
        log.error("{:+^80}".format("test case fail"))
        wireless.restore_wireless()
        return False
    report = {'step_name': 'connect wireless',
              'result': 'Pass',
              'expect': "connect wireless success",
              'actual': "connect wireless success",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)
    log.info('Wait 30 seconds to stabilize the network')
    time.sleep(30)
    if not network.ping_server(ip="15.83.240.98"):           # ping 15.83.240.98
        report = {'step_name': 'ping "15.83.240.98"',
                  'result': 'fail',
                  'expect': "ping server success",
                  'actual': "ping server fail",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        wired.enable_eth0()
        log.error("{:+^80}".format("test case fail"))
        wireless.restore_wireless()
        return False
    report = {'step_name': 'ping "15.83.240.98"',
              'result': 'pass',
              'expect': "ping server success",
              'actual': "ping server success",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)
    log.info("start reboot")
    os.system("reboot")
    time.sleep(60)


def step_3_4(**kwargs):
    case_name = kwargs.get("case_name")
    report_file = kwargs.get("report_file")
    ssid = kwargs.get("ssid")
    log.info("check wireless status after reboot")
    cf.SwitchThinProMode("admin")
    wireless = network_setting.Wireless()
    wired = network_setting.Wired()
    for i in range(24):
        if wireless.check_wireless_connected():
            log.info("wireless auto connect success after reboot")
            break
        log.info("wait connect wireless {}...".format(ssid))
        time.sleep(5)
    else:
        log.error("connect wireless time out")
        report = {'step_name': 'check wireless status',
                  'result': 'fail',
                  'expect': "wireless auto connect success after reboot",
                  'actual': "wireless auto connect fail after reboot",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wireless.del_wireless_profile_from_reg()
        wired.set_wired_connection_priority()
        wired.enable_eth0()
        log.error("{:+^80}".format("test case fail"))
        wireless.restore_wireless()
        return False
    report = {'step_name': 'check wireless status',
              'result': 'pass',
              'expect': "wireless auto connect success after reboot",
              'actual': "wireless auto connect success after reboot",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)

    log.info("start delete the wireless profile")
    wireless.del_wireless_profile_from_reg()
    log.info("wait wireless disconnect")
    time.sleep(10)
    if wireless.check_wireless_connected():
        log.error("wireless connected")
        report = {'step_name': 'check wireless status',
                  'result': 'fail',
                  'expect': "wireless is disconnect after delete wireless profile",
                  'actual': "wireless is connect after delete wireless profile",
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        wired.set_wired_connection_priority()
        wired.enable_eth0()
        log.error("{:+^80}".format("test case fail"))
        wireless.restore_wireless()
        return False
    report = {'step_name': 'check wireless status',
              'result': 'pass',
              'expect': "wireless is disconnect after delete wireless profile",
              'actual': "wireless is disconnect after delete wireless profile",
              'note': ''}
    cf.update_cases_result(report_file, case_name, report)
    wired.set_wired_connection_priority()
    if not wired.check_wired_is_connected():
        log.info("wired is not connected")
        wired.enable_eth0()
        time.sleep(20)
    log.info("{:+^80}".format("test case pass"))
    return True


def start(case_name, **kwargs):
    ssid = kwargs.get("ssid", "R1-TC_5G_n")
    report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    cf.new_cases_result(report_file, case_name)

    steps_list = ("step_1_2", "step_3_4")
    cf.case_steps_run_control(steps_list, __name__, case_name=case_name, report_file=report_file, ssid=ssid)

