# case name: check connectivity with the SSID R1-TC_5G_n
# Author: nick.lu

from Test_Suite import check_connect_ssid_r1_tc_5g_ac_wpa2p as tc_5g_ac


def start(case_name, **kwargs):
    if tc_5g_ac.start(case_name, ssid="R1-TC_5G_n", **kwargs):
        return True
    else:
        return False
