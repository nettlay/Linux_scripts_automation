import os
import re
import subprocess
import platform
import time
import yaml
import shutil
from Common import common_function
from Common.file_operator import XMLOperator
from Test_Script.ts_multiple_display import generate_xml_file
from Common.log import Logger
import copy
import random

__os = platform.system()
if __os.upper() == 'WINDOWS':
    import winreg
    import win32gui
    import win32con

logger = Logger()  # Below logger need rewrite
cwd = common_function.get_current_dir()


def analyze_name(case_name):
    """
    if case name can't be matched, it will throw a AssertionError to info you
     that you write a wrong rule or display_port has not enough ports
    :param case_name: Like one of them:
          't730_1 monitors_DP 1920x1200 60_no_ViEw_blast win10_p1",
          't730_1 monitors_eDP2 1920x1200 60_no_ViEw_blast win10_p1",
          't730_1 monitors_DP1 1024x768 60_Single_Local_Local Desktop_P1_display_matrix',
          'T628_2 monitors_VGA 1920x1200 60+DVI 3840x2140 60_L left 2x2_rdp_rdp Win10_p1',
          'Mt31_3 monitors_LCD 1600x900 60+HDMI 1920x1200 30+Monitor1 1920x1200 60_L left 3x1_view_Rdp win10_p1',
          't730_4 Monitors_DP1 3840x2160 30+DP2 3840x2160 30+DP3 3840x2160 30+DP4 3840x2160 30_Landscape 2X2_Citrix_Citrix Server2016_P1_display_matrix'
    :return: {'platform': 't730',
            'monitors': {'DisplayPort-0': ['3840x2160', 60],
                         'DisplayPort-1': ['3840x2160', 60],
                         'DisplayPort-2': ['3840x2160', 60],
                         'DisplayPort-3': ['3840x2160', 60]},
            'layout': 'LANDSCAPE 2X2',
            'vdi': 'CITRIX',
            'session': 'WIN10',
            'priority': 'P1'}
    """

    map_dic = {"platform": "",
               "monitors": {},
               "layout": "",
               "vdi": "",
               "session": "",
               "priority": ""}
    assert_error_string = "\033[1;35;1m{}:\"{}\"\033[0m".format("\r\nCaseName exits error! check case name", case_name)
    res = re.findall(r"(?i)([\dmt]{4})_([12346] monitors)_(.*)_(.*?)_(view|RDP|Citrix|Local)_(.*?)_(p\d)", case_name, re.S)
    assert res != [], assert_error_string
    plat, monitor, ports, layout, vdi, session, priority = res[0]
    session = session.split(" ")[-1] if "citrix" in session.lower() else session
    port_num = int(monitor[0])
    grep = r"(?i)\+?(.*?) (\d+x\d+) ([0-9]{2})"
    port_list = re.findall(grep, ports)
    port_num_re = len(port_list)
    assert port_num == port_num_re or port_num_re == 1, assert_error_string
    if port_num_re == 1:
        p = copy.deepcopy(port_list)
        for i in range(port_num-1):
            port_list.extend(p)
    with open(common_function.get_current_dir("Test_Data/td_multiple_display/display_port.yml"), "r") as f:
        dic_res = yaml.safe_load(f)
    config_port_dic = dic_res.get(plat.upper(), [])
    assert config_port_dic != [], assert_error_string
    config_port_dic_copy = copy.deepcopy(config_port_dic)
    config_ports = [n for a in config_port_dic.values() for n in a]
    port_result = {}

    def get_port(port_list):
        if port_list:
            port_item, *items = port_list
            name, *other_item = port_item
            name = name.upper()
            real_port_list = config_port_dic.get(name, [])
            if real_port_list:
                real_port = random.choices(real_port_list)
                real_port = real_port[0]
                if real_port in port_result:
                    return get_port(port_list)
            elif "MONITOR" in name:
                assert config_ports != [], assert_error_string
                real_port = random.choices(config_ports)
                real_port = real_port[0]
                if real_port in port_result:
                    return get_port(port_list)
                name = list(filter(lambda x: real_port in config_port_dic[x], config_port_dic))[0]
            else:
                assert str.isdigit(name[-1]), assert_error_string
                name, num = name[:-1].upper(), int(name[-1]) - 1
                real_port_list = config_port_dic_copy.get(name, [])
                assert len(real_port_list) > num, assert_error_string
                real_port = real_port_list[num]
            port_result.update({real_port: list(other_item)})
            assert real_port in config_ports, assert_error_string
            config_ports.remove(real_port)
            config_port_dic.get(name).remove(real_port)
            return get_port(items)
        else:
            return {}
    get_port(port_list)
    map_dic["platform"] = plat.upper().strip()
    map_dic["layout"] = layout.upper().strip()
    map_dic["vdi"] = vdi.upper().strip()
    map_dic["session"] = session.upper().strip()
    map_dic["priority"] = priority.upper().strip()
    map_dic["monitors"] = port_result
    return map_dic


class LinuxTools:
    """
    get_resolution()
    get_fresh_rate()
    check_fresh_rate(data)
    generate_profile(os_version, layout, resolution, save_file='displays.xml')
    set_local_resolution()
    snapshot(filename)
    """

    @staticmethod
    def get_resolution():
        monitors_info = os.popen('xrandr --listactivemonitors').readlines()
        dic = {}
        for i in range(1, len(monitors_info)):
            port_name = monitors_info[i].split()[-1]
            port_resolution = str(monitors_info[i].split()[-2].split('/')[0]) + 'x' + str(
                monitors_info[i].split()[-2].split('/')[1].split('x')[1])
            dic[port_name.lower()] = port_resolution.lower()
        return dic

    @staticmethod
    def get_fresh_rate():
        monitors_info = os.popen('xrandr').read()
        res = re.findall(r"\s?([\w-]*?) connected[\w()\sx+]{0,200}?[\dx+\s.i]*?(\d{2}\.\d{2})\*", monitors_info, re.S)
        fil_obj = map(lambda x: (x[0].lower(), x[1]), res)
        return dict(fil_obj)



    @classmethod
    def check_fresh_rate(cls, data):
        """
        :param data: {'DisplayPort-0': ['1920x1080', 60],
                        'DisplayPort-2': ['1440x900', 60]}
        :return: bool
        """
        original = cls.get_fresh_rate()
        for k, v in data.items():
            d_v = int(v[1])
            o_v = original.get(k.lower(), -1)
            o_v = int(round(float(o_v)))
            if abs(o_v - d_v) > 1:
                return False
        return original

    def generate_profile(self, layout, resolution, save_file='displays.xml'):
        return generate_xml_file.DisplaySetting(layout=layout, resolution=resolution,
                                                save_file=save_file).generate()

    @staticmethod
    def set_local_resolution():
        os.popen('cp {}/Test_Data/displays.xml /home/user/.config/xfce4/xfconf/xfce-perchannel-xml/'.format(cwd))
        os.popen('chmod 777 {}/Test_Data/td_multiple_display/refresh_display.sh '.format(cwd))
        time.sleep(1)
        os.popen('{}/Test_Data/td_multiple_display/refresh_display.sh'.format(cwd))
        time.sleep(20)


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
        cmd = r"{} /LoadConfig {}/test_data/displays.cfg".format(self.tool, file_name)
        subprocess.run(cmd)


