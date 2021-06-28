import pyautogui
import subprocess
import os
import re
from time import sleep
from Test_Script.ts_precheck import precheck_function as cfn
from Common import common_function
from Common.picture_operator import wait_element

log = common_function.log


# now connected wireless SSID
def now_connected_wireless():
    count = 0
    for i in range(60):
        sleep(1)
        count += 1
        s = subprocess.getoutput("iwconfig wlan0 | grep SSID")
        pattern = re.compile('"(.*)"')
        ssid_list = pattern.findall(s)
        if len(ssid_list) == 1:
            ssid = ssid_list[0]
            return ssid
        else:
            continue
    if count == 60:
        log.info('Fail to connect to wireless after {} seconds.'.format(count))
        return 'timeout'


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
    except Exception as e:
        log.error(e)
        # pass


def enable_eth0():
    try:
        os.popen("/usr/lib/hptc-network-mgr/common/netmgr_wired --up eth0")
        log.info("enable eth0")
    except Exception as e:
        log.error(e)


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
    # cfn.open_window("network")
    # log.info("open network window")
    # sleep(2)
    # net_win = cfn.check_window("cp_network_window.png")
    # if not net_win:
    #     log.error("open network window fail")
    #     return False
    pyautogui.hotkey('ctrl', 'alt', 's')
    sleep(1)
    pyautogui.typewrite('network', interval=0.25)
    sleep(1)
    pyautogui.hotkey('enter')
    sleep(1)
    if not __click_picture('_wireless_tab'):
        return False
    sleep(1)
    if not __click_picture('_add'):
        return False
    sleep(1)
    if not __click_picture('ssid', offset=True):
        return False
    sleep(1)
    pyautogui.typewrite(ssid, interval=0.25)
    sleep(1)
    if not __click_picture('security'):
        return False
    sleep(1)
    if not __click_picture('security_authentication'):
        return False
    sleep(1)
    if password != '':
        pyautogui.press('down', presses=2, interval=0.5)
    pyautogui.press('enter')
    sleep(1)
    if ssid != 'R1-TC_5G_n':
        if not __click_picture('preshared_key', offset=True):
            return False
        sleep(1)
        pyautogui.typewrite(password, interval=0.25)
        sleep(1)
    if not __click_picture('_ok'):
        return False
    sleep(1)
    if not __click_picture('apply'):
        return False
    sleep(1)
    subprocess.getoutput("wmctrl -c 'Control Panel'")
    log.info("configure wireless {}".format(ssid))
    return True


def connect_wireless_R1_TC_5G_n():
    # cfn.open_window("network")
    # log.info("open network window")
    # sleep(1)
    # net_win = cfn.check_window("cp_network_window.png")
    pyautogui.hotkey('ctrl', 'alt', 's')
    sleep(1)
    pyautogui.typewrite('network', interval=0.25)
    sleep(1)
    pyautogui.hotkey('enter')
    sleep(1)
    net_win = wait_pictures('_wireless_tab')
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
        # cp_quit = cfn.check_window("cp_quit.png")
        # if cp_quit:
        #     pyautogui.click(cp_quit)
        #     log.info("connect wireless R1_TC_5G_n")
        #     return True
        # else:
        #     os.system("pkill hptc-control-pa")
        #     log.info("connect wireless R1_TC_5G_n")
        #     return True
        subprocess.getoutput("wmctrl -c 'Control Panel'")
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
    scan_times = 5
    for i in range(scan_times):
        sleep(1)
        all_ssid = subprocess.getoutput("iwlist wlan0 scan | grep ESSID")
        if SSID in all_ssid:
            c += 1
    if c == scan_times:
        log.info("Found {} in environment and signal stable. Scan {} times found {} times.".format(SSID, scan_times, c))
        return True
    elif c == 0:
        log.info("Can't find {} in environment, scan {} times found {} times.".format(SSID, scan_times, c))
        return False
    else:
        log.info("Found {} in environment but signal not stable. Scan {} times found {} times.".format(SSID, scan_times, c))
        return True


def wired_wireless_switch(enable):
    if enable.upper() == 'ON':
        subprocess.getoutput("mclient set root/Network/WiredWirelessSwitch 1 && mclient commit")
    elif enable.upper() == 'OFF':
        subprocess.getoutput("mclient set root/Network/WiredWirelessSwitch 0 && mclient commit")
    else:
        log.info('Invalid parameter: {}'.format(enable))
    curr_value = subprocess.getoutput('mclient --quiet get root/Network/WiredWirelessSwitch')
    if all([enable.upper() == 'ON', curr_value == '1']) or all([enable.upper() == 'OFF', curr_value == '0']):
        log.info('WiredWirelessSwitch set successfully. Value is {}.'.format(curr_value))
    else:
        log.info('Fail to set WiredWirelessSwitch.')


def wait_pictures(pic_folder_name):
    '''
    Wait a desired picture. If exists, return its coordinate.
    :param pic_folder_name: folder name of pictures. e.g. 'right_down_corner'
    :return: tuple of coordinate. e.g. ()
    '''
    path = common_function.get_current_dir()
    pic_folder = path + '/Test_Data/td_precheck/wireless/{}'.format(pic_folder_name)
    result = wait_element(pic_folder, rate=0.97)
    if result:
        return result[0], result[1]
    else:
        log.info('Not found {} picture.'.format(pic_folder_name))
        return False


def __click_picture(pic_folder_name, offset=False):
    pic_pos = wait_pictures(pic_folder_name)
    if not pic_pos:
        return False
    if offset is True:
        click_pos = pic_pos[0][0] + pic_pos[1][1], pic_pos[0][1]
    else:
        click_pos = pic_pos[0]
    pyautogui.click(click_pos)
    sleep(1)
    return True


def __wireless_channel_list_query(start, end, exp_status='active'):
    flag = False
    output_list = os.popen("iw list | grep \'MHz\' | sed -n '{}, {}p'".format(start, end)).readlines()
    if not output_list:
        log.info('No result for querying specific wireless channel.')
        return flag
    if exp_status.upper() == 'ACTIVE':
        func = lambda x: '.0 dBm)' in x
    elif exp_status.upper() == 'DISABLED':
        func = lambda x: '(disabled)' in x
    else:
        log.info('Invalid expected status.')
        return flag
    for item in output_list:
        if not func(item):
            return flag
    flag = True
    return flag


def indo_wireless_channels_5g_check():
    start_5g = subprocess.getoutput("iw list | grep \'MHz\' | grep -n '\[36\]' | awk -F: '{print $1}'")
    end_5g = subprocess.getoutput("iw list | grep \'MHz\' | grep -n '\[165\]' | awk -F: '{print $1}'")
    start_indo = subprocess.getoutput("iw list | grep \'MHz\' | grep -n '\[149\]' | awk -F: '{print $1}'")
    end_indo = subprocess.getoutput("iw list | grep \'MHz\' | grep -n '\[161\]' | awk -F: '{print $1}'")
    check_indo = __wireless_channel_list_query(start_indo, end_indo)
    check_prior = __wireless_channel_list_query(start_5g, str(int(start_indo) - 1), exp_status='disabled')
    check_post = __wireless_channel_list_query(str(int(end_indo) + 1), end_5g, exp_status='disabled')
    if all([check_indo, check_prior, check_post]):
        log.info('Check wireless channel 5g for indo is successful.')
        return True
    else:
        log.info('Check wireless channel 5g for indo is failed.')
        return False








