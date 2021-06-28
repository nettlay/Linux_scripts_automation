from Common.common_function import Run_App
from Common.log import log
import subprocess, time, re


def disable_lan_filber(device_name):
    try:
        subprocess.run("/usr/lib/hptc-network-mgr/common/netmgr_wired --down {}".format(device_name),shell=True)
        log.info("disable {}".format(device_name))
    except Exception as e:
        log.error(e)
        # pass


def enable_lan_filber(device_name):
    try:
        subprocess.Popen("/usr/lib/hptc-network-mgr/common/netmgr_wired --up {}".format(device_name),shell=True)
        log.info("enable {}".format(device_name))
    except Exception as e:
        log.error(e)


def disable_wlan(device_name):
    try:
        subprocess.run("/usr/lib/hptc-network-mgr/wireless/hptc-wireless-manager --down {}".format(device_name),shell=True)
        log.info("disable {}".format(device_name))
    except Exception as e:
        log.error(e)


def enable_wlan(device_name):
    try:
        subprocess.run("/usr/lib/hptc-network-mgr/wireless/hptc-wireless-manager --up {}".format(device_name),shell=True)
        log.info("enable {}".format(device_name))
    except Exception as e:
        log.error(e)


# ping server to verify the wireless
def ping_server(ip="15.83.240.98"):
    log.info("start ping " + ip)
    s = subprocess.Popen("ping {} -c 50 | grep -i received".format(ip), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = s.communicate(timeout=60)
    out = out.decode()
    out_list = out.split(',')
    try:
        s.kill()
        res = re.search(r"(\d+)", out_list[2])
        result = res.group(1)
        if int(result) <= 25:
            log.info("ping " + ip + " success")
            return True
        # if out_list[2] == ' 0% packet loss':
        #     log.info("ping " + ip + " success")
        #     return True
        else:
            log.error("ping " + ip + " fail")
            log.error(f'ping {ip} result: {out}')
            return False
    except Exception as e:
        log.error(e)
        log.error("ping " + ip + " fail")
        return False


class NetWorkDisableEnable():
    def __init__(self):
        self.fiber_lan = []
        self.wlan = []

    def linux_cmd_data_format(self,raw_data):
        data_list=[]
        for i in raw_data.split('\n'):
            temp=i.strip()
            if temp:
                data_list.append(temp)
        return data_list

    def get_nics(self):
        app=Run_App('ifconfig')
        app.start()
        r=app.get_stdout().decode()
        r_list=self.linux_cmd_data_format(r)
        nics=[]
        for i in r_list:
            if 'hwaddr' in i.lower():
                single_nic=[]
                single_nic_pure=[]
                single_nic.extend(i.split('  '))
                single_nic.extend(r_list[r_list.index(i)+1].split('  '))
                for j in single_nic:
                    if j:
                        single_nic_pure.append(j)
                nics.append(single_nic_pure)
        return nics

    def update_nic_status(self):
        nics = self.get_nics()
        for nic in nics:
            if nic[0].startswith('eth'):
                self.fiber_lan.append(nic)
            elif nic[0].startswith('wlan'):
                self.wlan.append(nic)

    def get_lan(self):
        if len(self.fiber_lan):
            return self.fiber_lan[0]

    def disable_lan(self):
        lan=self.get_lan()
        if lan:
            disable_lan_filber(lan[0])
        else:
            log.info("Not found lan")

    def enable_lan(self):
        lan = self.get_lan()
        if lan:
            enable_lan_filber(lan[0])
        else:
            log.info("Not found lan")

    def get_wlan(self):
        if self.wlan:
            return self.wlan[0]

    def disable_wlan(self):
        wlan=self.get_wlan()
        if wlan:
            disable_wlan(wlan[0])
        log.info("Not found wlan")

    def enable_wlan(self):
        wlan = self.get_wlan()
        if wlan:
            enable_wlan(wlan[0])
        else:
            log.info("Not found wlan")

    def get_fiber(self):
        if len(self.fiber_lan)>1:
            return self.fiber_lan[1]

    def disable_fiber(self):
        fiber=self.get_fiber()
        if fiber:
            disable_lan_filber(fiber[0])
        else:
            log.info("Not found fiber")

    def enable_fiber(self):
        fiber = self.get_fiber()
        if fiber:
            enable_lan_filber(fiber[0])
        else:
            log.info("Not found fiber")


def test():
    net=NetWorkDisableEnable()
    net.update_nic_status()
    net.enable_lan()
    time.sleep(10)
    ping_server()
    # net.enable_fiber()
    # ping_server()
    # net.enable_wlan()
    # ping_server()
    net.disable_lan()
    time.sleep(10)
    ping_server()
    # net.disable_fiber()
    # ping_server()
    # net.disable_wlan()
    # ping_server()

