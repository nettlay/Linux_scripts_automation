#  ThinPro power manager screensaver function
import subprocess
import yaml
import os
import time
import pyautogui
import traceback
from Common import common_function as cf
from Common.log import Logger
from Common.picture_operator import wait_element


class ScreenSaver:

    def __init__(self):
        self.log = Logger()

    @staticmethod
    def pic(picture):
        return os.path.join(cf.get_current_dir(), "Test_Data", "td_power_manager", "ScreenSaver", "{}".format(picture))

    @staticmethod
    def lock_screen_by_command():
        os.system("hptc-lockscreen")
        time.sleep(1)

    def lock_screen_by_right_click(self):
        lock_screen_pic = self.pic("_lock_screen")
        try:
            pyautogui.rightClick(1, 1)
            time.sleep(1)
            rs = wait_element(lock_screen_pic)
            if rs:
                pyautogui.move(rs[0])
                time.sleep(0.2)
                pyautogui.click()
            else:
                self.log.error("not found the 'Lock Screen' in right click menu")
                return False
        except Exception as e:
            print(e)

    @staticmethod
    def lock_screen_by_hotkey():
        pyautogui.hotkey("ctrl", "alt", "l")

    @staticmethod
    def __registry():
        config = os.path.join(cf.get_current_dir(), 'Test_Data', 'td_common', 'thinpro_registry.yml')
        with open(config, 'r') as f:
            return yaml.safe_load(f)

    def check_default_set(self):
        registry = self.__registry()
        default = registry["get"]["screensaver"]["default_set"]
        for key, value in default.items():
            k = subprocess.getoutput("mclient --quiet get {}".format(key))
            if k.upper() == str(value).upper():
                self.log.info("'{}' value is '{}'".format(key, value))
            else:
                self.log.error("'{}' value not is '{}'".format(key, value))
                return False

    def set_default_setting(self):
        registry = self.__registry()
        default = registry["set"]["screensaver"]["default_set"]
        for key, value in default.items():
            try:
                os.system("mclient --quiet set {} {}".format(key, value))
                os.system("mclient commit")
            except:
                self.log.error(traceback.format_exc())
                return False

    def __login_from_screen_lock(self, **kwargs):
        admin = os.path.exists('/var/run/hptc-admin')
        require_user_mode = subprocess.getoutput("mclient --quiet get root/screensaver/lockScreenUser")
        require_domain_user = subprocess.getoutput("mclient --quiet get root/screensaver/lockScreenDomain")
        require_admin_mode = subprocess.getoutput("mclient --quiet get root/screensaver/lockScreen")
        require_remote_session = subprocess.getoutput("mclient --quiet get root/screensaver/lockScreenSession")
        if admin:                                              # admin mode
            if require_admin_mode == '1':
                admin_pw = kwargs.get("admin_password", "1")
                if wait_element(cf.get_current_dir("Test_Data/td_power_manager/ScreenSaver/_root_lock_screen"), rate=0.98):
                    pyautogui.typewrite(admin_pw)
                    time.sleep(1)
                    pyautogui.press("enter")
                elif wait_element(cf.get_current_dir("Test_Data/td_power_manager/ScreenSaver/_domain_lock_screen"), rate=0.98):  # in domain
                    pyautogui.typewrite("root")
                    time.sleep(1)
                    pyautogui.press("tab")
                    time.sleep(1)
                    pyautogui.typewrite(admin_pw)
                    time.sleep(1)
                    pyautogui.press("enter")
            else:
                pass
        else:                                                    # user mode
            if wait_element(cf.get_current_dir("Test_Data/td_power_manager/ScreenSaver/_root_lock_screen"), rate=0.98):  # not in domain
                if require_user_mode == '1':
                    user_pw = kwargs.get("user_password", "1")
                    pyautogui.typewrite("user")
                    time.sleep(1)
                    pyautogui.press("tab")
                    time.sleep(1)
                    pyautogui.typewrite(user_pw)
                    time.sleep(1)
                    pyautogui.press("enter")
                else:
                    pass
            elif wait_element(cf.get_current_dir("Test_Data/td_power_manager/ScreenSaver/_domain_lock_screen"),
                                  rate=0.98):                                                              # in domain
                if require_user_mode == "1":
                    pyautogui.press("tab", interval=4)
                    pyautogui.typewrite("root")
                    time.sleep(1)
                    pyautogui.press("tab")
                    time.sleep(1)
                    pyautogui.typewrite("1")
                    time.sleep(1)
                    pyautogui.press("enter")
                elif require_domain_user == "1":
                    user_sh_pw = kwargs.get("user_sh_password", "Shanghai2010")
                    pyautogui.typewrite(user_sh_pw)
                    time.sleep(1)
                    pyautogui.press("enter")
                elif require_remote_session == 1:
                    vdi_pw = kwargs.get("vdi_password", "Shanghai2010")
                    pyautogui.typewrite(vdi_pw)
                    time.sleep(1)
                    pyautogui.press("enter")

    def resume_screensaver_by_keyboard(self, **kwargs):
        pyautogui.press("enter")
        time.sleep(1)
        self.__login_from_screen_lock(**kwargs)

    def resume_screensaver_by_mouse(self, **kwargs):
        pyautogui.click()
        time.sleep(1)
        self.__login_from_screen_lock(**kwargs)

    def reboot_by_screen_lock(self):
        pyautogui.press("enter")
        time.sleep(1)
        tool_pic_rs = wait_element(self.pic("_tool"))
        if tool_pic_rs:
            pyautogui.click(tool_pic_rs[0])
        power_rs = wait_element(self.pic("_power"))
        if not power_rs:
            self.log.error("not found power button")
            return False
        pyautogui.click(power_rs[0])
        reboot_rs = wait_element(self.pic("_reboot"))
        if not reboot_rs:
            self.log.error("not found reboot button")
            return False
        pyautogui.click(reboot_rs[0])
        self.log.info("start reboot")

    def power_off_by_screen_lock(self):
        pyautogui.press("enter")
        time.sleep(1)
        tool_pic_rs = wait_element(self.pic("_tool"))
        if tool_pic_rs:
            pyautogui.click(tool_pic_rs[0])
        power_rs = wait_element(self.pic("_power"))
        if not power_rs:
            self.log.error("not found power button")
            return False
        pyautogui.click(power_rs[0])
        reboot_rs = wait_element(self.pic("_power_off"))
        if not reboot_rs:
            self.log.error("not found power_off button")
            return False
        pyautogui.click(reboot_rs[0])
        self.log.info("start power off")

    @staticmethod
    def resume_lock_screen_by_mouse():
        path = cf.get_current_dir("Test_Data/td_power_manager/password_frame/double")
        pyautogui.click()
        time.sleep(1)
        res = wait_element(path)
        if res:
            pyautogui.typewrite("root")
            time.sleep(1)
            pyautogui.press("tab")
            time.sleep(1)
        pyautogui.typewrite("1")
        time.sleep(1)
        pyautogui.press("enter")
        return True



if __name__ == '__main__':
    ss = ScreenSaver()
    ss.check_default_set()