def set_background(pic='background.jpg'):
    logger.info("set automation background")
    uid = os.popen("id -u $currentUser").readline().strip()
    temp_env = 'XDG_RUNTIME_DIR=/run/user/{}'.format(uid)
    if __os.upper() == 'LINUX':
        shutil.copy(os.path.join(common_function.get_current_dir(), 'Test_Utility', pic),
                    "/writable/home/user/{}".format(pic))
        os.system("mclient --quiet set root/background/desktop/theme 'image'")
        os.system("mclient --quiet set root/background/desktop/imagePath '/writable/home/user/{}'".format(pic))
        os.system("mclient --quiet set root/background/desktop/style 'fill'")
        os.system("mclient commit")
        os.system("{} hptc-zero-desktop --image=/writable/home/user/{} --image-style=fill --root".format(temp_env, pic))
        time.sleep(10)
    else:
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


def set_display_profile(data):
    """
    :param data: profile_data = [['DisplayPort-0', 1920, 1080, 60, 0, 0, 0], ['DisplayPort-1', 1920, 1080, 60, 1920, 0, 0]]
    :return: ./Test_Data/displays.xml
    """
    profile_data = calculate_monitors_layout(data)
    if __os.upper() == 'LINUX':
        xml_file = os.path.join(cwd, 'Test_Data', 'td_multiple_display', 'displays_template_temp.xml')
        shutil.copy("/home/user/.config/xfce4/xfconf/xfce-perchannel-xml/displays.xml", xml_file)
        tree = XMLOperator(xml_file)
        for i in tree.find_nodes('property/property'):
            for profile in profile_data:
                if profile[0] == tree.get_value(i, 'name'):
                    for d in tree.iter(i):
                        if tree.get_value(d, 'name') == 'Resolution':
                            tree.set_value(d, 'value', str(profile[1]) + 'x' + str(profile[2]))
                        if tree.get_value(d, 'name') == 'RefreshRate':
                            tree.set_value(d, 'value', str(profile[3]))
                        if tree.get_value(d, 'name') == 'Rotation':
                            tree.set_value(d, 'value', str(profile[6]))
                        if profile_data.index(profile) == 0 and tree.get_value(d, 'name') == 'Primary':
                            tree.set_value(d, 'value', 'true')
                        if profile_data.index(profile) != 0 and tree.get_value(d, 'name') == 'Primary':
                            tree.set_value(d, 'value', 'false')
                        if tree.get_value(d, 'name') == 'Active':
                            tree.set_value(d, 'value', 'true')
                        for coord in tree.iter(d):
                            if tree.get_value(coord, 'name') == 'X':
                                tree.set_value(coord, 'value', str(profile[4]))
                            if tree.get_value(coord, 'name') == 'Y':
                                tree.set_value(coord, 'value', str(profile[5]))
                    break
            else:
                for d in tree.iter(i):
                    if tree.get_value(d, 'name') == 'Active':
                        tree.set_value(d, 'value', 'false')
                    if tree.get_value(d, 'name') == 'Primary':
                        tree.set_value(d, 'value', 'false')

        display_xml = os.path.join(cwd, 'Test_Data', 'displays.xml')
        tree.write(display_xml)
        os.remove(xml_file)

    elif __os.upper() == 'WINDOWS':
        display_config_file = os.path.join(cwd, 'Test_Data', 'displays.cfg')
        save_config = os.path.join(cwd, 'Test_Utility', 'MultiMonitorTool.exe') \
                      + ' /saveconfig ' + display_config_file
        os.system(save_config)
        with open(display_config_file, 'r') as f:
            lines = f.readlines()
        with open(display_config_file, 'w') as f_w:
            count = 0
            for line in lines:
                if count < len(profile_data):
                    if 'Width' in line:
                        line = line.replace(line, 'Width={}\n'.format(profile_data[count][1]))
                    if 'Height' in line:
                        line = line.replace(line, 'Height={}\n'.format(profile_data[count][2]))
                    if 'DisplayFrequency' in line:
                        line = line.replace(line, 'DisplayFrequency={}\n'.format(profile_data[count][3]))
                    if 'DisplayOrientation' in line:
                        line = line.replace(line, 'DisplayOrientation={}\n'.format(profile_data[count][6]))
                    if 'PositionX' in line:
                        line = line.replace(line, 'PositionX={}\n'.format(profile_data[count][4]))
                    if 'PositionY' in line:
                        line = line.replace(line, 'PositionY={}\n'.format(profile_data[count][5]))
                        count += 1
                    f_w.write(line)
                else:
                    if 'BitsPerPixel' in line:
                        line = line.replace(line, 'BitsPerPixel=0\n')
                    if 'Width' in line:
                        line = line.replace(line, 'Width=0\n')
                    if 'Height' in line:
                        line = line.replace(line, 'Height=0\n')
                    if 'DisplayFrequency' in line:
                        line = line.replace(line, 'DisplayFrequency=0\n')
                    if 'DisplayOrientation' in line:
                        line = line.replace(line, 'DisplayOrientation=0\n')
                    if 'PositionX' in line:
                        line = line.replace(line, 'PositionX=0\n')
                    if 'PositionY' in line:
                        line = line.replace(line, 'PositionY=0\n')
                        count += 1
                    f_w.write(line)
    else:
        print("os error")
        return False


