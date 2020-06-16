import pyautogui
import subprocess
import os
import re
from time import sleep
from Test_Script.ts_precheck import precheck_function as cfn
from Common import common_function

log = common_function.log()


# now connected wireless SSID
def now_connected_wireless():
    s = subprocess.getoutput("iwconfig wlan0 | grep SSID")
    try:
        pattern = re.compile('"(.*)"')
        ssid = pattern.findall(s)[0]
        return ssid
    except:
        return False


# ping server to verify the wireless
def ping_server(ip="15.83.240.98"):
    log.info("start ping " + ip)
    s = subprocess.getoutput("ping " + ip + " -c 4 | grep received")
    sleep(5)
    t = s.split(' ')[0]
    r = s.split(' ')[3]
    if int(t) > 0 and int(r) > 0:
        log.info("ping " + ip + " success")
        return True
    else:
        log.error("ping " + ip + " fail")
        return False


# check if have wireless card on thinpro
def check_wireless_card():
    log.info("start check wireless card status")
    wc = subprocess.getoutput("ifconfig | grep -i wlan")
    if not wc:
        log.info("not found wireless card in thinpro")
        return False
    else:
        log.info("found wireless card in thinpro")
        return True


def disable_eth0():
    try:
        os.popen("/usr/lib/hptc-network-mgr/common/netmgr_wired --down eth0")
        log.info("disable eth0")
    except Exception:
        pass


def enable_eth0():
    try:
        os.popen("/usr/lib/hptc-network-mgr/common/netmgr_wired --up eth0")
        log.info("enable eth0")
    except Exception:
        pass


# check if wireless network wlan0 IPv4 is connected
def check_wireless_connect():
    wireless_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/wlan0/IPv4/status")
    if wireless_status == "1":
        log.info("wireless is connected")
        return True
    else:
        log.info("wireless is disconnect")
        return False


# check if wired network eth0 IPv4 is connected
def check_eth0_connect():
    wireless_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/eth0/IPv4/status")
    if wireless_status == "1":
        log.info("eth0 is connected")
        return True
    else:
        log.info("eth0 is disconnect")
        return False


def del_all_wireless_profile():
    log.info("delete all wireless profiles")
    mp = cfn.mouse_position()
    sleep(1)
    cfn.open_window("network")
    log.info("open network window")
    sleep(1)
    pyautogui.press("tab", presses=3, interval=0.1)
    sleep(0.1)
    pyautogui.press("right")  # change to wireless tab
    wls = cfn.check_window("cp_wireless_tab.png")
    w = subprocess.getoutput("mclient --quiet get root/Network/Wireless/Profiles").splitlines()
    d = len(w)
    if wls:
        while d:
            pyautogui.click(wls[0]+mp['cp_wireless_tab'][0], wls[1]+mp['cp_wireless_tab'][1])

            dl = cfn.check_window("cp_network_delete_button.png")
            if dl:
                pyautogui.click(dl[0]+mp['cp_network_delete_button'][0], dl[1]+mp['cp_network_delete_button'][1])  # delete
                sleep(1)
                pyautogui.press("space")

                apl = cfn.check_window("cp_apply.png")
                pyautogui.click(apl)  # click apply
                d -= 1
            else:
                log.error("not found delete button")
                os.system("pkill hptc-control-pa")
                d = 0
                return False

        os.system("pkill hptc-control-pa")
        sleep(1)
    else:
        log.error("not in the wireless tab")
        os.system("pkill hptc-control-pa")
        sleep(1)
        return False


def check_network_status():
    log.info("start check the network status")
    network_status = subprocess.getoutput("mclient --quiet get tmp/network/status")
    if int(network_status) == 1:
        log.info("network has connected")
        return True
    else:
        log.info("currently no network is connected")
        return False


