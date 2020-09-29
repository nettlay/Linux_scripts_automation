import os
import time
import traceback
from Test_Script.ts_power_manager.power_manager_factory import PowerManagerFactory
from Test_Script.ts_power_manager import power_manager_settings as pms
from Test_Script.ts_power_manager.screensaver import ScreenSaver
import pyautogui
from Common import common_function, log
from Common.common_function import new_cases_result, update_cases_result
from Test_Script.ts_power_manager.common_function import SwitchThinProMode
from Common.picture_operator import capture_screen, wait_element
from PIL import Image

log = log.Logger()


def set_image_slideshow(power_m):
    log.info('set the image type to slideshow')
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Image_Mapping, selected=pms.ScreenSaver.Select.SlideShow)
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Custom_image, selected=pms.ScreenSaver.Select.Customized_dictory)


def set_image_slideshowstretch(power_m):
    log.info('set the image type to slideshowstretch')
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Image_Mapping, selected=pms.ScreenSaver.Select.SlideShowStretch)
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Custom_image, selected=pms.ScreenSaver.Select.Customized_dictory)


def set_image_center(power_m, path):
    log.info('set the image type to center')
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Image_Mapping, selected=pms.ScreenSaver.Select.Center)
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Custom_image, selected=pms.ScreenSaver.Select.Customized_dictory,
                            pic_path=path)


def set_image_expand(power_m, path):
    log.info('set the image type to expand')
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Image_Mapping, selected=pms.ScreenSaver.Select.Expand)
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Custom_image, selected=pms.ScreenSaver.Select.Customized_dictory,
                            pic_path=path)


def set_image_stretch(power_m, path):
    log.info('set the image type to stretch')
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Image_Mapping, selected=pms.ScreenSaver.Select.Stretch)
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Custom_image, selected=pms.ScreenSaver.Select.Customized_dictory,
                            pic_path=path)


def set_image_tile(power_m, path):
    log.info('set the image type to title')
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Enable_Screensaver_and_Screen_Lock, radio="on")
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Image_Mapping, selected=pms.ScreenSaver.Select.Title)
    power_m.ScreenSaver.set(pms=pms.ScreenSaver.Custom_image, selected=pms.ScreenSaver.Select.Customized_dictory,
                            pic_path=path)


def lock_screen():
    log.info('lock the screen')
    pyautogui.hotkey('ctrl', 'alt', 'l')


def locked_wake_up():
    log.info('wake up tc')
    screen_saver = ScreenSaver()
    screen_saver.resume_lock_screen_by_mouse()


def pic_path(pic_name):
    path = os.path.join(common_function.get_current_dir(), 'Test_Data/td_power_manager/verify_screensaver_diff_image'
                                                           '/source_pic/{}'.format(pic_name))
    log.info('select the source picture:{}'.format(path))
    return path


def template_pic_path(p):
    path = os.path.join(common_function.get_current_dir(), 'Test_Data/td_power_manager/verify_screensaver_diff_image'
                                                           '/{}'.format(p))
    log.info('verify the template picture:{}'.format(path))
    return path


def get_defaule():
    enable = os.popen("mclient --quiet get root/screensaver/enableCustomLogo").read().strip()
    logo_path = os.popen("mclient --quiet get root/screensaver/logoPath").read().strip()
    image_map = os.popen("mclient --quiet get root/screensaver/mode").read().strip()
    return [enable, logo_path, image_map]


def reset_settings(lis):
    os.system("mclient --quiet set root/screensaver/enableCustomLogo {}".format(lis[0]))
    os.system("mclient --quiet set root/screensaver/logoPath {}".format(lis[1]))
    os.system("mclient --quiet set root/screensaver/mode {}".format(lis[2]))
    os.system("mclient commit")
    os.system("rm /home/user/Images/*.png")
    os.system("rm /home/user/Images/*.jpg")
    for i in ['2', '3', '5', '6']:
        pic = os.path.join(common_function.get_current_dir(), 'Test_Data/td_power_manager/verify_screensaver_diff_image',
                           '{}'.format(i))
        os.system("rm -r {}".format(pic))


def open_pic(path):
    img_src = Image.open(path)
    size = img_src.size
    print(size)
    return img_src, size


