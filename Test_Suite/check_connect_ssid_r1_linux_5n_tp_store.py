# case name: check connectivity with the SSID R1-Linux-5N use ThinPro Store tab certificate
# Author: nick.lu

from Test_Suite import check_connect_ssid_r1_tc_5g_ac_wpa2p as tc_5g_ac


def start(case_name, **kwargs):
    if tc_5g_ac.start(case_name, ssid="R1-Linux-5N_thinpro_store", **kwargs):
        return True
    else:
        return False
