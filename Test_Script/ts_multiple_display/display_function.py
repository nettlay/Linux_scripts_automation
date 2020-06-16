import os
import re
import subprocess
import sys
import platform
import time
import traceback
import yaml
import shutil
from Test_Script.ts_multiple_display import generate_xml_file
from Common.exception import AnalyzeNameError
from Common.log import Logger

__os = platform.system()
if __os.upper() == 'WINDOWS':
    import winreg
    import win32gui
    import win32con


logger = Logger()                        # Below logger need rewrite
if os.path.dirname(sys.argv[0]) == "":
    cwd = os.getcwd()
else:
    cwd = os.path.dirname(sys.argv[0])


def analyze_name(case_name):
    """
    if case name can't be matched, it will throw a AssertionError or AnalyzeNameError to info you
     that you write a wrong rule or display_port has not enough ports
    :param case_name: Like one of them:
          't730_4 monitors_DP 1920x1200 60_Landscape 4x1_ViEw_blast win10_p1',
          'T628_2 monitors_VGA 1920x1200 60+DVI 3840x2140 60_L left 2x2_rdp_Win10_p1',
          'Mt31_3 monitors_LCD 1600x900 60+HDMI 1920x1200 30+Type-c 1920x1200 60_L left 3x1_view_Rdp win10_p1'
    :return: {'platform': 't730',
            'monitors': {'DisplayPort-0': ['3840x2160', 60],
                         'DisplayPort-1': ['3840x2160', 60],
                         'DisplayPort-2': ['3840x2160', 60],
                         'DisplayPort-3': ['3840x2160', 60]},
            'layout': 'Landscape 4x1',
            'vdi': 'view',
            'session': 'blast win10',
            'priority': 'P1'}
    """

    map_dic = {"platform": "",
               "monitors": {},
               "layout": "",
               "vdi": "",
               "session": "",
               "priority": ""}
    assert_error_string = "\033[1;35;1m{}:\"{}\"\033[0m".format("\r\nCaseName exits error! check case name", case_name)
    res = re.findall(r"((?i)[\dmt]{4})_([12346] monitors)_(.*)_(.*?)_(view|RDP|Citrix)_(.*?)_((?i)p\d)$", case_name,
                     re.S)
    assert res != [], assert_error_string
    platform, monitor, ports, layout, vdi, session, priority = res[0]
    port_num = int(monitor[0])
    ports_list = ports.split("+")
    port_num_spl = len(ports_list)
    assert port_num == port_num_spl or port_num_spl == 1, assert_error_string
    with open("./Test_Data/td_multiple_display/display_port.yml", "r") as f:
        dic_res = yaml.safe_load(f)
    grep = r"(.*?) (\d+x\d+) ([0-9]{2})$"
    p_it_dic = {}
    zip_list = []
    map_f = {}
    num_dic = {}
    if port_num_spl == 1:
        port_list = re.findall(grep, ports_list[0])
        assert port_list != [], assert_error_string
        p, *res_ref = port_list[0]
        map_f = dic_res.get(platform.upper(), {})
        map_p = map_f.get(p.upper(), "")
        assert map_p != "", assert_error_string
        if isinstance(map_p, list) and not p_it_dic.get(p.upper()):
            p_it_dic[p.upper()] = iter(map_p)
        for i in range(port_num):
            zip_list.append((p.upper(), res_ref))
    else:
        for port in ports_list:
            port_list = re.findall(grep, port)
            assert port_list != [], assert_error_string
            p, *res_ref = port_list[0]
            map_f = dic_res.get(platform.upper(), {})
            map_p = map_f.get(p.upper(), "")
            assert map_p != "", assert_error_string
            zip_list.append((p.upper(), res_ref))
            num_dic[p.upper()] = num_dic.get(p.upper(), 0) + 1
            if isinstance(map_p, list) and not p_it_dic.get(p.upper()):
                p_it_dic[p.upper()] = iter(map_p)

    map_dic["platform"] = platform.upper().strip()
    map_dic["layout"] = layout.upper().strip()
    map_dic["vdi"] = vdi.upper().strip()
    map_dic["session"] = session.upper().strip()
    map_dic["priority"] = priority.upper().strip()
    monitors = map_dic["monitors"]
    for element in zip_list:
        p_it = p_it_dic.get(element[0], "")
        if p_it:
            stop_it_error = False
            try:
                monitors[next(p_it)] = element[1]
            except StopIteration:
                stop_it_error = True
            except Exception:
                traceback.print_exc()
            if stop_it_error:
                raise AnalyzeNameError("\033[1;35;1m{}:\"{}\"\033[0m".format(
                    "\r\nStopIteration!!CaseName error, check port exit,or check display_port.xml", case_name))
        else:
            assert not p_it and num_dic.get(element[0]) == 1, "\033[1;35;1m{}:\"{}\"\033[0m".format(
                "\r\nCaseName error, check port exit,or check display_port.xml", case_name)
            monitors[map_f[element[0]]] = element[1]
    return map_dic