def prepare_monitor_data(raw_data):
    layout = raw_data.get('layout')
    monitors = raw_data.get('monitors')
    prepared_monitors = []
    for i in monitors.keys():
        monitor_name = i
        width, height = monitors.get(i)[0].lower().split('x')
        frequency = monitors.get(i)[1]
        prepared_monitors.append([monitor_name, int(width), int(height), frequency])
    prepared_data = {'case_monitors': len(monitors.keys()), 'layout': layout, 'monitors': prepared_monitors}
    return prepared_data


def calculate_monitors_layout(data):
    if __os.upper() == 'LINUX':
        layout = LinuxLayout(data)
        layout_data = layout.calculate_layout()
        return layout_data
    elif __os.upper() == 'WINDOWS':
        layout_data = calculate_monitors_layout_wes(data)
        return layout_data


def calculate_monitors_layout_wes(data):
    processed_data = prepare_monitor_data(data)
    layout=processed_data.get("layout")
    case_monitors=processed_data.get('case_monitors')
    monitors=processed_data.get('monitors')
    if case_monitors==1:
        monitor_0_name = monitors[0][0]
        monitor_0_w = monitors[0][1]
        monitor_0_h = monitors[0][2]
        monitor_0_f = monitors[0][3]
        monitor_0_x = 0
        monitor_0_y = 0
        monitor_0_o = 0
        layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o]]
        print(layout_data)
        return layout_data
    elif case_monitors==2:
        if layout.upper()=='Landscape 2x1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w=monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x=0
            monitor_0_y =0
            monitor_0_o =0
            monitor_1_name = monitors[1][0]
            monitor_1_w=monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = -monitor_1_w
            monitor_1_y =0
            monitor_1_o = 0
            layout_data=[[monitor_0_name,monitor_0_w, monitor_0_h,monitor_0_f,monitor_0_x,monitor_0_y,monitor_0_o],
                         [monitor_1_name,monitor_1_w, monitor_1_h,monitor_1_f,monitor_1_x,monitor_1_y,monitor_1_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Landscape 1X2'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = monitor_0_y+monitor_1_h
            monitor_1_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='L Left'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][2]
            monitor_1_h = monitors[1][1]
            monitor_1_f = monitors[1][3]
            monitor_1_x = monitor_0_w
            monitor_1_y = 0
            monitor_1_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Portrait 2X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][2]
            monitor_1_h = monitors[1][1]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0+monitor_0_h
            monitor_1_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o]]
            print(layout_data)
            return layout_data
        else:
            raise Exception("unknown layout {}".format(layout))
    elif case_monitors==3:
        if layout.upper()=='Landscape 3X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0+monitor_0_w
            monitor_1_y = 0
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0+monitor_0_w+monitor_1_w
            monitor_2_y = 0
            monitor_2_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Portrait 3X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][2]
            monitor_1_h = monitors[1][1]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0-monitor_1_h
            monitor_1_o = 1
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][2]
            monitor_2_h = monitors[2][1]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0
            monitor_2_y = 0-monitor_1_h-monitor_2_h
            monitor_2_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Left L'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0+monitor_0_w
            monitor_1_y = 0
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0+monitor_0_w
            monitor_2_y = 0+monitor_2_h
            monitor_2_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Landscape 1X3'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0+monitor_0_h
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0
            monitor_2_y = 0+monitor_0_h+monitor_1_h
            monitor_2_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Portrait 1X3'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][2]
            monitor_1_h = monitors[1][1]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0-monitor_1_w
            monitor_1_y = 0
            monitor_1_o = 1
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][2]
            monitor_2_h = monitors[2][1]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0-monitor_1_w-monitor_2_w
            monitor_2_y = 0
            monitor_2_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Mixed 2+1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0+monitor_0_h
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0+monitor_1_h
            monitor_2_y = 0+monitor_0_h
            monitor_2_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Mixed 3X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0+monitor_0_h
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][2]
            monitor_2_h = monitors[2][1]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0
            monitor_2_y = 0+monitor_0_h+monitor_1_w
            monitor_2_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o]]
            print(layout_data)
            return layout_data
        else:
            raise Exception("unknown layout {}".format(layout))
    elif case_monitors==4:
        # """
        # only support same resolution
        # """
        # w_list=[monitors[0][1],monitors[1][1],monitors[2][1],monitors[3][1]]
        # w_list_set=set(w_list)
        # h_list=[monitors[0][2],monitors[1][2],monitors[2][2],monitors[3][2]]
        # h_list_set = set(h_list)
        # if len(w_list_set)!=1:
        #     print("only support same width resolution")
        #     return
        #     # raise Exception("only support same width resolution")
        # if len(h_list_set)!=1:
        #     print("only support same width resolution")
        #     return
        #     # raise Exception("only support same height resolution")

        if layout.upper()=='Landscape 2X2'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            w0=monitor_0_w
            h1=monitor_1_h
            h0=monitor_0_h
            monitor_1_x = w0
            monitor_1_y = -(h1-h0)
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            w2=monitor_2_w
            monitor_2_x = -(w2-w0)
            monitor_2_y = h0
            monitor_2_o = 0
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][1]
            monitor_3_h = monitors[3][2]
            monitor_3_f = monitors[3][3]
            monitor_3_x = w0
            monitor_3_y = h0
            monitor_3_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Portrait 2X2'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][2]
            monitor_1_h = monitors[1][1]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0-monitor_1_h
            monitor_1_o = 1
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][2]
            monitor_2_h = monitors[2][1]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0+monitor_0_w
            monitor_2_y = 0
            monitor_2_o = 1
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][2]
            monitor_3_h = monitors[3][1]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0+monitor_0_w
            monitor_3_y = 0-monitor_3_h
            monitor_3_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Left L'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            w0=monitor_0_w
            monitor_1_x = w0
            monitor_1_y = 0
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            w1=monitor_1_w
            monitor_2_x = w0+w1
            monitor_2_y = 0
            monitor_2_o = 0
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][1]
            monitor_3_h = monitors[3][2]
            monitor_3_f = monitors[3][3]
            h3=monitor_3_h
            monitor_3_x = w0+w1
            monitor_3_y = -h3
            monitor_3_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Landscape 4X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            w0=monitor_0_w
            monitor_1_x = w0
            monitor_1_y = 0
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            w1=monitor_1_w
            monitor_2_x = w0+w1
            monitor_2_y = 0
            monitor_2_o = 0
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][1]
            monitor_3_h = monitors[3][2]
            monitor_3_f = monitors[3][3]
            w2=monitor_2_w
            monitor_3_x = w0+w1+w2
            monitor_3_y = 0
            monitor_3_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Portrait 4X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][2]
            monitor_1_h = monitors[1][1]
            monitor_1_f = monitors[1][3]
            w0=monitor_0_w
            h0=monitor_0_h
            w1=monitor_1_w
            monitor_1_x = -(w1-w0)
            monitor_1_y =h0
            monitor_1_o = 1
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][2]
            monitor_2_h = monitors[2][1]
            monitor_2_f = monitors[2][3]
            w1=monitor_1_w
            h1=monitor_1_h
            monitor_2_x = -(w1-w0)
            monitor_2_y = h0+h1
            monitor_2_o = 1
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][2]
            monitor_3_h = monitors[3][1]
            monitor_3_f = monitors[3][3]
            w2=monitor_2_w
            h2=monitor_2_h
            monitor_3_x = -(w1-w0)
            monitor_3_y = h0+h1+h2
            monitor_3_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o]]
            print(layout_data)
            return layout_data
        # elif layout.upper()=='Portrait 4X1'.upper():
        #     monitor_0_name = monitors[0][0]
        #     monitor_0_w = monitors[0][2]
        #     monitor_0_h = monitors[0][1]
        #     monitor_0_f = monitors[0][3]
        #     monitor_0_x = 0
        #     monitor_0_y = 0
        #     monitor_0_o = 1
        #     monitor_1_name = monitors[1][0]
        #     monitor_1_w = monitors[1][2]
        #     monitor_1_h = monitors[1][1]
        #     monitor_1_f = monitors[1][3]
        #     w0=monitor_0_w
        #     monitor_1_x = w0
        #     monitor_1_y = 0
        #     monitor_1_o = 1
        #     monitor_2_name = monitors[2][0]
        #     monitor_2_w = monitors[2][2]
        #     monitor_2_h = monitors[2][1]
        #     monitor_2_f = monitors[2][3]
        #     w1=monitor_1_w
        #     monitor_2_x = w0+w1
        #     monitor_2_y = 0
        #     monitor_2_o = 1
        #     monitor_3_name = monitors[3][0]
        #     monitor_3_w = monitors[3][2]
        #     monitor_3_h = monitors[3][1]
        #     monitor_3_f = monitors[3][3]
        #     w2=monitor_2_w
        #     monitor_3_x = w0+w1+w2
        #     monitor_3_y = 0
        #     monitor_3_o = 1
        #     layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
        #                    [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
        #                    [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
        #                    [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o]]
        #     print(layout_data)
        #     return layout_data
        elif layout.upper()=='Mixed 4X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = monitor_0_h
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0
            monitor_2_y = monitor_0_h+monitor_1_h
            monitor_2_o = 0
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][2]
            monitor_3_h = monitors[3][1]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0
            monitor_3_y = 0+monitor_0_h+monitor_1_h+ monitor_2_h
            monitor_3_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o]]
            print(layout_data)
            return layout_data
        else:
            raise Exception("unknown layout {}".format(layout))
    elif case_monitors==6:
        """
        only support same resolution
        """
        w_list=[monitors[0][1],monitors[1][1],monitors[2][1],monitors[3][1],monitors[4][1],monitors[5][1],]
        w_list_set=set(w_list)
        h_list=[monitors[0][2],monitors[1][2],monitors[2][2],monitors[3][2],monitors[4][2],monitors[5][2]]
        h_list_set = set(h_list)
        if len(w_list_set)!=1:
            print("only support same width resolution")
            return
            # raise Exception("only support same width resolution")
        if len(h_list_set)!=1:
            print("only support same width resolution")
            return
            # raise Exception("only support same height resolution")

        if layout.upper()=='Landscape 3X2'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0+monitor_0_w
            monitor_1_y = 0
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0+monitor_0_w+monitor_1_w
            monitor_2_y = 0
            monitor_2_o = 0
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][1]
            monitor_3_h = monitors[3][2]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0
            monitor_3_y = 0+monitor_0_h
            monitor_3_o = 0
            monitor_4_name = monitors[4][0]
            monitor_4_w = monitors[4][1]
            monitor_4_h = monitors[4][2]
            monitor_4_f = monitors[4][3]
            monitor_4_x = 0+monitor_0_w
            monitor_4_y = 0+monitor_0_h
            monitor_4_o = 0
            monitor_5_name = monitors[5][0]
            monitor_5_w = monitors[5][1]
            monitor_5_h = monitors[5][2]
            monitor_5_f = monitors[5][3]
            monitor_5_x = 0+monitor_0_w+monitor_1_w
            monitor_5_y = 0+monitor_0_h
            monitor_5_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o],
                           [monitor_4_name, monitor_4_w, monitor_4_h, monitor_4_f, monitor_4_x, monitor_4_y, monitor_4_o],
                           [monitor_5_name, monitor_5_w, monitor_5_h, monitor_5_f, monitor_5_x, monitor_5_y, monitor_5_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Portrait 3X2'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][2]
            monitor_1_h = monitors[1][1]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0-monitor_1_h
            monitor_1_o = 1
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][2]
            monitor_2_h = monitors[2][1]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0
            monitor_2_y = 0-monitor_1_h-monitor_2_h
            monitor_2_o = 1
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][2]
            monitor_3_h = monitors[3][1]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0+monitor_0_w
            monitor_3_y = 0
            monitor_3_o = 1
            monitor_4_name = monitors[4][0]
            monitor_4_w = monitors[4][2]
            monitor_4_h = monitors[4][1]
            monitor_4_f = monitors[4][3]
            monitor_4_x = 0+monitor_0_w
            monitor_4_y = 0-monitor_4_h
            monitor_4_o = 1
            monitor_5_name = monitors[5][0]
            monitor_5_w = monitors[5][2]
            monitor_5_h = monitors[5][1]
            monitor_5_f = monitors[5][3]
            monitor_5_x = 0+monitor_0_w
            monitor_5_y = 0-monitor_4_h-monitor_5_h
            monitor_5_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o],
                           [monitor_4_name, monitor_4_w, monitor_4_h, monitor_4_f, monitor_4_x, monitor_4_y, monitor_4_o],
                           [monitor_5_name, monitor_5_w, monitor_5_h, monitor_5_f, monitor_5_x, monitor_5_y, monitor_5_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Left L'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0+monitor_0_w
            monitor_1_y = 0
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0+monitor_0_w+monitor_1_w
            monitor_2_y = 0
            monitor_2_o = 0
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][1]
            monitor_3_h = monitors[3][2]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0+monitor_0_w+monitor_1_w+monitor_2_w
            monitor_3_y = 0
            monitor_3_o = 0
            monitor_4_name = monitors[4][0]
            monitor_4_w = monitors[4][1]
            monitor_4_h = monitors[4][2]
            monitor_4_f = monitors[4][3]
            monitor_4_x = 0+monitor_0_w+monitor_1_w+monitor_2_w
            monitor_4_y = 0+monitor_4_h
            monitor_4_o = 0
            monitor_5_name = monitors[5][0]
            monitor_5_w = monitors[5][1]
            monitor_5_h = monitors[5][2]
            monitor_5_f = monitors[5][3]
            monitor_5_x = 0+monitor_0_w+monitor_1_w+monitor_2_w
            monitor_5_y = 0+monitor_4_h+monitor_5_h
            monitor_5_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o],
                           [monitor_4_name, monitor_4_w, monitor_4_h, monitor_4_f, monitor_4_x, monitor_4_y, monitor_4_o],
                           [monitor_5_name, monitor_5_w, monitor_5_h, monitor_5_f, monitor_5_x, monitor_5_y, monitor_5_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Landscape 6X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0+monitor_0_w
            monitor_1_y = 0
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0+monitor_0_w+monitor_1_w
            monitor_2_y = 0
            monitor_2_o = 0
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][1]
            monitor_3_h = monitors[3][2]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0+monitor_0_w+monitor_1_w+monitor_2_w
            monitor_3_y = 0
            monitor_3_o = 0
            monitor_4_name = monitors[4][0]
            monitor_4_w = monitors[4][1]
            monitor_4_h = monitors[4][2]
            monitor_4_f = monitors[4][3]
            monitor_4_x = 0+monitor_0_w+monitor_1_w+monitor_2_w+monitor_3_w
            monitor_4_y = 0
            monitor_4_o = 0
            monitor_5_name = monitors[5][0]
            monitor_5_w = monitors[5][1]
            monitor_5_h = monitors[5][2]
            monitor_5_f = monitors[5][3]
            monitor_5_x = 0+monitor_0_w+monitor_1_w+monitor_2_w+monitor_3_w+monitor_4_w
            monitor_5_y = 0
            monitor_5_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o],
                           [monitor_4_name, monitor_4_w, monitor_4_h, monitor_4_f, monitor_4_x, monitor_4_y, monitor_4_o],
                           [monitor_5_name, monitor_5_w, monitor_5_h, monitor_5_f, monitor_5_x, monitor_5_y, monitor_5_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Portrait 6X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][2]
            monitor_1_h = monitors[1][1]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0+monitor_0_h
            monitor_1_o = 1
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][2]
            monitor_2_h = monitors[2][1]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0
            monitor_2_y = 0+monitor_0_h+monitor_1_h
            monitor_2_o = 1
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][2]
            monitor_3_h = monitors[3][1]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0
            monitor_3_y = 0+monitor_0_h+monitor_1_h+monitor_2_h
            monitor_3_o = 1
            monitor_4_name = monitors[4][0]
            monitor_4_w = monitors[4][2]
            monitor_4_h = monitors[4][1]
            monitor_4_f = monitors[4][3]
            monitor_4_x = 0
            monitor_4_y = 0+monitor_0_h+monitor_1_h+monitor_2_h+monitor_3_h
            monitor_4_o = 1
            monitor_5_name = monitors[5][0]
            monitor_5_w = monitors[5][2]
            monitor_5_h = monitors[5][1]
            monitor_5_f = monitors[5][3]
            monitor_5_x = 0
            monitor_5_y = 0+monitor_0_h+monitor_1_h+monitor_2_h+monitor_3_h+monitor_4_h
            monitor_5_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o],
                           [monitor_4_name, monitor_4_w, monitor_4_h, monitor_4_f, monitor_4_x, monitor_4_y, monitor_4_o],
                           [monitor_5_name, monitor_5_w, monitor_5_h, monitor_5_f, monitor_5_x, monitor_5_y, monitor_5_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Mixed 6X1'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0+monitor_0_h
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0
            monitor_2_y = 0+monitor_0_h+monitor_1_h
            monitor_2_o = 0
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][1]
            monitor_3_h = monitors[3][2]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0
            monitor_3_y =  0+monitor_0_h+monitor_1_h+monitor_2_h
            monitor_3_o = 0
            monitor_4_name = monitors[4][0]
            monitor_4_w = monitors[4][1]
            monitor_4_h = monitors[4][2]
            monitor_4_f = monitors[4][3]
            monitor_4_x =0
            monitor_4_y = 0+monitor_0_h+monitor_1_h+monitor_2_h+monitor_3_h
            monitor_4_o = 0
            monitor_5_name = monitors[5][0]
            monitor_5_w = monitors[5][2]
            monitor_5_h = monitors[5][1]
            monitor_5_f = monitors[5][3]
            monitor_5_x = 0
            monitor_5_y = 0+monitor_0_h+monitor_1_h+monitor_2_h+monitor_3_h+monitor_4_h
            monitor_5_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o],
                           [monitor_4_name, monitor_4_w, monitor_4_h, monitor_4_f, monitor_4_x, monitor_4_y, monitor_4_o],
                           [monitor_5_name, monitor_5_w, monitor_5_h, monitor_5_f, monitor_5_x, monitor_5_y, monitor_5_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Landscape 2X3'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][1]
            monitor_0_h = monitors[0][2]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 0
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][1]
            monitor_1_h = monitors[1][2]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0
            monitor_1_y = 0+monitor_0_h
            monitor_1_o = 0
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][1]
            monitor_2_h = monitors[2][2]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0
            monitor_2_y = 0+monitor_0_h+monitor_1_h
            monitor_2_o = 0
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][1]
            monitor_3_h = monitors[3][2]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0+monitor_0_w
            monitor_3_y = 0
            monitor_3_o = 0
            monitor_4_name = monitors[4][0]
            monitor_4_w = monitors[4][1]
            monitor_4_h = monitors[4][2]
            monitor_4_f = monitors[4][3]
            monitor_4_x = 0+monitor_0_w
            monitor_4_y = 0+monitor_3_h
            monitor_4_o = 0
            monitor_5_name = monitors[5][0]
            monitor_5_w = monitors[5][1]
            monitor_5_h = monitors[5][2]
            monitor_5_f = monitors[5][3]
            monitor_5_x = 0+monitor_0_w
            monitor_5_y = 0+monitor_3_h+monitor_4_h
            monitor_5_o = 0
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o],
                           [monitor_4_name, monitor_4_w, monitor_4_h, monitor_4_f, monitor_4_x, monitor_4_y, monitor_4_o],
                           [monitor_5_name, monitor_5_w, monitor_5_h, monitor_5_f, monitor_5_x, monitor_5_y, monitor_5_o]]
            print(layout_data)
            return layout_data
        elif layout.upper()=='Portrait 2x3'.upper():
            monitor_0_name = monitors[0][0]
            monitor_0_w = monitors[0][2]
            monitor_0_h = monitors[0][1]
            monitor_0_f = monitors[0][3]
            monitor_0_x = 0
            monitor_0_y = 0
            monitor_0_o = 1
            monitor_1_name = monitors[1][0]
            monitor_1_w = monitors[1][2]
            monitor_1_h = monitors[1][1]
            monitor_1_f = monitors[1][3]
            monitor_1_x = 0-monitor_1_w
            monitor_1_y = 0
            monitor_1_o = 1
            monitor_2_name = monitors[2][0]
            monitor_2_w = monitors[2][2]
            monitor_2_h = monitors[2][1]
            monitor_2_f = monitors[2][3]
            monitor_2_x = 0-monitor_1_w-monitor_2_w
            monitor_2_y = 0
            monitor_2_o = 1
            monitor_3_name = monitors[3][0]
            monitor_3_w = monitors[3][2]
            monitor_3_h = monitors[3][1]
            monitor_3_f = monitors[3][3]
            monitor_3_x = 0
            monitor_3_y = 0+monitor_0_h
            monitor_3_o = 1
            monitor_4_name = monitors[4][0]
            monitor_4_w = monitors[4][2]
            monitor_4_h = monitors[4][1]
            monitor_4_f = monitors[4][3]
            monitor_4_x = 0-monitor_4_w
            monitor_4_y = 0+monitor_0_h
            monitor_4_o = 1
            monitor_5_name = monitors[5][0]
            monitor_5_w = monitors[5][2]
            monitor_5_h = monitors[5][1]
            monitor_5_f = monitors[5][3]
            monitor_5_x = 0-monitor_4_w-monitor_5_w
            monitor_5_y = 0+monitor_0_h
            monitor_5_o = 1
            layout_data = [[monitor_0_name, monitor_0_w, monitor_0_h, monitor_0_f, monitor_0_x, monitor_0_y, monitor_0_o],
                           [monitor_1_name, monitor_1_w, monitor_1_h, monitor_1_f, monitor_1_x, monitor_1_y, monitor_1_o],
                           [monitor_2_name, monitor_2_w, monitor_2_h, monitor_2_f, monitor_2_x, monitor_2_y, monitor_2_o],
                           [monitor_3_name, monitor_3_w, monitor_3_h, monitor_3_f, monitor_3_x, monitor_3_y, monitor_3_o],
                           [monitor_4_name, monitor_4_w, monitor_4_h, monitor_4_f, monitor_4_x, monitor_4_y, monitor_4_o],
                           [monitor_5_name, monitor_5_w, monitor_5_h, monitor_5_f, monitor_5_x, monitor_5_y, monitor_5_o]]
            print(layout_data)
            return layout_data
        else:
            raise Exception("unknown layout {}".format(layout))