def get_xy(size, size1=()):
    x, y = size[0], size[1]
    if size1:
        X, Y = size1[0], size1[1]
        print([(X/2-x*(Y/y)/3/2-50, Y/3-50), (X/2+x*(Y/y)/3/2+50, Y/3-50),
                (X/2-x*(Y/y)/3/2-50, Y*2/3+50), (X/2+x*(Y/y)/3/2+50, Y*2/3+50)])
        return [(X/2-x*(Y/y)/3/2-50, Y/3-50), (X/2+x*(Y/y)/3/2+50, Y/3-50),
                (X/2-x*(Y/y)/3/2-50, Y*2/3+50), (X/2+x*(Y/y)/3/2+50, Y*2/3+50)]
    else:
        print([(x/3-50, y/3-50), (x*2/3+50, y/3-50),
                (x/3-50, y*2/3+50), (x*2/3+50, y*2/3+50)])
        return [(x/3-50, y/3-50), (x*2/3+50, y/3-50),
                (x/3-50, y*2/3+50), (x*2/3+50, y*2/3+50)]


def get_pic_color(img, lis):
    img_src = img.convert('RGBA')
    src_strlist = img_src.load()
    data1 = src_strlist[lis[0][0], lis[0][1]]
    data2 = src_strlist[lis[1][0], lis[1][1]]
    data3 = src_strlist[lis[2][0], lis[2][1]]
    data4 = src_strlist[lis[3][0], lis[3][1]]
    return [data1, data2, data3, data4]


def pic_cut(folder, name):
    pic = os.path.join(common_function.get_current_dir(), 'Test_Data/td_power_manager/verify_screensaver_diff_image',
                       '{}/{}.png'.format(folder, name))
    capture_screen(pic)
    return pic


def step1(power_m, size, size1):
    try:
        set_image_slideshow(power_m)
        power_m.ScreenSaver.apply()
        time.sleep(5)
        lock_screen()
        time.sleep(5)
        img21, size21 = open_pic(pic_cut('2', '1'))
        data21 = get_pic_color(img21, get_xy(size, size21))
        log.info(data21)
        time.sleep(25)
        img22, size22 = open_pic(pic_cut('2', '2'))
        data22 = get_pic_color(img22, get_xy(size1, size22))
        log.info(data22)
        locked_wake_up()
        time.sleep(5)
        return data21, data22
    except:
        log.warning(traceback.format_exc())
        power_m.close_all_power_manager()
        return None


def step2(power_m):
    try:
        set_image_slideshowstretch(power_m)
        power_m.ScreenSaver.apply()
        time.sleep(5)
        lock_screen()
        time.sleep(5)
        img21, size21 = open_pic(pic_cut('3', '1'))
        data21 = get_pic_color(img21, get_xy(size21))
        log.info(data21)
        time.sleep(25)
        img22, size22 = open_pic(pic_cut('3', '2'))
        data22 = get_pic_color(img22, get_xy(size22))
        log.info(data22)
        locked_wake_up()
        time.sleep(5)
        return data21, data22
    except:
        log.warning(traceback.format_exc())
        power_m.close_all_power_manager()
        return None


def step3(power_m, num):
    try:
        set_image_center(power_m, pic_path('pic.jpg'))
        power_m.ScreenSaver.apply()
        time.sleep(5)
        lock_screen()
        res = wait_element(template_pic_path(num))
        return res
    except:
        log.warning(traceback.format_exc())
        power_m.close_all_power_manager()
        return None


def step4(power_m, size):
    try:
        set_image_expand(power_m, pic_path('pic.jpg'))
        power_m.ScreenSaver.apply()
        time.sleep(5)
        lock_screen()
        time.sleep(5)
        img1, size1 = open_pic(pic_cut('5', '1'))
        data = get_pic_color(img1, get_xy(size, size1))
        log.info(data)
        locked_wake_up()
        time.sleep(5)
        return data
    except:
        log.warning(traceback.format_exc())
        power_m.close_all_power_manager()
        return None


def step5(power_m):
    try:
        set_image_stretch(power_m, pic_path('pic1.png'))
        power_m.ScreenSaver.apply()
        time.sleep(5)
        lock_screen()
        time.sleep(5)
        img1, size1 = open_pic(pic_cut('6', '1'))
        data1 = get_pic_color(img1, get_xy(size1))
        log.info(data1)
        locked_wake_up()
        time.sleep(5)
        log.info(data1)
        return data1
    except:
        log.warning(traceback.format_exc())
        power_m.close_all_power_manager()
        return None


def step6(power_m, num):
    try:
        set_image_tile(power_m, pic_path('pic1.png'))
        power_m.ScreenSaver.apply()
        time.sleep(5)
        lock_screen()
        res = wait_element(template_pic_path(num))
        time.sleep(2)
        return res
    except:
        log.warning(traceback.format_exc())
        power_m.close_all_power_manager()
        return None


