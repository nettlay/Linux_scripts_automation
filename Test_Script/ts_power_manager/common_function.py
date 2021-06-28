import os
import time
import re
import threading
import subprocess
import pyautogui
from Common import common_function, picture_operator, tool
from Common.socket_client import SocketClient
from Common.exception import ConnectionRefused
from Common.file_operator import YamlOperator
from Common.common_function import kb
import traceback
import socket
from Common.vdi_connection import VDIConnection
from Common.log import log
import time


def linux_check_locked(**kwargs):
    path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager', 'locked_pic')
    path1 = kwargs.get('path', path)
    if picture_operator.wait_element(os.path.join(path1), cycle=1):
        return True
    else:
        return False


def write_file(file_path):
    count = 0
    while True:
        cur_time = time.time()
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(str(int(cur_time)))
            f.write('\n')
        time.sleep(2)
        count += 2
        if count > 20:
            return


def counting(lis):
    for i in range(len(lis) - 1):
        if int(lis[i + 1].strip('\n')) - int(lis[i].strip('\n')) > 3:
            return int(lis[i + 1].strip('\n')) - int(lis[i].strip('\n'))


def linux_check_sleep(self, file_name, file_path=''):
    if file_path:
        path = file_path
    else:
        path = common_function.get_current_dir()
    end_path = os.path.join(path, '{}.txt'.format(file_name))
    print(end_path)
    self.write_file(end_path)
    with open(end_path, 'r', encoding='utf-8') as f:
        file_info = f.readlines()
        sleep_time = self.counting(file_info)
    os.remove(end_path)
    if sleep_time:
        print('have sleep movements, sleep time:{}'.format(sleep_time))
        return True
    else:
        print('no sleep movements')
        return False


class TimeCounter(threading.Thread):
    __last_time = 0
    __max_time_gap = 0
    __flag = True

    def __init__(self):
        threading.Thread.__init__(self)
        self.__last_time = time.time()
        print(self.__last_time, "init")

    def listen(self):
        print(threading.currentThread())
        while self.__flag:
            last_time = time.time()
            gap = last_time - self.__last_time
            self.__last_time, self.__max_time_gap = (last_time, gap) if gap > self.__max_time_gap else \
                (last_time, self.__max_time_gap)
            time.sleep(5)

    def get_current_time(self):
        return self.__last_time

    def get_max_time_gap(self):
        return self.__max_time_gap

    def set_max_time_gap(self, t):
        self.__max_time_gap = t

    def stop(self):
        self.__flag = False
        return

    def run(self) -> None:
        self.listen()


class PrepareWakeUp:
    _yaml_path = common_function.get_current_dir("Test_Data/td_power_manager/global_settings.yml")
    _sys_wait_time = 30

    def __init__(self, **kwargs):
        self.t = TimeCounter()
        self.ti = kwargs.get("time", self._sys_wait_time)
        self._sys_wait_time = kwargs.get("sys_time", self._sys_wait_time)
        self.domain_list = YamlOperator(self._yaml_path).read().get("Wol_server_list")
        self.ip_list = self.domains_to_ip_list(self.domain_list)
        assert self.ip_list, "ip list is None"
        print("init")

    def __enter__(self):
        self.t.setDaemon(True)
        self.t.start()
        self.send_sleep()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("wait before exit")
        self.wait(self._sys_wait_time)
        self.t.stop()
        print("exit")

    @staticmethod
    def wait(t):
        return time.sleep(t)

    @staticmethod
    def add_wake_on_auth(eth):
        os.popen("ethtool -s {} wol g".format(eth))
        return

    @staticmethod
    def get_info(eth="eth0"):
        """
        :return: [eth, mac, ip, gateway]
        """
        result = subprocess.getoutput(r"ifconfig | grep {} -A 2 -B 1|grep -i 'inet' -A 2 -B 1".format(eth))
        g_ip = re.search(r"(?i)(?:inet|inet addr)[: ]([\\.\d]+)", result)
        g_mac = re.search(r"(?i)(?:HWaddr|ether)[: ](..:..:..:..:..:..)", result)
        assert g_ip, "Get IP Fail"
        assert g_mac, "Get Mac Fail"
        gate_way = subprocess.getoutput(r"route -n|grep {} -m 1".format(eth))
        g_way = re.search(r"[.\d]+ +([.\d]+)", gate_way)
        assert g_way, "Get Gate Way Fail"
        return eth, g_mac.group(1), g_ip.group(1), g_way.group(1)

    @staticmethod
    def domains_to_ip_list(domains):
        ip_list = []
        log.info("domains: {}".format(domains))
        for domain in domains:
            try:
                ip_list.append(socket.getaddrinfo(domain, None)[0][4][0])
            except:
                log.info(" Can't connect {}".format(domain))
                traceback.print_exc()
        # return ip_list
        return ip_list

    @staticmethod
    def filter_socket_by_gateway(target_gw, ip_list):
        """
        Traverse the list to get the target ip by compare gateway
        :param target_gw: str
        :param ip_list: list
        :return: socket obj
        """
        log.info("server ip list: {}".format(ip_list))
        for ip in ip_list:
            log.info(f'current server ip is {ip}')
            soc = SocketClient(ip, 9011)
            time.sleep(1)
            res = soc.request("getinfo")
            log.info(f"'getinfo' server response: {res}")
            if not res or "fail" in res.lower():
                continue
            gateway = res.strip("'").strip("(").strip(")").replace("'", "").split(", ")
            if gateway[-1] == target_gw:
                log.info(f'target gateway is {target_gw}, target ip is {ip}')
                return soc
        else:
            raise ConnectionRefused

    @staticmethod
    def filter_ip_list(ip, ip_list):
        ip = ".".join(ip.split(".")[:-1])
        ip_list_new = list(filter(lambda x: ip in x, ip_list))
        assert ip_list_new, "No suitable Server in {}".format(ip_list)
        return ip_list_new

    def get_max_time_gap(self):
        return self.t.get_max_time_gap()

    def set_max_time_gap(self, t):
        return self.t.set_max_time_gap(t)

    def get_current_time(self):
        return self.t.get_current_time()

    def send_sleep(self):
        info = self.get_info()
        print(info, self.ip_list)
        eth, mac, ip, gateway = info
        mac = "".join(mac.split(":"))
        self.add_wake_on_auth(eth)
        filter_ip = ".".join(ip.split(".")[:-1])
        fil_ip_list = list(filter(lambda x: x if ".".join(x.split(".")[:-1]) == filter_ip else None, self.ip_list))
        soc = self.filter_socket_by_gateway(gateway, fil_ip_list)
        time.sleep(1)
        res = soc.request("wakeup {} {}".format(mac, self.ti + self._sys_wait_time))
        if "ACCEPT" in res.upper():
            soc.request("break")
            print("already to sleep!")
            return True
        else:
            soc.request("break")
            raise ConnectionRefused("Connect server but not get ACCEPT reponse")


