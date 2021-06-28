from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
import os
from Common.common_function import get_folder_items,get_current_dir
import Common.tool
from Common.common_function import get_position


class ACCheck():
    def __init__(self):
        self.folder=os.path.join(get_current_dir(),'Test_Data', 'td_power_manager', 'PowerManager','Check','AC')

    def look(self,sub_folder):
        full_folder = os.path.join(self.folder, sub_folder)
        file_list=get_folder_items(full_folder)
        for file in file_list:
            tag = file.split(".")[0].split("_")[-1]
            res = get_position(file, base_dir=full_folder,similaity=0.99)
            if res and tag=="checked":
                print("checked")
                return True
            elif res and tag=="unchecked":
                print('unchecked')
                return False

    @property
    def minutes_display_checked(self):
        return self.look('minutes_display')

    @property
    def minutes_sleep_checked(self):
        return self.look('minutes_sleep')

    def check_power_action_type(self,parent_region,offset_w_h,):
        power_actions=os.path.join(self.folder, 'power_actions')
        file_list = get_folder_items(power_actions)
        new_region=(parent_region[0],parent_region[1],parent_region[2]+offset_w_h[0],parent_region[3]+offset_w_h[1])
        for file in file_list:
            tag = file.split(".")[0].split("_")[-1]
            res = get_position(file, base_dir=power_actions, similaity=0.99,region=new_region)
            if res and tag=="nothing":
                print("nothing")
                return "nothing"
            elif res and tag=="shutdown":
                print('shutdown')
                return 'shutdown'
            elif res and tag=="sleep":
                print('sleep')
                return 'sleep'

    @property
    def power_button_status(self):
        power_button = os.path.join(self.folder, 'power_button')
        file_list=get_folder_items(power_button)
        for file in file_list:
            tag = file.split(".")[0].split("_")[-1]
            res = get_position(file, base_dir=power_button,similaity=0.99)
            if res:
                return self.check_power_action_type(res[0],(200,0))

    @property
    def cpu_mode_status(self):
        cpu_mode = os.path.join(self.folder, 'cpu_mode')
        file_list=get_folder_items(cpu_mode)
        for file in file_list:
            tag = file.split(".")[0].split("_")[-1]
            res = get_position(file, base_dir=cpu_mode,similaity=0.99)
            if res and tag=="ondemand":
                print("ondemand")
                return "ondemand"
            elif res and tag=="performance":
                print('performance')
                return 'performance'

    @property
    def lib_action_status(self):
        lib_action = os.path.join(self.folder, 'lib_action')
        file_list=get_folder_items(lib_action)
        for file in file_list:
            tag = file.split(".")[0].split("_")[-1]
            res = get_position(file, base_dir=lib_action,similaity=0.99)
            if res:
                return self.check_power_action_type(res[0], (200, 0))


class BatteryCheck(ACCheck):
    def __init__(self):
        super().__init__()
        self.folder=os.path.join(get_current_dir(),'Test_Data', 'td_power_manager', 'PowerManager','Check','Battery')

    @property
    def mode_status(self):
        mode = os.path.join(self.folder, 'mode')
        file_list=get_folder_items(mode)
        for file in file_list:
            tag = file.split(".")[0].split("_")[-1]
            res = get_position(file, base_dir=mode,similaity=0.99)
            if res and tag=="normal":
                print("normal")
                return "normal"
            elif res and tag=="low":
                print('low')
                return 'low'
            elif res and tag=="critical":
                print('critical')
                return 'critical'

    @property
    def critical_action_status(self):
        critical_action = os.path.join(self.folder, 'critical_action')
        file_list=get_folder_items(critical_action)
        for file in file_list:
            tag = file.split(".")[0].split("_")[-1]
            res = get_position(file, base_dir=critical_action,similaity=0.99)
            if res and tag=="nothing":
                print("nothing")
                return "nothing"
            elif res and tag=="shutdown":
                print('shutdown')
                return 'shutdown'
            elif res and tag=="sleep":
                print('sleep')
                return 'sleep'


class ScreenSaverCheck():
    def __init__(self):
        self.folder=os.path.join(get_current_dir(),'Test_Data', 'td_power_manager', 'PowerManager','Check','ScreenSaver')

    def look(self,sub_folder):
        full_folder = os.path.join(self.folder, sub_folder)
        file_list=get_folder_items(full_folder)
        for file in file_list:
            tag = file.split(".")[0].split("_")[-1]
            res = get_position(file, base_dir=full_folder,similaity=0.99)
            if res and tag=="checked":
                print("checked")
                return True
            elif res and tag=="unchecked":
                print('unchecked')
                return False

    @property
    def enable_TSL_checked(self):
        return self.look('enable_TSL')


    @property
    def enable_SS_checked(self):
        return self.look('enable_SS')


    @property
    def minutes_before_asa_checked(self):
        return self.look('minutes_before_asa')

    @property
    def require_pwd_admin_checked(self):
        return self.look('require_pwd_admin')


    @property
    def require_pwd_domain_checked(self):
        return self.look('require_pwd_domain')


    @property
    def require_pwd_user_checked(self):
        return self.look('require_pwd_user')


    @property
    def standard_image_checked(self):
        return self.look('standard_image')


    @property
    def custom_image_checked(self):
        return self.look('custom_image')

    @property
    def solid_color_checked(self):
        return self.look('solid_color')


