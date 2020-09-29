import os
import pyautogui
import time
import yaml
from Common.log import Logger
from Common.common_function import get_position, open_window, close_window, \
    reboot, get_current_dir, now, add_linux_script_startup, linux_rm_startup_script
from Test_Script.ts_power_manager.common_function import SwitchThinProMode


def add_domain(status_code, user_name, password, domain_name):
    if status_code == 0:
        Logger().info("setting nothing")
        return
    elif status_code != 1 and status_code != 2:
        Logger().info("invalid status code")
        return
    SwitchThinProMode(switch_to='admin')
    open_window("active directory")
    ad = get_position('ad.png')
    if not ad:
        Logger().info("find ad fail")
        return
    domain = get_position('domain_name.png')
    if not domain:
        Logger().info("find domain fail")
        return
    domain_txt_pos = (domain[1][0] + 200, domain[1][1])
    pyautogui.click(domain_txt_pos)
    for i in range(20):
        pyautogui.hotkey('backspace')
        time.sleep(0.5)
    pyautogui.typewrite(domain_name)
    authenticate = get_position('authenticate.png')
    if not authenticate:
        Logger().info("find authenticate fail")
        return
    pyautogui.click(authenticate[1])
    apply = get_position('apply.png')
    if not apply:
        Logger().info("find apply fail")
        return

    if status_code == 1:
        pyautogui.click(apply[1])

        while True:
            enter = get_position('enter_authenticate.png')
            if enter:
                Logger().info("entering domain")
            else:
                break
            time.sleep(1)

        apply_checked = get_position('apply_checked.png')
        if not apply_checked:
            Logger().info("find apply_checked fail")
            close_window()
            return
        else:
            Logger().info("apply_checked pass")
            close_window()
            return True

    elif status_code == 2:
        join_authenticate = get_position('join_authenticate.png')
        if not join_authenticate:
            Logger().info("find join_authenticate fail")
            return
        pyautogui.click(join_authenticate[1])
        pyautogui.click(apply[1])
        dialog = get_position('dialog.png')
        if not dialog:
            Logger().info("find dialog fail")
            return
        user = get_position('user.png')
        if not user:
            Logger().info("find user fail")
            return

        pwd = get_position('pwd.png')
        if not user:
            Logger().info("find pwd fail")
            return
        pyautogui.click(user[1])
        pyautogui.typewrite(user_name)
        pyautogui.click(pwd[1])
        pyautogui.typewrite(password)
        ok = get_position('ok.png')
        if not user:
            Logger().info("find ok fail")
            return
        pyautogui.click(ok[1])
        while True:
            enter = get_position('enter.png')
            if enter:
                Logger().info("entering domain")
            else:
                break
            time.sleep(1)

        apply_checked = get_position('apply_checked.png')
        if not apply_checked:
            Logger().info("find apply_checked fail")
            close_window()
            return
        else:
            Logger().info("apply_checked pass")
            close_window()
            return True


def leave_domain(status_code, user_name, password):
    if status_code == 0:
        return True
    SwitchThinProMode(switch_to='admin')
    open_window("active directory")
    ad = get_position('ad.png')
    if not ad:
        Logger().info("find ad fail")
        return
    authenticate_checked = get_position('authenticate_checked.png')
    if not authenticate_checked:
        Logger().info("find authenticate fail")
        return
    pyautogui.click(authenticate_checked[1])
    apply = get_position('apply.png')
    if not apply:
        Logger().info("find apply fail")
        return
    pyautogui.click(apply[1])
    if status_code == 1:
        reboot_dialog = get_position('reboot_dialog.png')
        if reboot_dialog:
            pyautogui.hotkey("enter")
            time.sleep(1)
            pyautogui.hotkey("enter")
            Logger().info("reboot to exit dialog")
            remove_flag()
            return
        apply_checked = get_position('apply_checked.png')
        if not apply_checked:
            Logger().info("find apply_checked fail")
            close_window()
            return
        else:
            Logger().info("apply_checked pass")
            close_window()
            return True

    elif status_code == 2:
        reboot_dialog = get_position('reboot_dialog.png')
        if reboot_dialog:
            pyautogui.hotkey("enter")
            Logger().info("reboot to exit dialog")

            dialog = get_position('dialog.png')
            if not dialog:
                Logger().info("find dialog fail")
                return
            user = get_position('user.png')
            if not user:
                Logger().info("find user fail")
                return

            pwd = get_position('pwd.png')
            if not user:
                Logger().info("find pwd fail")
                return
            pyautogui.click(user[1])
            pyautogui.typewrite(user_name)
            pyautogui.click(pwd[1])
            pyautogui.typewrite(password)
            ok = get_position('ok.png')
            if not user:
                Logger().info("find ok fail")
                close_window()
                return
            pyautogui.click(ok[1])

            while True:
                leave = get_position('leave.png')
                if leave:
                    Logger().info("leaving domain")
                else:
                    break
                time.sleep(1)
            pyautogui.hotkey("enter")
            return True
        else:
            dialog = get_position('dialog.png')
            if not dialog:
                Logger().info("find dialog fail")
                return
            user = get_position('user.png')
            if not user:
                Logger().info("find user fail")
                return

            pwd = get_position('pwd.png')
            if not user:
                Logger().info("find pwd fail")
                return
            pyautogui.click(user[1])
            pyautogui.typewrite(user_name)
            pyautogui.click(pwd[1])
            pyautogui.typewrite(password)
            ok = get_position('ok.png')
            if not user:
                Logger().info("find ok fail")
                close_window()
                return
            pyautogui.click(ok[1])

            while True:
                leave = get_position('leave.png')
                if leave:
                    Logger().info("leaving domain")
                else:
                    break
                time.sleep(1)
            pyautogui.hotkey("enter")

            apply_checked = get_position('apply_checked.png')
            if not apply_checked:
                Logger().info("find apply_checked fail")
                close_window()
                return
            else:
                Logger().info("apply_checked pass")
                remove_flag()
                close_window()
                return True