def check_indo_wireless_channal_disable():
    p1 = re.compile(r'[(](.*?)[)]', re.S)

    c_144 = subprocess.getoutput("iw list | grep '5720 MHz'").strip()
    c_149 = subprocess.getoutput("iw list | grep '5745 MHz'").strip()
    c_153 = subprocess.getoutput("iw list | grep '5765 MHz'").strip()
    c_157 = subprocess.getoutput("iw list | grep '5785 MHz'").strip()
    c_161 = subprocess.getoutput("iw list | grep '5805 MHz'").strip()
    c_165 = subprocess.getoutput("iw list | grep '5825 MHz'").strip()
    c_169 = subprocess.getoutput("iw list | grep '5845 MHz'").strip()

    channel_144 = re.findall(p1, c_144)  # disabled
    channel_149 = re.findall(p1, c_149)  # 22.0 dBm
    channel_153 = re.findall(p1, c_153)  # 22.0 dBm
    channel_157 = re.findall(p1, c_157)  # 22.0 dBm
    channel_161 = re.findall(p1, c_161)  # 22.0 dBm
    channel_165 = re.findall(p1, c_165)  # disabled
    channel_169 = re.findall(p1, c_169)  # disabled

    if channel_144[0] != "disabled":
        log.error("channel 144 not is disabled")
        return False

    if channel_149[0] != "22.0 dBm":
        log.error("channel 149 not is 22.0 dBm")
        return False

    if channel_153[0] != "22.0 dBm":
        log.error("channel 153 not is 22.0 dBm")
        return False

    if channel_157[0] != "22.0 dBm":
        log.error("channel 157 not is 22.0 dBm")
        return False

    if channel_161[0] != "22.0 dBm":
        log.error("channel 161 not is 22.0 dBm")
        return False

    if channel_165[0] != "disabled":
        log.error("channel 165 not is disabled")
        return False

    if channel_169[0] != "disabled":
        log.error("channel 169 not is disabled")
        return False

    log.info("channel 149, 153, 157, 161 is enable, and channel 165 is disabled.")
    return True


def check_wireless_connect_status(ap_name):
    if now_connected_wireless() == ap_name:
        log.info("connect {} wireless success".format(ap_name))
    else:
        log.error("connect wireless not is {}".format(ap_name))
        return False


def system_ip():

    wired_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/eth0/IPv4/status")
    if wired_status == "1":
        sys_eth0_ip = subprocess.getoutput("ifconfig | grep eth0 -A 1 | grep -i 'inet addr'")
        eth0_ip = sys_eth0_ip.strip().split()[1].split(":")[1]
        return eth0_ip

    wireless_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/wlan0/IPv4/status")
    if wireless_status == "1":
        sys_wlan0_ip = subprocess.getoutput("ifconfig | grep wlan0 -A 1 | grep -i 'inet addr'")
        wlan0_ip = sys_wlan0_ip.strip().split()[1].split(":")[1]
        return wlan0_ip

    else:
        return "null"


