import subprocess
from Common.picture_operator import *
from Common.exception import IconNotExistError
from Common.tool import click, type_string, press_key, moveto, right_click, tap_key, drag
import functools
from Common import common_function
from Common.common_function import get_folder_items, get_current_dir
from Common.log import Logger
from Test_Script.ts_precheck import precheck_function
import pyautogui
import re


def log():
    return Logger()


def check_radio():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self, pms, loc, shape = args
            flag = kwargs.get("radio", "")
            print(args, flag, "check_radio")
            loc_x, loc_y = loc
            print(loc_x, loc_y, "check_radio")
            off_x, off_y = 22, 5
            fil_x = loc_x - off_x if loc_x - off_x > 0 else 0
            fil_y = loc_y - off_y if loc_y - off_y > 0 else 0
            filter_dic = {"left": fil_x, "top": fil_y, "width": 30, "height": 30}
            save_path = get_current_dir() + "/Test_Data/td_power_manager/temp.png"
            capture_screen_by_loc(save_path, filter_dic)
            if flag.upper() == "ON":
                path_sel = self._file_path + "Common/Radio_selected/"
                pic_path_list = get_folder_items(path_sel, file_only=True)
                for i in pic_path_list:
                    if compare_pic_similarity(path_sel + i, save_path):
                        print(self.Info.format("Status is already checked"))
                        return
                else:
                    func(*args, **kwargs)
            elif flag.upper() == "OFF":
                path_sel = self._file_path + "Common/Radio_unselected/"
                pic_path_list = get_folder_items(path_sel, file_only=True)
                for i in pic_path_list:
                    if compare_pic_similarity(path_sel + i, save_path):
                        print(self.Info.format("Status is already unchecked"))
                        return
                else:
                    func(*args, **kwargs)
        return wrapper

    return decorator