class PowerMenuCheck():
    def __init__(self):
        self.folder=os.path.join(get_current_dir(),'Test_Data', 'td_power_manager', 'PowerManager','Check','PowerMenu')

    def look(self,sub_folder):
        full_folder = os.path.join(self.folder, sub_folder)
        file_list=get_folder_items(full_folder)
        for file in file_list:
            tag = file.split(".")[0].split("_")[-1]
            res = get_position(file, base_dir=full_folder,similaity=0.99)
            if res and tag=="checked":
                print("checked")
                return True
            elif res and tag=="unchecked":
                print('unchecked')
                return False

    @property
    def show_PM_checked(self):
        return self.look('show_PM')

    @property
    def show_logout_checked(self):
        return self.look('show_logout')


    @property
    def show_poweroff_checked(self):
        return self.look('show_poweroff')

    @property
    def show_sleep_checked(self):
        return self.look('show_sleep')

    @property
    def show_reboot_checked(self):
        return self.look('show_reboot')


def test():
    power_manager = PowerManagerFactory("AC", "Battery", "ScreenSaver", "PowerMenu", "LOG")#PowerManagerFactory.generate_dtc()
    power_manager.open_power_manager()
    # """
    # AC
    # """
    # power_manager.AC.switch()
    # accheck=ACCheck()
    # print('minutes_display_checked',accheck.minutes_display_checked)
    # print("minutes_sleep_checked", accheck.minutes_sleep_checked)
    # print('power_button_status', accheck.power_button_status)
    # print('lib_action_status',accheck.lib_action_status)
    # print('cpu_mode_status', accheck.cpu_mode_status)
    """
    BAT ,only for MTC
    """
    power_manager.Battery.switch("Normal")
    batcheck=BatteryCheck()
    print('BAT mode check',batcheck.mode_status)
    print('BAT Normal minutes_display_checked', batcheck.minutes_display_checked)
    print("BAT Normal minutes_sleep_checked", batcheck.minutes_sleep_checked)
    print('BAT Normal power_button_status', batcheck.power_button_status)
    print('BAT Normal lib_action_status', batcheck.lib_action_status)
    print('BAT Normal cpu_mode_status', batcheck.cpu_mode_status)
    power_manager.Battery.switch("Low")
    print('BAT mode check', batcheck.mode_status)
    print('BAT low minutes_display_checked', batcheck.minutes_display_checked)
    print("BAT low minutes_sleep_checked", batcheck.minutes_sleep_checked)
    print('BAT low cpu_mode_status', batcheck.cpu_mode_status)
    power_manager.Battery.switch("Critical")
    print('BAT mode check', batcheck.mode_status)
    print("BAT critical action",batcheck.critical_action_status)
    # """
    # PM
    # """
    # power_manager.PowerMenu.switch()
    # powermenucheck=PowerMenuCheck()
    # print("PM show_PM_checked",powermenucheck.show_PM_checked)
    # print("PM show_logout_checked", powermenucheck.show_logout_checked)
    # print("PM show_poweroff_checked", powermenucheck.show_poweroff_checked)
    # print("PM show_reboot_checked", powermenucheck.show_reboot_checked)
    # print("PM show_sleep_checked", powermenucheck.show_sleep_checked)

    # """
    # SC
    # """
    # power_manager.ScreenSaver.switch()
    # sc=ScreenSaverCheck()
    # print("SC enable_TSL_checked", sc.enable_TSL_checked)
    # print("SC enable_SS_checked", sc.enable_SS_checked)
    # print("SC minutes_before_asa_checked", sc.minutes_before_asa_checked)
    # print("SC require_pwd_admin_checked ", sc.require_pwd_admin_checked)
    # print("SC require_pwd_domain_checked", sc.require_pwd_domain_checked)
    # print("SC require_pwd_user_checked", sc.require_pwd_user_checked)
    # print("SC standard_image_checked", sc.standard_image_checked)
    # print("SC custom_image_checked ", sc.custom_image_checked)
    # print("SC solid_color_checked", sc.solid_color_checked)

    # power_manager.apply()