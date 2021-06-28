from Test_Script.ts_power_manager.power_manager_base import *
import pyautogui


class UniqueSettings(PowerManager):
    @staticmethod
    def copy_pic(pic_path):
        os.popen("rm /home/user/Images/*.png")
        os.popen("rm /home/user/*.png")
        os.popen("rm /media/*.png")
        os.popen("rm /home/user/Images/*.jpg")
        os.popen("rm /home/user/*.jpg")
        os.popen("rm /media/*.jpg")
        os.popen("cp {} /home/user/Images".format(pic_path))
        os.popen("cp {} /media".format(pic_path))
        os.popen("cp {} /home/user/".format(pic_path))
        return

    @staticmethod
    def _customised(index, **kwargs):
        parent_path = kwargs.get("path")
        print(parent_path)
        print(PowerManager.select, "      P")
        path = parent_path + "{}/".format(index)
        pic_path_list = get_folder_items(path, file_only=True)
        assert pic_path_list, PowerManager.Path_Error.format(path)
        res = PowerManager._get_loc_from_path_list(path, pic_path_list)
        loc, shape = res
        offset = (-10, int(shape[0] / 2))
        PowerManager._click(loc, offset)
        pic_path = get_current_dir() + "/Test_Data/td_power_manager/verify_screensaver_diff_image/source_pic/pic.jpg"
        pic_path = kwargs.get("pic_path", pic_path)
        if PowerManager.select.get("ScreenSaver", -1) in [2, 3]:
            pic_path = kwargs.get("pic_path", os.path.dirname(pic_path))
            assert os.path.isdir(pic_path), "Must be a path not a pic"
            time.sleep(1)
            pyautogui.typewrite(pic_path, interval=0.1)
            time.sleep(1)
            tap_key("KP_Enter")
            return
        UniqueSettings.copy_pic(pic_path)
        pic_search_path = get_current_dir() + "/Test_Data/td_power_manager/PowerManager/Common/File/"
        pic_path_list = get_folder_items(pic_search_path, file_only=True)
        assert pic_path_list, PowerManager.Path_Error.format(path)
        res = PowerManager._get_loc_from_path_list(pic_search_path, pic_path_list)
        loc, shape = res
        offset = (int(shape[1] / 2), int(shape[0]/2 + 5))
        PowerManager._click(loc, offset, num=2, interval=0.2)
        tap_key("KP_Enter")

    @staticmethod
    def system_image(**kwargs):
        return UniqueSettings._customised(1, **kwargs)

    @staticmethod
    def customised_dictory(**kwargs):
        return UniqueSettings._customised(2, **kwargs)


class AC:
    Minutes_before_display_is_turn_off = {"index": 1, "radio": (-10, 0), "text": (75, 0)}
    Minutes_before_system_sleep = {"index": 2, "radio": (-6, -1), "text": (75, 0)}
    Power_button_action = {"index": 3, "selected": (75, 0)}
    CPU_mode = {"index": 4, "selected": (75, 0)}
    Laptop_lid_action_Mtc_only = {"index": 99, "selected": (75, 0)}

    class Select:
        nothing = 1
        sleep = 2
        shutdown = 3
        ondemand = 2
        performance = 1


class Battery:

    class Normal:
        Minutes_before_display_is_turn_off = {"index": 1, "radio": (-10, 0), "text": (75, 0)}
        Minutes_before_system_sleep = {"index": 2, "radio": (-6, -1), "text": (75, 0)}
        Power_button_action = {"index": 3, "selected": (75, 0)}
        CPU_mode = {"index": 4, "selected": (75, 0)}
        Laptop_lid_action_Mtc_only = {"index": 99, "selected": (75, 0)}

    class Low:
        Minutes_before_display_is_turn_off = {"index": 1, "radio": (-10, 0), "text": (50, 0)}
        Minutes_before_system_sleep = {"index": 2, "radio": (-6, -1), "text": (50, 0)}
        CPU_mode = {"index": 3, "selected": (50, 0)}
        Low_battery_level = {"index": 4, "text": (50, 0)}

    class Critical:
        Critial_battery_level = {"index": 1, "text": (75, 0)}
        Critial_battery_action = {"index": 2, "selected": (75, 0)}

    class Select:
        nothing = 1
        sleep = 2
        shutdown = 3
        ondemand = 2
        performance = 1


class ScreenSaver:
    Enable_Timed_System_Lock = {"index": 1, "radio": (-10, 0)}
    Enable_Screensaver_and_Screen_Lock = {"index": 2, "radio": (-10, 0)}
    Minutes_before_automatic_Screensaver_activation = {"index": 3, "radio": (-10, 0), "text": (25, 0)}
    Require_password_in_Administrator_Mode = {"index": 4, "radio": (-10, 0)}
    Require_password_for_domain_users = {"index": 5, "radio": (-10, 0)}
    Require_password_for_general_users = {"index": 6, "radio": (-10, 0)}
    Standard_image = {"index": 7, "radio": (-10, 0), "selected": (75, 0)}
    Custom_image = {"index": 8, "radio": (-10, 0), "selected": (25, 0)}
    Solid_color = {"index": 9, "radio": (-10, 0), "selected": (35, 0)}
    Image_Mapping = {"index": 10, "selected": (120, 0)}
    Require_password_for_active_remote_session = {"index": 99, "radio": (-10, 0)}

    class Select:
        Default = 1
        SlideShow = 2
        SlideShowStretch = 3
        Center = 4
        Expand = 5
        Stretch = 6
        Title = 7
        System_images = UniqueSettings.system_image
        Customized_dictory = UniqueSettings.customised_dictory


class PowerMenu:
    Show_power_menu_system_wide_for_regular_users = {"index": 1, "radio": (-8, -2)}
    Show_Logout = {"index": 2, "radio": (-10, 0)}
    Show_Poweroff = {"index": 3, "radio": (-10, 0)}
    Show_Reboot = {"index": 4, "radio": (-10, 0)}
    Show_Sleep = {"index": 5, "radio": (-10, 0)}