from Test_Script.ts_power_manager.power_manager_base import *
from Test_Script.ts_power_manager import power_manager_settings


class AC(PowerManager):
    def __init__(self):
        super().__init__()


class Battery(PowerManager):

    def __init__(self):
        super().__init__()

    def switch(self, case="Normal"):
        self.file_path = self.file_path.split("Battery")[0] + "Battery/"
        current_switch = PowerManager.common.get("switch", "")
        if current_switch.upper() != "BATTERY":
            super().switch()
        if case.upper() == "NORMAL":
            self.file_path = self.file_path + "1/"
        elif case.upper() == "LOW":
            self.file_path = self.file_path + "2/"
        elif case.upper() == "CRITICAL":
            self.file_path = self.file_path + "3/"
        print(PowerManager.common, "switch")
        print(self.file_path)
        return super().switch()


class ScreenSaver(PowerManager):

    def __init__(self):
        super().__init__()

    def set(self, pms, *args, **kwargs):
        print(kwargs)
        print(PowerManager.select)
        print(PowerManager.common)
        status = PowerManager.common.get("Enable_Screensaver_and_Screen_Lock", "off")
        print(status, "set in screen")
        if pms.get("index") > 2 and status == "off":
            print(self.Warning.format("Enable_Screensaver_and_Screen_Lock is off! try to open it"))
            super().set(power_manager_settings.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
        return super().set(pms, *args, **kwargs)

    @check_radio()
    def _set_radio(self, pms, *args, **kwargs):
        if pms.get("index") == 2:
            PowerManager.common["Enable_Screensaver_and_Screen_Lock"] = kwargs.get("radio", "").lower()
        return super()._set_radio(pms, *args, **kwargs)


class PowerMenu(PowerManager):

    def __init__(self):
        super().__init__()

    def set(self, pms, *args, **kwargs):
        status = PowerManager.common.get("Show_power_menu_system_wide_for_regular_users", "off")
        print(status, "set in screen")
        if pms.get("index") > 1 and status == "off":
            print(self.Warning.format("Show_power_menu_system_wide_for_regular_users is off! try to open it"))
            super().set(power_manager_settings.PowerMenu.Show_power_menu_system_wide_for_regular_users, radio="on")
        return super().set(pms, *args, **kwargs)

    @check_radio()
    def _set_radio(self, pms, *args, **kwargs):
        if pms.get("index") == 1:
            PowerManager.common["Show_power_menu_system_wide_for_regular_users"] = kwargs.get("radio", "").lower()
        return super()._set_radio(pms, *args, **kwargs)





if __name__ == '__main__':
    print(ScreenSaver.__dict__)