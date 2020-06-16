
def get_single_monitor_info(monitor_list, i):
    single_monitor_info = []
    if len(monitor_list) <= 0:
        return
    monitor_num = "[Monitor%s]" % i
    for mon in monitor_list:
        if monitor_num in mon:
            single_monitor_info = mon
            break
    return single_monitor_info


def layout_setting(pro, monitor_list):
    w = 'None'
    h = 'None'
    o = 'None'
    x = 'None'
    y = 'None'
    layout_info = []
    k = int(pro[0])
    width = int(pro[1])
    height = int(pro[2])
    frequency = pro[3]
    layout = pro[4]
    if not monitor_list:
        return
    total_monitors = len(monitor_list)
    if total_monitors < 1:
        return
    for i in range(k):
        single_info = get_single_monitor_info(monitor_list, i)
        num = single_info[0]
        name = single_info[1]
        moni_id = single_info[2]
        colour = single_info[3]
        flag = single_info[6]
        f = "DisplayFrequency=%s" % frequency
        if k == 2:
            if layout.upper() == 'L Left'.upper():
                if i == 0:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=%s" % str(height - width)
            elif layout.upper() == 'Landscape 2X1'.upper():
                if i == 0:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(0 - width)
                    y = "PositionY=0"
            elif layout.upper() == 'Landscape 1X2'.upper():
                if i == 0:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=%s" % str(height)
            elif layout.upper() == 'Portrait 2X1'.upper():
                if i == 0:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(height)
                    y = "PositionY=0"
            else:
                msg = 'Not Support %s monitors %s layout' % (str(k), layout)
        elif k == 3:
            if layout.upper() == 'Landscape 3X1'.upper():
                if i == 0:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=0"
                elif i == 2:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(2 * width)
                    y = "PositionY=0"
            elif layout.upper() == 'Portrait 3X1'.upper():
                if i == 0:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(0 - height)
                    y = "PositionY=0"
                elif i == 2:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(0 - 2 * height)
                    y = "PositionY=0"
            elif layout.upper() == 'Left L'.upper():
                if i == 0:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=0"
                elif i == 2:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=%s" % (0 - height)
            else:
                msg = 'Not Support %s monitors %s layout' % (str(k), layout)
        elif k == 4:
            if layout.upper() == 'Landscape 2X2'.upper():
                if i == 0:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=0"
                elif i == 2:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=%s" % str(height)
                elif i == 3:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=%s" % str(height)
            elif layout.upper() == 'Portrait 2X2'.upper():
                if i == 0:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(0 - height)
                    y = "PositionY=0"
                elif i == 2:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(0 - height)
                    y = "PositionY=%s" % str(0 - width)
                elif i == 3:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=0"
                    y = "PositionY=%s" % str(0 - width)
            elif layout.upper() == 'Left L'.upper():
                if i == 0:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=0"
                elif i == 2:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(2 * width)
                    y = "PositionY=0"
                elif i == 3:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(2 * width)
                    y = "PositionY=%s" % str(0 - height)
            else:
                msg = 'Not Support %s monitors %s layout' % (str(k), layout)
        elif k == 6:
            if layout.upper() == 'Landscape 3X2'.upper():
                if i == 0:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=0"
                elif i == 2:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(2 * width)
                    y = "PositionY=0"
                elif i == 3:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=%s" % str(height)
                elif i == 4:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=%s" % str(height)
                elif i == 5:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(2 * width)
                    y = "PositionY=%s" % str(height)
            elif layout.upper() == 'Portrait 3X2'.upper():
                if i == 0:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(0 - height)
                    y = "PositionY=0"
                elif i == 2:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(0 - 2 * height)
                    y = "PositionY=0"
                elif i == 3:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=0"
                    y = "PositionY=%s" % str(0 - width)
                elif i == 4:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(0 - height)
                    y = "PositionY=%s" % str(0 - width)
                elif i == 5:
                    w = "Width=%s" % str(height)
                    h = "Height=%s" % str(width)
                    o = 'DisplayOrientation=1'
                    x = "PositionX=%s" % str(0 - 2 * height)
                    y = "PositionY=%s" % str(0 - width)
            elif layout.upper() == 'Left L'.upper():
                if i == 0:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=0"
                    y = "PositionY=0"
                elif i == 1:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(width)
                    y = "PositionY=0"
                elif i == 2:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(2 * width)
                    y = "PositionY=0"
                elif i == 3:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(3 * width)
                    y = "PositionY=0"
                elif i == 4:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(3 * width)
                    y = "PositionY=%s" % str(0 - height)
                elif i == 5:
                    w = "Width=%s" % str(width)
                    h = "Height=%s" % str(height)
                    o = 'DisplayOrientation=0'
                    x = "PositionX=%s" % str(3 * width)
                    y = "PositionY=%s" % str(0 - 2 * height)
            else:
                msg = 'Not Support %s monitors %s layout' % (str(k), layout)
        single_layout_info = [num, name, moni_id, colour, w, h, flag, f, o, x, y]
        single_layout_info2 = []
        for p in single_layout_info:
            j = '%s\n' % p
            single_layout_info2.append(j)
        layout_info.append(single_layout_info2)
    return layout_info