class WebConn:
    web_id = VDIConnection.vdi_connection_id('firefox')[0]
    set_options = ['address', 'intendedUse', 'kioskMode', 'showBackForwardButton', 'showUrlBarRefreshButton',
                   'showSearchBar', 'showHomeButton', 'showTabsBar', 'showTaskBar', 'showWindowBorder', 'fullscreen',
                   'enablePrintDialog', 'manageOwnPrefs', 'fallBackConnection', 'autostart', 'autoReconnect',
                   'waitForNetwork', 'hasDesktopIcon', 'authorizations/user/execution', 'authorizations/user/edit']
    defau_value = [['https://www.baidu.com'], ['Citrix', 'RDP', 'Internet'], ['0', '1'],
                   ['0', '1'], ['0', '1'], ['0', '1'], ['0', '1'], ['0', '1'],
                   ['0', '1'], ['0', '1'], ['0', '1'], ['0', '1'], ['0', '1'],
                   ['{da39aa56-6c50-4e50-8897-e6f1869e220e}', '{4b3214f8-bfb1-4dc0-b07f-8e1197bae24a}',
                    '{16ce7b68-a1a1-443d-9f0d-d6310abdcb64}'], ['0', '1', '2', '3', '4', '5'],
                   ['0', '1'], ['0', '1'], ['0', '1'], ['0', '1'], ['0', '1']]

    def __init__(self, lis):
        self.lis = lis

    def get_default_set(self):
        lis = []
        for i in self.set_options:
            lis.append(os.popen("mclient --quiet get root/ConnectionType/firefox/connections/"
                                "{}/{}".format(self.web_id, i)).read().strip('\n'))
        return lis

    def edit_def_value(self, default_lis, edit_lis):
        for i in range(len(edit_lis)):
            if edit_lis[i] not in self.defau_value[i] and i != 0:
                os.system("mclient --quiet set root/ConnectionType/firefox/connections/"
                          "{}/{} {}".format(self.web_id, self.set_options[i], default_lis[i]))
            else:
                os.system("mclient --quiet set root/ConnectionType/firefox/connections/"
                          "{}/{} {}".format(self.web_id, self.set_options[i], edit_lis[i]))
        os.system("mclient commit")
        time.sleep(10)

    def set_web_connection(self, default_lis, edit_lis):
        if edit_lis:
            self.edit_def_value(default_lis, edit_lis)
        else:
            print('no value need edit,use default setting')

    @staticmethod
    def open_firefox():
        # path = os.path.join(common_function.get_current_dir(), 'Test_Data', 'td_power_manager', 'web_conn')
        # pic_path = common_function.get_folder_items(path, file_only=True)
        # web_icon = picture_operator.wait_element(os.path.join(path, pic_path[0]), offset=(15, 15))
        # tool.click(web_icon[0][0], web_icon[0][1], 2)
        common_function.open_window('web browser')

    @staticmethod
    def check_web_conn():
        res = subprocess.getoutput("wmctrl -lx | grep -i firefox")
        if res:
            return True
        else:
            return False

    def close_web_connection(self):
        os.system("wmctrl -c 'firefox'")
        time.sleep(2)
        if not self.check_web_conn():
            print("close web connection success")
            return True
        else:
            print("close web connection fail")
            return False

    def start_web_conn(self):
        default = self.get_default_set()
        print(default)
        self.set_web_connection(default, self.lis)
        self.open_firefox()
        time.sleep(15)
        if self.check_web_conn():
            print('web connection success')
        else:
            print('web not connection')
        time.sleep(5)
        self.close_web_connection()
        self.edit_def_value(default, default)