class PowerManager:
    _file_path = get_current_dir() + "/Test_Data/td_power_manager/PowerManager/"
    _class_name = ""
    Info = '\033[1;21;1m#{}#\033[0m'
    Error = '\033[1;31;1m#{}#\033[0m'
    Warning = '\033[1;33;1m#{}#\033[0m'
    Path_Error = Error.format("pic folder is null!! in {}")
    common = {}
    select = {}

    def __init__(self):
        self._class_name = self.__class__.__name__
        self.file_path = self._file_path + self._class_name + "/"

    @staticmethod
    def open_power_manager():
        os.popen("hptc-control-panel --config-panel /etc/hptc-control-panel/applications/hptc-power-mgr.desktop")

    @staticmethod
    def open_power_manager_from_tray():
        log().info("start open power manager from tray")
        platform = common_function.get_platform()
        if 'MT' not in platform.upper():
            log().error("dtc can't open power manager from tray")
            return False
        os.system("wmctrl -c 'Control Panel'")
        x, y = common_function.screen_resolution()
        power_setting_word = os.path.join(get_current_dir(), "Test_Data", "td_power_manager", "systray_icon",
                                          "_pm_adjust_power_settings")
        x, y = int(x), int(y)
        icon_info = os.popen('xwininfo -name hptc-battery-systray').read()
        print(icon_info)
        res = re.findall(r"Absolute upper-left X:.*?(\d{3,4}).{0,100}Absolute upper-left Y:.*?(\d{3,4})"
                         r".{0,100}Width:.*?(\d{2}).{0,100}Height:.*?(\d{2})", icon_info, re.S)
        print(res)
        log().info('current screen size is : {} x {}'.format(x, y))
        ts = precheck_function.thinpro_or_smartzero()
        if ts == "thinpro":          # ThinPro mode
            if not res:
                log().error("can't get battery size and loc")
                return False
            res = res[0]
            x, y, w, h = int(res[0]), int(res[1]), int(res[2]), int(res[3])
            log().info('battery loc: {} x {}, battery icon size: {} x {}'.format(x, y, w, h))
            right_click(int(x + w/2), int(y + h/2))
            time.sleep(1)
            rs = wait_element(power_setting_word, cycle=1, offset=(0, 0))
            if rs:
                moveto(rs[0][0], rs[0][1]+5)
                click(rs[0][0], rs[0][1]+5)
                time.sleep(2)
                window = subprocess.getoutput("wmctrl -lx | grep -i 'control panel'")
                if window:
                    log().info("open power manager from tray success")
                    return True
                else:
                    log().error("open power manager from tray fail")
                    return False
            else:
                log().error("open power manager from tray fail")
                return False
        else:                                   # smart zero mode
            k = int(y/2)
            moveto(x-1, k)
            time.sleep(1)
            for j in range(0, 8):
                moveto(x - 1, k)
                click(x - 10, k + 226 - (50 * j))
                time.sleep(0.2)
                right_click(x - 10, k + 226 - (50 * j))
                time.sleep(1)
                os.system("wmctrl -c 'HP Virtual Keyboard'")
                rs = wait_element(power_setting_word, cycle=1, offset=(0, 0))
                if rs:
                    moveto(rs[0][0], rs[0][1] + 5)
                    click(rs[0][0], rs[0][1] + 5)
                    time.sleep(2)
                    window = subprocess.getoutput("wmctrl -lx | grep -i 'control panel'")
                    if window:
                        log().info("open power manager from tray success")
                        return True
                    else:
                        log().error("open power manager from tray fail")
                        return False
            else:
                log().error("open power manager from tray fail")
                return False

    @staticmethod
    def open_power_manager_from_control_panel():
        for _ in range(2):
            os.system("wmctrl -c 'Control Panel'")
            precheck_function.open_window("power manager")
            window = subprocess.getoutput("wmctrl -lx | grep -i 'control panel'")
            if window:
                log().info("open power manager from control panel success")
                return True
            time.sleep(5)
        else:
            log().error("open power manager from control panel fail")
            return False

    @staticmethod
    def close_all_power_manager():
        os.popen("hptc-control-panel --term")

    @staticmethod
    def _click(loc, offset=(0, 0), num=1, interval=0.1):
        res = list(map(lambda x, y: x+y, loc, offset))
        time.sleep(1)
        # return click(*res, num=num)
        return pyautogui.click(res, clicks=num, interval=interval)

    @staticmethod
    def _get_loc_from_path_list(path, icon_path_list, **kwargs):
        offset = kwargs.get("offset", (0, 0))
        for i in icon_path_list:
            print(path + i)
            res = wait_element(path + i, cycle=2, offset=offset)
            if res:
                return res
        else:
            raise IconNotExistError("Can't find icon")

    @check_radio()
    def _set_radio(self, pms, *args, **kwargs):
        loc, shape, *arg = args
        offset = pms.get("radio", ())
        assert offset != (), AttributeError("no Attribute {}".format("radio"))
        re_loc = list(map(lambda x, y: x + y, loc, (0, int(shape[0] / 2))))
        print(loc, re_loc, shape[0], "set_radio")
        self._click(re_loc, offset)

    def _set_text(self, pms, *args, **kwargs):
        loc, shape, text, *arg = args
        offset = pms.get("text", ())
        assert offset != (), AttributeError("no Attribute {}".format("text"))
        re_loc = list(map(lambda x, y: x + y, loc, (shape[1], int(shape[0] / 2))))
        self._click(re_loc, offset, num=3)
        time.sleep(0.5)
        press_key("BackSpace")
        press_key("BackSpace")
        time.sleep(0.5)
        type_string(text)

    def _set_selected(self, pms, *args, **kwargs):
        loc, shape, selected, *arg = args
        print(selected, "set_sel")
        offset = pms.get("selected", ())
        assert offset != (), AttributeError("no Attribute {}".format("selected"))
        re_loc = list(map(lambda x, y: x + y, loc, (shape[1], int(shape[0] / 2))))
        self._click(re_loc, offset)
        time.sleep(0.5)
        if isinstance(selected, int):
            path = self.file_path + "{}/{}/".format(pms.get("index"), selected)
            pic_path_list = get_folder_items(path, file_only=True)
            assert pic_path_list, self.Path_Error.format(path)
            res = self._get_loc_from_path_list(path, pic_path_list)
            loc, shape = res
            offset = int(shape[1] / 2), int(shape[0] / 2)
            self._click(loc, offset)
            PowerManager.select["{}".format(self._class_name)] = selected
        elif callable(selected):
            path = self.file_path + "{}/".format(pms.get("index"))
            selected(path=path, **kwargs)
        return

    def set_brightness_mtc_only(self, percent="0"):
        _bar_length = 405
        _bar_scope_per = 3.95
        _icon = (13, 13)
        _brightness_path = self._file_path + "Common/Brightness/"
        _icon_path = self._file_path + "Common/Brightness/Bright_Icon/"
        pic_path_list = get_folder_items(_brightness_path, file_only=True)
        print(_brightness_path, pic_path_list)
        assert pic_path_list, self.Path_Error.format(_brightness_path)
        res = self._get_loc_from_path_list(_brightness_path, pic_path_list)
        loc, shape = res
        print(res)
        loc_x_r = loc[0] + int(shape[1])

        icon_path_list = get_folder_items(_icon_path, file_only=True)
        assert pic_path_list, self.Path_Error.format(_icon_path)
        res = self._get_loc_from_path_list(_icon_path, icon_path_list)
        loc_i, shape_i = res
        offset_loc = (loc_i[0] + int(shape_i[1] / 2), loc_i[1] + int(shape_i[0] / 2))
        offset_x = _bar_scope_per * (percent-1) if isinstance(percent, float) else _bar_scope_per * (int(percent) -1)
        offset_x = int(round(offset_x + 7))
        drag(offset_loc, (loc_x_r + int(offset_x), offset_loc[1]))

    def set(self, pms, *args, **kwargs):
        radio = kwargs.get("radio", False)
        text = kwargs.get("text", "")
        selected = kwargs.get("selected", "")
        index = pms.get("index")
        if text or selected:
            print(pms.get("radio"), radio,)
            if isinstance(pms.get("radio"), tuple) and not radio:
                print(radio, "1234")
                print(self.Warning.format("Please set radio first!, try to work around"))
                radio = True
                kwargs["radio"] = "on"
        pic_parent_path = self.file_path + "{}/".format(index)
        print(pic_parent_path, "pic_path", 'set')
        pic_path_list = get_folder_items(pic_parent_path, file_only=True)
        assert pic_path_list, self.Path_Error.format(pic_parent_path)
        res = self._get_loc_from_path_list(pic_parent_path, pic_path_list)
        loc, shape = res
        if radio:
            self._set_radio(pms, loc, shape, **kwargs)
        if text:
            self._set_text(pms, loc, shape, text)
        if selected:
            self._set_selected(pms, loc, shape, selected, **kwargs)

    def switch(self, path=""):
        icon_path_list = get_folder_items(self.file_path, file_only=True)
        print(icon_path_list)
        res = self._get_loc_from_path_list(self.file_path, icon_path_list)
        loc, shape = res
        offset = int(shape[1] / 2), int(shape[0] / 2)
        self._click(loc, offset)
        PowerManager.common["switch"] = self._class_name
        return

    @classmethod
    def apply(cls):
        print(cls._file_path, "apply")
        icon_path_list = get_folder_items(cls._file_path, file_only=True)
        assert icon_path_list, cls.Path_Error.format(icon_path_list)
        print(icon_path_list, "apply")
        res = cls._get_loc_from_path_list(cls._file_path, icon_path_list)
        loc, shape = res
        cls._click(loc, [int(shape[1] / 2), int(shape[0] / 2)])
        print(loc, shape, "apply")


if __name__ == '__main__':
    # @PowerManager.check_radio()
    # def fun():
    #     print("123")
    #     return
    #
    # fun()
    pass