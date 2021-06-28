# import os, re
# import subprocess


# def get_info(eth="eth0"):
#     """
#     :return: [eth, mac, ip, gateway]
#     """
#     result = subprocess.getoutput(r"ifconfig | grep {} -A 2 -B 1|grep -i 'inet' -A 2 -B 1".format(eth))
#     print(result)
#     g_ip = re.search(r"(?i)(?:inet|inet addr)[: ]([\\.\d]+)", result)
#     g_mac = re.search(r"(?i)(?:HWaddr|ether)[: ](..:..:..:..:..)", result)
#     assert g_ip, "Get IP Fail"
#     assert g_mac, "Get Mac Fail"
#     gate_way = subprocess.getoutput(r"route -n|grep {} -m 1".format(eth))
#     g_way = re.search(r"[.\d]+ +([.\d]+)", gate_way)
#     assert g_way, "Get Gate Way Fail"
#     return eth, g_mac.group(1), g_ip.group(1), g_way.group(1)
from Test_Script.ts_power_manager.common_function import PrepareWakeUp
import time
with PrepareWakeUp(time=0):
    time.sleep(20)

print("ok")