class LinuxLayout:
    def __init__(self, data):
        processed_data = prepare_monitor_data(data)
        self.layout = processed_data.get("layout")
        self.case_monitors = processed_data.get('case_monitors')
        self.monitors = processed_data.get('monitors')
        self.layout_data = []
        for i in range(self.case_monitors):
            monitor_data = [self.monitors[i][0], self.monitors[i][1], self.monitors[i][2], self.monitors[i][3], 0, 0, 0]
            self.layout_data.append(monitor_data)
        # print(self.layout_data)

    def calculate_layout(self):
        if self.case_monitors == 1:
            print(self.layout_data)
            return self.layout_data
        if self.case_monitors == 2:
            if self.layout.upper() in ['Landscape 2x1'.upper(), 'Landscape 1X2'.upper(), 'L Left'.upper(),
                                       'Portrait 2X1'.upper()]:
                if self.layout.upper() == 'Landscape 2x1'.upper():
                    self.layout_data[0][4] = self.monitors[1][1]
                elif self.layout.upper() == 'Landscape 1X2'.upper():
                    self.layout_data[1][5] = self.monitors[0][2]
                elif self.layout.upper() == 'L Left'.upper():
                    self.layout_data[1][4] = self.monitors[0][1]
                    self.layout_data[1][6] = 90
                elif self.layout.upper() == 'Portrait 2X1'.upper():
                    self.layout_data[0][6] = 270
                    self.layout_data[1][4] = self.monitors[0][2]
                    self.layout_data[1][6] = 270
                print(self.layout_data)
                return self.layout_data
            else:
                raise Exception("unknown layout {}".format(self.layout))
        if self.case_monitors == 3:
            if self.layout.upper() in ['Landscape 3X1'.upper(), 'Portrait 3X1'.upper(), 'Left L'.upper(),
                                       'Landscape 1X3'.upper(), 'Portrait 1X3'.upper(), 'Mixed 2+1'.upper(),
                                       'Mixed 3X1'.upper()]:
                if self.layout.upper() == 'Landscape 3X1'.upper():
                    self.layout_data[1][4] = self.monitors[0][1]
                    self.layout_data[2][4] = self.monitors[0][1] + self.monitors[1][1]
                elif self.layout.upper() == 'Portrait 3X1'.upper():
                    self.layout_data[0][6] = 270
                    self.layout_data[1][4] = self.monitors[0][2]
                    self.layout_data[1][6] = 270
                    self.layout_data[2][4] = self.monitors[0][2] * 2
                    self.layout_data[2][6] = 270
                elif self.layout.upper() == 'Left L'.upper():
                    self.layout_data[0][4] = self.monitors[1][1]
                    self.layout_data[1][5] = self.monitors[0][2]
                    self.layout_data[2][4] = self.monitors[1][1]
                    self.layout_data[2][5] = self.monitors[0][2]
                elif self.layout.upper() == 'Landscape 1X3'.upper():
                    self.layout_data[1][5] = self.monitors[0][2]
                    self.layout_data[2][5] = self.monitors[0][2] + self.monitors[1][2]
                elif self.layout.upper() == 'Portrait 1X3'.upper():
                    self.layout_data[0][6] = 270
                    self.layout_data[1][5] = self.monitors[0][1]
                    self.layout_data[1][6] = 270
                    self.layout_data[2][5] = self.monitors[0][1] * 2
                    self.layout_data[2][6] = 270
                elif self.layout.upper() == 'Mixed 2+1'.upper():
                    if self.monitors[0][1] == self.monitors[1][1]:       # dtc
                        self.layout_data[0][4] = self.monitors[1][1]
                        self.layout_data[0][6] = 90
                        self.layout_data[2][5] = self.monitors[1][2]
                    else:                                                # mtc
                        self.layout_data[0][4] = self.monitors[1][1] - self.monitors[0][1]
                        self.layout_data[1][5] = self.monitors[0][2]
                        self.layout_data[2][4] = self.monitors[0][1]
                        self.layout_data[2][6] = 90
                elif self.layout.upper() == 'Mixed 3X1'.upper():
                    if self.monitors[0][1] == self.monitors[1][1]:
                        self.layout_data[1][4] = self.monitors[0][2]
                        self.layout_data[0][6] = 270
                        self.layout_data[2][4] = self.monitors[0][2] + self.monitors[1][1]
                        self.layout_data[2][6] = 270
                    else:
                        self.layout_data[0][4] = self.monitors[1][2]
                        self.layout_data[1][6] = 270
                        self.layout_data[2][4] = self.monitors[1][2] + self.monitors[0][1]
                        self.layout_data[2][6] = 270
                print(self.layout_data)
                return self.layout_data
            else:
                raise Exception("unknown layout {}".format(self.layout))
        if self.case_monitors == 4:
            if self.layout.upper() in ['Landscape 2X2'.upper(), 'Portrait 2X2'.upper(), 'Left L'.upper(),
                                       'Landscape 4X1'.upper(), 'Portrait 4X1'.upper(), 'Mixed 4X1'.upper()]:
                if self.layout.upper() == 'Landscape 2X2'.upper():
                    self.layout_data[0][4] = self.monitors[2][1] - self.monitors[0][1]
                    self.layout_data[0][5] = self.monitors[1][2] - self.monitors[0][2]
                    self.layout_data[1][4] = self.monitors[2][1]
                    self.layout_data[2][5] = self.monitors[1][2]
                    self.layout_data[3][4] = self.monitors[2][1]
                    self.layout_data[3][5] = self.monitors[1][2]
                elif self.layout.upper() == 'Portrait 2X2'.upper():
                    if self.monitors[0][1] == self.monitors[1][1]:            # dtc
                        self.layout_data[0][6] = 270
                    else:                                                     # mtc
                        self.layout_data[0][4] = abs(self.monitors[1][2]-self.monitors[0][1])
                        self.layout_data[0][5] = self.monitors[1][1]-self.monitors[0][2]
                    self.layout_data[1][5] = self.monitors[2][1]
                    self.layout_data[1][6] = 270
                    self.layout_data[2][4] = self.monitors[1][2]
                    self.layout_data[2][6] = 270
                    self.layout_data[3][4] = self.monitors[1][2]
                    self.layout_data[3][5] = self.monitors[2][1]
                    self.layout_data[3][6] = 270
                elif self.layout.upper() == 'Left L'.upper():
                    self.layout_data[0][4] = self.monitors[1][1] + self.monitors[2][1]
                    self.layout_data[1][5] = self.monitors[0][2]
                    self.layout_data[2][4] = self.monitors[1][1]
                    self.layout_data[2][5] = self.monitors[0][2]
                    self.layout_data[3][4] = self.monitors[1][1] + self.monitors[2][1]
                    self.layout_data[3][5] = self.monitors[0][2]
                elif self.layout.upper() == 'Landscape 4X1'.upper():
                    self.layout_data[1][4] = self.monitors[0][1]
                    self.layout_data[2][4] = self.monitors[0][1] + self.monitors[1][1]
                    self.layout_data[3][4] = self.monitors[0][1] + self.monitors[1][1] + self.monitors[2][1]
                elif self.layout.upper() == 'Portrait 4X1'.upper():
                    if self.monitors[0][1] == self.monitors[1][1]:      # dtc
                        self.layout_data[0][6] = 270
                        self.layout_data[1][4] = self.monitors[0][2]
                    else:                                               # mtc
                        self.layout_data[1][4] = self.monitors[0][1]
                    self.layout_data[1][6] = 270
                    self.layout_data[2][4] = self.monitors[0][2] + self.monitors[1][2]
                    self.layout_data[2][6] = 270
                    self.layout_data[3][4] = self.layout_data[2][4] + self.monitors[2][2]
                    self.layout_data[3][6] = 270
                elif self.layout.upper() == 'Mixed 4X1'.upper():
                    if self.monitors[0][1] == self.monitors[1][1]:                     # dtc
                        self.layout_data[0][6] = 270
                        self.layout_data[1][4] = self.monitors[0][2]
                        self.layout_data[2][4] = self.monitors[0][2] + self.monitors[1][1]
                    else:                                                              # mtc
                        self.layout_data[0][4] = self.monitors[1][2]
                        self.layout_data[1][6] = 270
                        self.layout_data[2][4] = self.monitors[0][1] + self.monitors[1][2]
                    self.layout_data[3][4] = self.layout_data[2][4] + self.monitors[2][1]
                    self.layout_data[3][6] = 270
                print(self.layout_data)
                return self.layout_data
            else:
                raise Exception("unknown layout {}".format(self.layout))
        if self.case_monitors == 6:
            if self.layout.upper() in ['Landscape 3X2'.upper(), 'Portrait 3X2'.upper(), 'Left L'.upper(),
                                       'Landscape 6X1'.upper(), 'Portrait 6X1'.upper(), 'Mixed 6X1'.upper(),
                                       'Landscape 2X3'.upper(), 'Portrait 2x3'.upper()]:
                if self.layout.upper() == 'Landscape 3X2'.upper():
                    self.layout_data[1][4] = self.monitors[0][1]
                    self.layout_data[2][4] = self.monitors[0][1] + self.monitors[1][1]
                    self.layout_data[3][5] = self.monitors[0][2]
                    self.layout_data[4][4] = self.monitors[0][1]
                    self.layout_data[4][5] = self.monitors[0][2]
                    self.layout_data[5][4] = self.monitors[0][1] + self.monitors[1][1]
                    self.layout_data[5][5] = self.monitors[0][2]
                elif self.layout.upper() == 'Portrait 3X2'.upper():
                    self.layout_data[0][6] = 270
                    self.layout_data[1][4] = self.monitors[0][2]
                    self.layout_data[1][6] = 270
                    self.layout_data[2][4] = self.monitors[0][2] + self.monitors[1][2]
                    self.layout_data[2][6] = 270
                    self.layout_data[3][5] = self.monitors[0][1]
                    self.layout_data[3][6] = 270
                    self.layout_data[4][4] = self.monitors[0][2]
                    self.layout_data[4][5] = self.monitors[0][1]
                    self.layout_data[4][6] = 270
                    self.layout_data[5][4] = self.monitors[4][2] + self.monitors[5][2]
                    self.layout_data[5][5] = self.monitors[0][1]
                    self.layout_data[5][6] = 270
                elif self.layout.upper() == 'Left L'.upper():
                    self.layout_data[0][4] = self.monitors[2][1] * 3
                    self.layout_data[1][4] = self.monitors[2][1] * 3
                    self.layout_data[1][5] = self.monitors[0][2]
                    self.layout_data[2][5] = self.monitors[0][2] * 2
                    self.layout_data[3][4] = self.monitors[2][1]
                    self.layout_data[3][5] = self.monitors[0][2] * 2
                    self.layout_data[4][4] = self.monitors[2][1] + self.monitors[3][1]
                    self.layout_data[4][5] = self.monitors[0][2] * 2
                    self.layout_data[5][4] = self.monitors[2][1] + self.monitors[3][1] + self.monitors[4][1]
                    self.layout_data[5][5] = self.monitors[0][2] * 2
                elif self.layout.upper() == 'Landscape 6X1'.upper():
                    for k in range(self.case_monitors):
                        self.layout_data[k][4] = self.monitors[0][1] * k
                elif self.layout.upper() == 'Portrait 6X1'.upper():
                    for k in range(self.case_monitors):
                        self.layout_data[k][4] = self.monitors[0][2] * k
                        self.layout_data[k][6] = 270
                elif self.layout.upper() == 'Mixed 6X1'.upper():
                    self.layout_data[0][6] = 270
                    self.layout_data[1][4] = self.monitors[0][2]
                    self.layout_data[2][4] = self.monitors[0][2] + self.monitors[1][1]
                    self.layout_data[3][4] = self.layout_data[2][4] + self.monitors[2][1]
                    self.layout_data[4][4] = self.layout_data[3][4] + self.monitors[3][1]
                    self.layout_data[5][4] = self.layout_data[4][4] + self.monitors[4][1]
                    self.layout_data[5][6] = 270
                elif self.layout.upper() == 'Landscape 2X3'.upper():
                    self.layout_data[1][4] = self.monitors[0][1]
                    self.layout_data[2][4] = self.monitors[0][1]
                    self.layout_data[2][5] = self.monitors[1][2]
                    self.layout_data[3][5] = self.monitors[0][2]
                    self.layout_data[4][5] = self.monitors[0][2] + self.monitors[3][2]
                    self.layout_data[5][4] = self.monitors[0][1]
                    self.layout_data[5][5] = self.monitors[0][2] + self.monitors[3][2]
                elif self.layout.upper() == 'Portrait 2x3'.upper():
                    self.layout_data[0][6] = 270
                    self.layout_data[1][4] = self.monitors[0][2]
                    self.layout_data[1][6] = 270
                    self.layout_data[2][4] = self.monitors[0][2]
                    self.layout_data[2][5] = self.monitors[0][1]
                    self.layout_data[2][6] = 270
                    self.layout_data[3][5] = self.monitors[0][1]
                    self.layout_data[3][6] = 270
                    self.layout_data[4][5] = self.monitors[0][1] * 2
                    self.layout_data[4][6] = 270
                    self.layout_data[5][4] = self.monitors[0][2]
                    self.layout_data[5][5] = self.monitors[0][1] * 2
                    self.layout_data[5][6] = 270
                print(self.layout_data)
                return self.layout_data
            else:
                raise Exception("unknown layout {}".format(self.layout))