def event(event_method, *args, **kwargs):
    event_method_name = event_method.__name__
    step = {'step_name': '',
            'result': 'PASS',
            'expect': '',
            'actual': '',
            'note': ''}
    case_name = kwargs.get("case_name")
    yml_path = kwargs.get("yml_path", "")
    assert yml_path != "", 'yml_path error'
    event_params, event_dic = kwargs.get("event_params", ((), {}))
    call_back = kwargs.get("call_back", None)
    callback_params, callback_dic = kwargs.get("callback_parmas", ((), {}))
    inherit = kwargs.get("inherit", False)
    do_callback = kwargs.get("do_call_back", True)
    do_callback_false = kwargs.get("do_call_back_while_fail", False)
    res = event_method(*event_params, **event_dic)
    flag = True if res else False
    step.update({'step_name': event_method_name})
    if not res:
        path = common_function.get_current_dir("Test_Report/img/{}__{}_exception.png".format(case_name.replace(' ', '_'), event_method_name))
        picture_operator.capture_screen(path)
        error_msg = kwargs.get("error_msg", {})
        step.update({'result': 'Fail',
                     'expect': error_msg.get("expect", ""),
                     'actual': error_msg.get("actual", ""),
                     'note': '{}_exception.png'.format(event_method_name)})
    common_function.update_cases_result(yml_path, case_name, step)
    if do_callback and flag:
        if inherit and res:
            call_back(res, **callback_dic)
        elif call_back:
            print(*callback_params)
            call_back(*callback_params, **callback_dic)
    elif do_callback_false and not res:
        call_back(*callback_params, **callback_dic)
    return flag


def set_user_password(**kwargs):
    current_path = common_function.get_current_dir("Test_Data")
    temp_path = current_path + "/temp.png"
    user = current_path + "/td_power_manager/user_icon"
    enabled = user + "/enabled"
    change_path = user + "/change"
    SwitchThinProMode("admin")
    time.sleep(1)
    log.info("Open security desktop")
    os.popen("hptc-control-panel --config-panel /etc/hptc-control-panel/applications/hptc-security.desktop")
    time.sleep(2)
    res = picture_operator.wait_element(user)
    if res:
        location, shape = res
        loc_x, loc_y = location
        offset_x, offset_y = 0, -20
        loc = {"left": loc_x + offset_x, "top": loc_y + offset_y, "width": 500, "height": 40}
        picture_operator.capture_screen_by_loc(temp_path, loc)
        enabled_list = common_function.get_folder_items(enabled, file_only=True)
        change_path_list = common_function.get_folder_items(change_path, file_only=True)
        flag = True
        for i in enabled_list:
            if picture_operator.compare_pic_similarity(enabled + "/{}".format(i), temp_path):
                break
        else:
            flag = False
        for i in change_path_list:
            change_res = picture_operator.compare_pic_similarity(change_path + "/{}".format(i), temp_path)
            if change_res:
                break
        else:
            change_res = False
        if flag and change_res:
            change_loc, change_shape = change_res
            offset = (change_loc[0] + int(change_shape[1] / 2), change_loc[1] + int(change_shape[0] / 2))
            res = (loc_x + offset_x, loc_y + offset_y), offset
            loc, offset = res
            loc_x, loc_y = loc[0] + offset[0], loc[1] + offset[1]
            tool.click(loc_x, loc_y)
            time.sleep(1)
            tool.tap_key("1", 1)
            tool.tap_key("Tab", 1)
            tool.tap_key("1", 1)
            tool.tap_key(tool.keyboard.enter_key, 2)
            os.popen("hptc-control-panel --term")


def preparewakeup(t=120):
    with PrepareWakeUp(time=t) as w:
        w.wait(t)
    t_gap = w.get_max_time_gap()
    print(t_gap)
    if t_gap > 11:
        return True
    return False


def check_password_frame_exist(flag=True):
    time.sleep(2)
    pic_path = common_function.get_current_dir("Test_Data/td_power_manager/loc_screen_pic")
    res = picture_operator.wait_element(pic_path)
    res_flag = True if res else False
    if res_flag == flag:
        return True
    return False


class SwitchThinProMode(common_function.SwitchThinProMode):

    def __init__(self, switch_to, **kwargs):
        super().__init__(switch_to, **kwargs)


if __name__ == '__main__':
    web_conn = WebConn(['www.taobao.com', 'Rdp', '', '', '', '', '', '', '', '', '1', '1'])
    web_conn.start_web_conn()