def start(case_name, **kwargs):
    value_ls = get_defaule()
    try:
        log.info('Begin to start test {}'.format(case_name))
        result_file = os.path.join(common_function.get_current_dir(),
                                   r'Test_Report', '{}.yaml'.format(common_function.check_ip_yaml()))
        new_cases_result(result_file, case_name)
        SwitchThinProMode(switch_to='admin')
        source_pic1 = os.path.join(common_function.get_current_dir(),
                           'Test_Data/td_power_manager/verify_screensaver_diff_image',
                           'source_pic/pic.jpg')
        source_img1, source_size1 = open_pic(source_pic1)
        source_data1 = get_pic_color(source_img1, get_xy(source_size1))
        log.info('pic.jpg data {}'.format(source_data1))
        source_pic2 = os.path.join(common_function.get_current_dir(),
                           'Test_Data/td_power_manager/verify_screensaver_diff_image',
                           'source_pic/pic1.png')
        source_img2, source_size2 = open_pic(source_pic2)
        source_data2 = get_pic_color(source_img2, get_xy(source_size2))
        log.info('pic1.png data {}'.format(source_data2))
        power_m = PowerManagerFactory("ScreenSaver")
        if not power_m.open_power_manager_from_control_panel():
            log.info('try open power manager again')
            power_m.open_power_manager_from_control_panel()
        power_m.ScreenSaver.switch()
        data1, data2 = step1(power_m, source_size1, source_size2)
        if data1 == source_data1 and data2 == source_data2:
            steps = {
                'step_name': 'verify new slideshow',
                'result': 'Pass',
                'expect': 'slideshow',
                'actual': 'slideshow',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'verify new slideshow',
                'result': 'Fail',
                'expect': 'slideshow',
                'actual': 'no slideshow',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
            reset_settings(value_ls)
            return False
        data3, data4 = step2(power_m)
        if data3 == source_data1 and data4 == source_data2:
            steps = {
                'step_name': 'verify new slideshowstretch',
                'result': 'Pass',
                'expect': 'slideshowstrech',
                'actual': 'slideshowstrech',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'verify new slideshow',
                'result': 'Fail',
                'expect': 'slideshow',
                'actual': 'no slideshowstrech',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
            reset_settings(value_ls)
            return False
        if step3(power_m, 4):
            steps = {
                'step_name': 'verify new center show',
                'result': 'Pass',
                'expect': 'center',
                'actual': 'center',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            log.debug("picture not match",
                      common_function.get_current_dir('Test_Report', 'img', '{}_step4.png'.format(case_name)))
            steps = {
                'step_name': 'verify new center show',
                'result': 'Fail',
                'expect': 'center',
                'actual': 'no center',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
            locked_wake_up()
            time.sleep(5)
            reset_settings(value_ls)
            return False
        locked_wake_up()
        time.sleep(5)
        data = step4(power_m, source_size1)
        if data == source_data1:
            steps = {
                'step_name': 'verify new expand show',
                'result': 'Pass',
                'expect': 'expand',
                'actual': 'expand',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'verify new expand show',
                'result': 'Fail',
                'expect': 'expand',
                'actual': 'no expand',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
            reset_settings(value_ls)
            return False
        data5 = step5(power_m)
        if data5 == source_data2:
            steps = {
                'step_name': 'verify new stretch show',
                'result': 'Pass',
                'expect': 'stretch',
                'actual': 'stretch',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            steps = {
                'step_name': 'verify new stretch show',
                'result': 'Fail',
                'expect': 'stretch',
                'actual': 'no stretch',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
            reset_settings(value_ls)
            return False
        if step6(power_m, 7):
            steps = {
                'step_name': 'verify new tile show',
                'result': 'Pass',
                'expect': 'tile',
                'actual': 'tile',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
        else:
            log.debug("picture not match",
                      common_function.get_current_dir('Test_Report', 'img', '{}_step6.png'.format(case_name)))
            steps = {
                'step_name': 'verify new tile show',
                'result': 'Fail',
                'expect': 'tile',
                'actual': 'no tile',
                'note': ''}
            update_cases_result(result_file, case_name, steps)
            locked_wake_up()
            time.sleep(5)
            reset_settings(value_ls)
            return False
        locked_wake_up()
        time.sleep(5)
        power_m.close_all_power_manager()
        reset_settings(value_ls)
        log.info('{} is end'.format(case_name))
    except:
        reset_settings(value_ls)
        log.error(traceback.format_exc())
        error_pic = os.path.join(common_function.get_current_dir(),
                                 r'Test_Report', 'img', '{}.png'.format(case_name))
        capture_screen(error_pic)
        os.popen("hptc-control-panel --term")
        pass
