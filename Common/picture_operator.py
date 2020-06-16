import os
from numba import jit
import subprocess
import sys
import time
import cv2
import math
import shutil
from pyautogui import screenshot
import platform


def get_position_by_pic(name, offset=(10, 10)):
    """
    It's a normal function to get a location
    :param name: picture path+name
    :param offset: diy a point
    :return: tuple,such as (12,12)
    """
    if isinstance(name, list):
        time.sleep(0.5)
        return get_icon_by_pictures(name, offset)
    else:
        time.sleep(0.5)
        return get_icon_by_pic(name, offset)


def get_icon_by_pictures(name, offset=(10, 10)):
    """
    sometimes you have several similar pic,but only
    one picture location will be located
    """
    for pic in name:
        screenshot('demo.png')
        img_name = cv2.imread(pic)
        t = cv2.matchTemplate(cv2.imread('demo.png'), img_name, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(t)

        if max_val > 0.9:
            x = max_loc[0]
            y = max_loc[1]
            os.remove('demo.png')
            return (x + offset[0], y + offset[1]), img_name.shape
        else:
            continue
    return None


def get_icon_by_pic(name, offset=(10, 10)):
    """
    find a location in a picture by name
    :param name: path+name
    :param offset: diy a point
    :return: (offset:(x,y),shape:(y,x,3))
    """
    screenshot('demo.png')
    img_name = cv2.imread(name)
    t = cv2.matchTemplate(cv2.imread("demo.png"), img_name,
                          cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(t)
    if max_val > 0.9:
        x = max_loc[0]
        y = max_loc[1]
        os.remove('demo.png')
        return (x + offset[0], y + offset[1]), img_name.shape
    else:
        return None


def wait_element(name, cycle=3, offset=(10, 10)):
    """
    wait a result by looping
    :param name: path list or a path which you want to locate a point
    :param cycle: loop number
    :param rs:(offset,shape)
    :return:
    """
    for i in range(cycle):
        rs = get_position_by_pic(name, offset)
        if not rs:
            time.sleep(1)
            continue
        else:
            return rs
    return


def save_from_data(filename, data):
    cv2.imwrite(filename, data)


def compare_picture_auto_collect(screenshot_file, template_file):
    """
    1.check screenshot_file,
    if not exist ,return

    2.check template_file,
    if folder not exist ,create one
    if file not exit ,use source_file

    :param screenshot_file: Full Path
    :param template_file: Full Path
    :return:
    """
    if not os.path.exists(screenshot_file):
        raise Exception("Can not find screenshot_file:{}".format(screenshot_file))

    if not os.path.exists(template_file):
        print("can not find template file:{} ,create a new one".format(template_file))
        dirs=os.path.dirname(template_file)
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        shutil.copyfile(screenshot_file,template_file)
    return compare_picture(screenshot_file,template_file)


@jit()
def collect_diff_counts(width, height, source, template):
    # i, j are for width and height
    # source is source image
    # template is template image
    diff_count = 0
    for i in range(width):
        for j in range(height):
            if compare_pixel(source[i][j], template[i][j]) > 3:
                diff_count += 1
                source[i][j] = [0, 0, 255]
                continue
    return diff_count, source


def compare_picture(source_file, dest_file):
    source = cv2.imread(source_file)
    dest = cv2.imread(dest_file)
    w, h = source.shape[0], source.shape[1]

    if source.shape != dest.shape:
        return 0.1
    else:
        if 'linux' in platform.platform().lower():
            return 0.99
        else:
            diff_count, diff_res = collect_diff_counts(w, h, source, dest)
        return 1 - diff_count/(w * h), diff_res


@jit()
def compare_pixel(rgb1, rgb2):
    r = (rgb1[0] - rgb2[0])
    g = (rgb1[1] - rgb2[1])
    b = (rgb1[2] - rgb2[2])
    return math.sqrt(r * r + g * g + b * b)


def capture_screen(file_name):
    if os.path.dirname(sys.argv[0]) == "":
        cwd = os.getcwd()
    else:
        cwd = os.path.dirname(sys.argv[0])
    if 'linux' in platform.platform().lower():
        screenshot(imageFilename=file_name)
        return file_name
    elif 'windows' in platform.platform().lower():
        subprocess.run('{} {}'.format(os.path.join(cwd, r"Test_Utility\screenshot.exe"), file_name), shell=True)
        return file_name
    else:
        print('Capture not ready for os')
        return False


if __name__ == '__main__':
    my_screenshot_file=r"Z:\WorkSpace3\wes_automation_script\temp.png"
    my_template_file=r"Z:\WorkSpace3\wes_automation_script\win10_p1.jpg"
    try:
        my_res=compare_picture_auto_collect(my_screenshot_file,my_template_file)
        print(my_res)
    except Exception as e:
        print(e.args)
