from Common.tool import *
from Common import picture_operator
from Common.common_function import *
from Test_Script.ts_precheck.precheck_function import SwitchThinProMode


def check_powerpic():
    path = get_root_path("Test_Data/td_precheck/Thinpro7.1/{}".format("estar_logo.png"))
    press_keys([keyboard.control_l_key, keyboard.alt_l_key, 's'])
    type_string('power')
    press_key(keyboard.down_key)
    press_key(keyboard.enter_key)
    estart_position = picture_operator.wait_element(path)
    return estart_position


def start(case_name, **kwargs):
    SwitchThinProMode(switch_to='admin')
    name = check_powerpic.__name__
    # ip = get_ip()
    ip = check_ip_yaml()
    pathyml = get_root_path("Test_Report/{}.yaml".format(ip))
    new_cases_result(pathyml, case_name)
    estart_position = check_powerpic()
    flag = False
    with os.popen('/usr/bin/hptc-hwsw-id --hw') as f:
        rs = f.read()

        if rs:
            rs = rs.lower()
            if 't630' in rs or 't730' in rs:
                with os.popen('ethtool eth0') as fl:
                    res = fl.read()
                    if res:
                        if 'fibre' in res.lower():
                            flag = True
                        else:
                            with os.popen("ifconfig") as fl2:
                                r = fl2.read()
                                r = r.lower() if r else r
                                if 'eth0' in r and 'eth1' in r.lower():
                                    flag = True

    if estart_position is not None and flag == False:
        steps = {'step_name': name,
                 'result': 'PASS',
                 'expect': '',  # can be string or pic path
                 'actual': '',  # can be string or pic path
                 'note': ''}
        print("success")
    elif estart_position is None and flag == True:
        steps = {'step_name': name,
                 'result': 'PASS',
                 'expect': 'no estarlogo',  # can be string or pic path
                 'actual': 'no estarlogo',  # can be string or pic path
                 'note': 'no estarlogo beacuse of tp with fibre'}
        print("success")
    else:
        path = get_root_path("Test_Report/img")
        if not os.path.exists(path):
            os.mkdir(path)
        picture_operator.capture_screen(get_root_path("Test_Report/img/{}.jpg".format(name)))
        steps = {'step_name': name,
                 'result': 'Fail',
                 'expect': '',  # can be string or pic path
                 'actual': 'img/{}.jpg'.format(name),  # can be string or pic path
                 'note': ''}
        print("fail")
    update_cases_result(pathyml, case_name, steps)
    try:
        pathclose = get_root_path("Test_Data/td_precheck/Thinpro7.1/{}".format("power_close.png"))
        rs = picture_operator.wait_element(pathclose, 1, (3, 3))[0]
        click(*rs)
    except AssertionError as e:
        print(e)
    except Exception as f:
        print(f)


if __name__ == "__main__":
    start()