def connect_wireless_wpa2_psk(ssid, password="neoware1234"):
    cfn.open_window("network")
    log.info("open network window")
    sleep(2)
    net_win = cfn.check_window("cp_network_window.png")
    if net_win:
        log.info("open control panel network window success")
        pyautogui.press("tab", presses=3, interval=0.2)
        sleep(0.5)
        pyautogui.press("right", presses=1, interval=0.2)  # open add wireless
        sleep(0.5)
        pyautogui.press("tab", presses=3, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", interval=0.2)  # open add wireless
        sleep(0.5)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.typewrite(ssid, interval=0.1)  # input ssid
        sleep(0.5)
        pyautogui.press("tab", presses=9, interval=0.2)
        sleep(0.5)
        pyautogui.press("right", presses=3, interval=0.2)  # security
        sleep(0.5)
        pyautogui.press("tab", interval=0.2)
        sleep(0.5)
        pyautogui.press("down", presses=2, interval=0.2)  # WPA2
        sleep(0.5)
        pyautogui.press("tab", interval=0.2)
        sleep(0.5)
        pyautogui.typewrite(password, interval=0.1)
        sleep(0.5)
        pyautogui.press("tab", presses=2, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", presses=1, interval=0.2)  # apply
        sleep(0.5)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", presses=1, interval=0.2)  # ok
        sleep(1)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", presses=1, interval=0.2)  # apply control panel

        cp_quit = cfn.check_window("cp_quit.png")
        if cp_quit:
            pyautogui.click(cp_quit)
            log.info("connect wireless {}".format(ssid))
            return True
        else:
            os.system("pkill hptc-control-pa")
            log.info("connect wireless {}".format(ssid))
            return True
    else:
        log.error("open network window fail")
        return False


def connect_wireless_R1_TC_5G_n():
    cfn.open_window("network")
    log.info("open network window")
    sleep(1)
    net_win = cfn.check_window("cp_network_window.png")
    if net_win:
        log.info("open control panel network window success")
        pyautogui.press("tab", presses=3, interval=0.2)
        sleep(0.5)
        pyautogui.press("right", presses=1, interval=0.2)  # open add wireless
        sleep(0.5)
        pyautogui.press("tab", presses=3, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", interval=0.2)  # open add wireless
        sleep(0.5)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.typewrite("R1-TC_5G_n", interval=0.1)  # input ssid
        sleep(0.5)
        pyautogui.press("tab", presses=6, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", presses=1, interval=0.2)  # apply
        sleep(0.5)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", presses=1, interval=0.2)  # ok
        sleep(1)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", presses=1, interval=0.2)  # apply control panel

        cp_quit = cfn.check_window("cp_quit.png")
        if cp_quit:
            pyautogui.click(cp_quit)
            log.info("connect wireless R1_TC_5G_n")
            return True
        else:
            os.system("pkill hptc-control-pa")
            log.info("connect wireless R1_TC_5G_n")
            return True
    else:
        log.error("open network window fail")
        return False


def connect_wireless_wpa2_psk_5g_band(ssid, password="neoware1234"):
    cfn.open_window("network")
    log.info("open network window")
    sleep(1)
    net_win = cfn.check_window("cp_network_window.png")
    if net_win:
        log.info("open control panel network window success")
        pyautogui.press("tab", presses=3, interval=0.2)
        sleep(0.5)
        pyautogui.press("right", presses=1, interval=0.2)  # open add wireless
        sleep(0.5)
        pyautogui.press("tab", presses=3, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", interval=0.2)  # open add wireless
        sleep(0.5)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.typewrite(ssid, interval=0.1)  # input ssid
        sleep(0.5)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.press("down", presses=2, interval=0.2)  # 5GHz band
        sleep(0.5)
        pyautogui.press("tab", presses=8, interval=0.2)
        sleep(0.5)
        pyautogui.press("right", presses=3, interval=0.2)  # security
        sleep(0.5)
        pyautogui.press("tab", interval=0.2)
        sleep(0.5)
        pyautogui.press("down", presses=2, interval=0.2)  # WPA2
        sleep(0.5)
        pyautogui.press("tab", interval=0.2)
        sleep(0.5)
        pyautogui.typewrite(password, interval=0.1)
        sleep(0.5)
        pyautogui.press("tab", presses=2, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", presses=1, interval=0.2)  # apply
        sleep(0.5)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", presses=1, interval=0.2)  # ok
        sleep(1)
        pyautogui.press("tab", presses=1, interval=0.2)
        sleep(0.5)
        pyautogui.press("space", presses=1, interval=0.2)  # apply control panel

        cp_quit = cfn.check_window("cp_quit.png")
        if cp_quit:
            pyautogui.click(cp_quit)
            log.info("connect wireless {}".format(ssid))
            return True
        else:
            os.system("pkill hptc-control-pa")
            log.info("connect wireless {}".format(ssid))
            return True
    else:
        log.error("open network window fail")
        return False


def del_wireless_profile_from_reg():

    profiles = subprocess.getoutput("mclient --quiet get root/Network/Wireless/Profiles").splitlines()
    if profiles:
        log.info('found wireless profiles')
        for profile in profiles:
            profile_name = profile.split('/')[-1].strip()
            os.system('mclient delete root/Network/Wireless/Profiles/{}'.format(profile_name))
            os.system('mclient commit root/Network/Wireless')

        if not subprocess.getoutput("mclient --quiet get root/Network/Wireless/Profiles").splitlines():
            log.info("delete all wireless profiles success")
            return True
        else:
            log.error("delete all wireless profiles success")
            return False
    else:
        log.info('not found wireless profiles')
        return True


def scan_wireless(SSID):
    c = 0
    for i in range(3):
        sleep(1)
        all_ssid = subprocess.getoutput("iwlist wlan0 scan | grep ESSID")
        if SSID in all_ssid:
            c += 1
    if c == 3:
        log.info("found the {} in environment".format(SSID))
        return True
    else:
        log.info("can't found the {} in environment, or the {} is weak signal".format(SSID, SSID))
        return False