class LinuxTools:
    """
    get_resolution()
    generate_profile(os_version, layout, resolution, save_file='displays.xml')
    check_resolution(data)
    check_resolution_xrandr(data)
    set_local_resolution()
    snapshot(filename)
    """

    @staticmethod
    def get_resolution():
        monitors_info = os.popen('xrandr --listactivemonitors').readlines()
        print(monitors_info)
        dic = {}
        for i in range(1, len(monitors_info)):
            port_name = monitors_info[i].split()[-1]
            port_resolution = str(monitors_info[i].split()[-2].split('/')[0]) + 'x' + str(
                monitors_info[i].split()[-2].split('/')[1].split('x')[1])
            dic[port_name] = port_resolution
        print(dic)
        return dic

    def generate_profile(self, layout, resolution, save_file='displays.xml'):
        return generate_xml_file.DisplaySetting(layout=layout, resolution=resolution,
                                                save_file=save_file).generate()

    def check_resolution_xrandr(self, data):
        dic = {}
        for i in data.keys():
            dic[i] = data[i][0]
        original = self.get_resolution()
        print(original)
        if original == dic:
            return True
        else:
            return False

    @staticmethod
    def set_local_resolution():
        os.popen('cp ./Test_Data/displays.xml /home/user/.config/xfce4/xfconf/xfce-perchannel-xml/')
        os.popen('chmod 777 ./Test_Data/td_multiple_display/refresh_display.sh ')
        time.sleep(1)
        os.popen('./Test_Data/td_multiple_display/refresh_display.sh')


class WESTools:
    def __init__(self):
        self.tool = os.path.join(cwd, r'Test_Utility\MultiMonitorTool.exe')

    def get_local_setting(self, file_name):
        if not os.path.exists(self.tool):
            return
        cmd = r"%s /SaveConfig \test_data\temp_%s" % (self.tool, file_name)
        subprocess.run(cmd)

    def set_local_resolution(self, file_name):
        if not os.path.exists(self.tool):
            return
        cmd = r"%s /LoadConfig \test_data\temp_%s" % (self.tool, file_name)
        subprocess.run(cmd)


def set_background(pic='background.jpg'):
    logger.info("set automation background")
    if __os.upper() == 'LINUX':
        shutil.copy(os.path.join(os.getcwd(), 'Test_Utility', pic),
                    '/writable/home/user/background.jpg')
        os.system("mclient --quiet set root/background/desktop/theme 'image'")
        os.system("mclient --quiet set root/background/desktop/imagePath '/writable/home/user/background.jpg'")
        os.system("mclient --quiet set root/background/desktop/style 'fill'")
        os.system("mclient commit")
        os.system("hptc-file-mgr -b /writable/home/user/background.jpg -d")
    else:
        cwd = os.getcwd()
        file_path = r'%s\Test_Utility\%s' % (cwd, pic)

        def get_reg_key_handle(reg_root, reg_path, reg_flag):
            try:
                key = winreg.OpenKeyEx(reg_root, reg_path, 0, reg_flag)
            except OSError:
                key = None
            return key

        def add_reg_value(reg_root, key_path, value_name, value_type, value_data):
            key_obj = get_reg_key_handle(reg_root, key_path, winreg.KEY_WOW64_64KEY | winreg.KEY_ALL_ACCESS)
            if key_obj:
                winreg.SetValueEx(key_obj, value_name, 0, value_type, value_data)
                winreg.CloseKey(key_obj)
            else:
                logger.error('not find %s' % key_path)

        add_reg_value(winreg.HKEY_CURRENT_USER, r'Control Panel\Desktop', 'WallPaper', winreg.REG_SZ, file_path)
        add_reg_value(winreg.HKEY_CURRENT_USER, r'Control Panel\Desktop', 'TileWallpaper', winreg.REG_SZ, '0')
        add_reg_value(winreg.HKEY_CURRENT_USER, r'Control Panel\Desktop', "WallpaperStyle", winreg.REG_SZ, '10')
        win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, file_path, win32con.SPIF_SENDWININICHANGE)
