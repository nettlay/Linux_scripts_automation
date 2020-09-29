# case name: verify can connect wireless use hexdecimal psk
# Author: nick.lu

from Test_Suite import check_connect_ssid_r1_tc_5g_ac_wpa2p as tc_5g_ac


def start(case_name, **kwargs):
    if tc_5g_ac.start(case_name, ssid="R1-TC-5G_ax_WPA2P", **kwargs):
        return True
    else:
        return False