def check_status():
    """
    0 >> no setting
    1 >> domain_1
    2 >> domain_2
    :return:
    """
    SwitchThinProMode(switch_to='admin')
    time.sleep(20)
    open_window("active directory")
    ad = get_position('ad.png')
    if not ad:
        Logger().info("find ad fail")
        return
    authenticate = get_position('authenticate.png')
    if authenticate:
        close_window()
        return 0
    authenticate_checked = get_position('authenticate_checked.png')
    if authenticate_checked:
        join_authenticate = get_position('join_authenticate.png')
        if join_authenticate:
            close_window()
            return 1
        join_authenticate_checked = get_position('join_authenticate_checked.png')
        if join_authenticate_checked:
            close_window()
            return 2

    close_window()


def add_domain_with_check(code, user_name='bamboo.pan', password="zxc123ZXC", domain_name='sh.dto'):
    """
    0 >> no domain
    1 >> join domain_1
    2 >> join domain_2
    :return:
    """
    current_status = check_status()
    print(current_status)
    if current_status is None:
        Logger().info("can not get correct status")
        return
    if current_status != 0:
        Logger().info("already in domain {}".format(code))
        return
        # res=leave_domain(current_status,user_name,password)
        # if not res:
        #     Logger().info("leave domain fail")
        #     return
    return add_domain(code, user_name, password, domain_name)


def capture_pic():
    p = os.path.join(get_current_dir(), "d", "temp_{}.png".format(now()))
    pyautogui.screenshot().save(p)
    pass


def update_flag(d):
    os.system("fsunlock")
    time.sleep(0.2)
    flag_file = "/root/flag.yml"
    with open(flag_file, 'w') as f:
        yaml.safe_dump(d, f)


def get_flag():
    os.system("fsunlock")
    time.sleep(0.2)
    flag_file = "/root/flag.yml"
    with open(flag_file, 'r') as f:
        return yaml.safe_load(f)


def domain_login(user_name='bamboo.pan', password="zxc123ZXC"):
    domain_login_user = get_position('domain_login_user.png')
    if not domain_login_user:
        Logger().info("find domain_login_user fail")
        return
    domain_login_pwd = get_position('domain_login_pwd.png')
    if not domain_login_pwd:
        Logger().info("find domain_login_pwd fail")
        return
    pyautogui.click(domain_login_user[1])
    pyautogui.typewrite(user_name)
    pyautogui.click(domain_login_pwd[1])
    pyautogui.typewrite(password)
    domain_login_button = get_position('domain_login_button.png')
    if not domain_login_button:
        Logger().info("find domain_login_button fail")
        return
    pyautogui.click(domain_login_button[1])
    steps = {
        "add_domain": True,
        "login_domain": True
    }
    update_flag(steps)
    Logger().info("login success")


def add_domain_mix(code):
    if not os.path.exists("/root/flag.yml"):
        add_res = add_domain_with_check(code)
        if add_res:
            steps = {
                "add_domain": True,
                "login_domain": False
            }
            update_flag(steps)
            add_auto_reboot()
            reboot()
        else:
            return
    else:
        Logger().info("flag exist")

    count = 60
    while count:
        if os.path.exists("/root/flag.yml"):
            flag = get_flag()
            if flag.get('add_domain'):
                if not flag.get("login_domain"):
                    domain_login()
                    break
                else:
                    Logger().info("already login as domain")
                    break
            else:
                Logger().info("not in domain")
        count = count - 1


def add_auto_reboot():
    add_linux_script_startup('/root/run.sh')


def remove_auto_reboot():
    linux_rm_startup_script('/root/run.sh')


def remove_flag():
    Logger().info("remove domain flag")
    if os.path.exists('/root/flag.yml'):
        os.remove('/root/flag.yml')
    remove_auto_reboot()
    # if os.path.exists('/root/auto_start_setup.sh'):
    #     os.remove('/root/auto_start_setup.sh')


def leave_domain_with_check():
    current_status = check_status()
    print(current_status)
    if current_status is None:
        Logger().info("can not get correct status")
        return
    if current_status == 0:
        return
    if current_status:
        res = leave_domain(current_status, user_name='bamboo.pan', password="zxc123ZXC")
        if res:
            Logger().info("leave domain {}".format(current_status))
            return
    else:
        Logger().info("not in domain {}".format(current_status))
