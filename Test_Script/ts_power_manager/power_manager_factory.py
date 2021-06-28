from Test_Script.ts_power_manager.power_manager import *
from Common.log import Logger


class PowerManagerFactory:
    """
    power_manager = PowerManagerFactory.generate_mtc()
    power_manager = PowerManagerFactory("AC", "Battery", name = Class_Name())
    power_manager = PowerManagerFactory("DTC")
    """
    AC = None
    Battery = None
    ScreenSaver = None
    PowerMenu = None
    log = None

    def __init__(self, *args, **kwargs):
        self.generate(args)
        self.generates(kwargs.items())

    @classmethod
    def generate_mtc(cls):
        parts = ["AC", "Battery", "ScreenSaver", "PowerMenu", "LOG"]
        return cls(*parts)

    @classmethod
    def generate_dtc(cls):
        parts = ["AC", "ScreenSaver", "PowerMenu", "LOG"]
        return cls(*parts)

    def generate(self, parts):
        if parts:
            part, *args = parts
            part = part.upper()
            if part == "AC":
                self.AC = AC()
            elif part == "BATTERY":
                self.Battery = Battery()
            elif part == "SCREENSAVER":
                self.ScreenSaver = ScreenSaver()
            elif part == "POWERMENU":
                self.PowerMenu = PowerMenu()
            elif part == "MTC":
                self.AC = AC()
                self.Battery = Battery()
                self.ScreenSaver = ScreenSaver()
                self.PowerMenu = PowerMenu()
            elif part == "DTC":
                self.AC = AC()
                self.ScreenSaver = ScreenSaver()
                self.PowerMenu = PowerMenu()
            if part == "LOG":
                self.log = Logger()
            return self.generate(args)
        return

    def generates(self, kw_items):
        if kw_items:
            item, *args = kw_items
            k, v = item
            setattr(self, k, v)
            return self.generates(args)
        return

    @classmethod
    def apply(cls):
        return PowerManager.apply()

    @staticmethod
    def open_power_manager():
        return PowerManager.open_power_manager()

    @staticmethod
    def open_power_manager_from_tray():
        return PowerManager.open_power_manager_from_tray()

    @staticmethod
    def open_power_manager_from_control_panel():
        return PowerManager.open_power_manager_from_control_panel()

    @staticmethod
    def close_all_power_manager():
        return PowerManager.close_all_power_manager()

if __name__ == '__main__':
    # copy to test
    # from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
    # from Test_Script.ts_power_manager import power_manager_settings as pms
    #
    # power_manager = PowerManagerFactory("AC", "Battery", "ScreenSaver", "PowerMenu", "LOG")#PowerManagerFactory.generate_dtc()
    # power_manager.open_power_manager()
    # power_manager.AC.switch()
    # power_manager.AC.set_brightness_mtc_only("33")
    # power_manager.AC.set(pms=pms.AC.Minutes_before_display_is_turn_off, text="12")
    # power_manager.AC.set(pms=pms.AC.Minutes_before_system_sleep, radio="on", text="18")
    # power_manager.AC.set(pms=pms.AC.Power_button_action, selected=pms.AC.Select.nothing)
    # power_manager.AC.set(pms=pms.AC.Laptop_lid_action_Mtc_only, selected=pms.AC.Select.nothing)
    # power_manager.AC.set(pms=pms.AC.CPU_mode, selected=pms.AC.Select.ondemand)
    # power_manager.PowerMenu.switch()
    # power_manager.PowerMenu.set(pms=pms.PowerMenu.Show_power_menu_system_wide_for_regular_users, radio="off")
    # power_manager.PowerMenu.set(pms=pms.PowerMenu.Show_Sleep, radio="off")
    # power_manager.PowerMenu.set(pms=pms.PowerMenu.Show_Logout, radio="off")
    # power_manager.PowerMenu.set(pms=pms.PowerMenu.Show_Poweroff, radio="off")
    # power_manager.PowerMenu.set(pms=pms.PowerMenu.Show_Reboot, radio="off")
    # power_manager.ScreenSaver.switch()
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Timed_System_Lock, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Minutes_before_automatic_Screensaver_activation, radio="on",
    #                               text="15")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_domain_users, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_for_general_users, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Require_password_in_Administrator_Mode, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Standard_image, radio="on")
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Image_Mapping, selected=pms.ScreenSaver.Select.SlideShowStretch)
    # power_manager.ScreenSaver.set(pms=pms.ScreenSaver.Custom_image, selected=pms.ScreenSaver.Select.Customized_dictory)
    #
    #
    # power_manager.Battery.switch("Low")
    # power_manager.AC.set_brightness_mtc_only("34")
    # power_manager.Battery.set(pms.Battery.Low.CPU_mode, selected=pms.Battery.Select.performance)
    # power_manager.Battery.set(pms.Battery.Low.Minutes_before_display_is_turn_off, text="12")
    # power_manager.Battery.set(pms.Battery.Low.Minutes_before_system_sleep, radio="on", text="12")
    # power_manager.Battery.set(pms.Battery.Low.Low_battery_level,  text="12")
    # power_manager.Battery.switch("Normal")
    # power_manager.Battery.set(pms.Battery.Normal.CPU_mode, selected=pms.Battery.Select.ondemand)
    # power_manager.Battery.set(pms.Battery.Normal.Minutes_before_system_sleep, text="12")
    # power_manager.Battery.set(pms.Battery.Normal.Minutes_before_display_is_turn_off, text="12")
    # power_manager.Battery.set(pms.Battery.Normal.Power_button_action, selected=pms.Battery.Select.sleep)
    # power_manager.Battery.set(pms.Battery.Normal.Laptop_lid_action_Mtc_only, selected=pms.Battery.Select.nothing)
    # power_manager.Battery.switch("Critical")
    # power_manager.Battery.set(pms.Battery.Critical.Critial_battery_action, selected=pms.Battery.Select.nothing)
    # power_manager.Battery.set(pms.Battery.Critical.Critial_battery_level, text="23")
    # power_manager.apply()
    pass