def check_resolution_support(d: dict):
    """
    filter the available port and fix the resolution catch by  `xrandr`
    d: response for method analyze_case_name()
    re[r"^ *?(.*?) connected"]: display_port_item, return the display port like DisplayPort-1-0, Type-C
    re[r"^ *?(\d+x\d+) {3} *?(.*)"]: mode_item,
        return two group contains resolution and fresh rate, like ['3840x2160', '60.00    29.98    24.00']]
    """
    dic = d.get("monitors")
    monitors_info = os.popen('xrandr').readlines()
    monitor_dict = {}
    dp = ""
    for i in monitors_info:
        display_port_item = re.search(r"^ *?(.*?) connected", i)
        if display_port_item:
            dp = display_port_item.group(1)
            print(dp)
            monitor_dict[dp] = {}
        if dp:
            mode_item = re.search(r"^ *?(\d+x\d+) {3} *?(.*)", i)
            if mode_item:
                new_list = []
                res, fresh = mode_item.groups()
                fresh_list = fresh.split(" ")
                for i in fresh_list:
                    fresh_new = i.strip("*+i")
                    if fresh_new:
                        new_list.append(fresh_new)
                monitor_dict[dp][res] = new_list
    print(monitor_dict)

    def check_exist():
        """
        param: k,str DisplayPort
        param: v, list [resolution, fresh_rate]
        """

        resolution, fresh_rate = v
        fresh_rate = float(fresh_rate)
        response = monitor_dict.get(k, {}).get(resolution, [])
        if not response:
            return False
        for i in response:
            actual_res = float(i)
            if actual_res < 61 and abs(fresh_rate-actual_res) < 3:
                new_d["monitors"][k] = [resolution, actual_res]
                break
            elif actual_res >= 61:
                new_d["monitors"][k] = [resolution, actual_res]
        return True

    new_d = copy.deepcopy(d)
    for k, v in dic.items():
        result = check_exist()
        assert result, "{} not Exist or disconnect or {} not support {}".format(k, k, v)
    return new_d