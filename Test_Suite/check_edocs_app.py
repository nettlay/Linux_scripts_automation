from Common.tool import *
import time, traceback
from Test_Script.ts_precheck.precheck_function import SwitchThinProMode
from Common.common_function import *


def prepare():
    press_keys([keyboard.control_l_key, keyboard.alt_l_key, 's'], 1)
    type_string('hp regulatory docs', 1)
    press_key(keyboard.down_key)
    press_key(keyboard.enter_key)


def preparation():
    '''
    get the hp regulatory docs window
    :return:
    '''
    press_keys([keyboard.control_l_key, keyboard.alt_l_key, 's'])
    type_string('hp regulatory docs')
    press_key(keyboard.down_key)
    press_key(keyboard.enter_key)
    return True


def repreparation(filename):
    '''
    if step fail, you can restart preparation() to continue checking
    :param filename: path
    :return:
    '''
    rs = check_cancel_icon(filename)
    if rs:
        dblclick(rs)
    time.sleep(0.5)
    return preparation()


def check_home_exist(filename, assertion=True):
    return check_object_exist(filename, 2)


def check_subfolders_exist(filename, assertion=True):
    response = check_object_exist(filename)
    if response:
        rs, shape = response
        return rs
    return


def check_trfpdf_exist(filename, assertion=True):
    offset = (5, 5)
    response = check_object_exist(filename, offset=offset)
    if response:
        rs, shape = response
        print(rs)
        return rs
    return


def check_pdf_in_subfolders(filename, assertion=True):
    offset = (10, 30)
    response = check_object_exist(filename, 2, offset=offset)
    if response:
        rs, shape = response
        return rs
    return


def check_backing_out(filename, assertion=True):
    offset = (5, 5)
    response = check_object_exist(filename, 2, offset=offset)
    if response:
        rs = response[0]
        return rs
    else:
        return response


def check_upicon_color(filename, assertion=True):
    offset = (15, 15)
    response = check_object_exist(filename, offset=offset)
    if response:
        rs = response[0]
        return rs
    return


def check_flder_can_open(filename, assertion=True):
    response = check_object_exist(filename, 2)
    return response


def check_pdf_can_open(filename, assertion=True):
    return check_flder_can_open(filename, assertion=assertion)


def close_pdf(filename, assertion=True):
    offset = (10, 10)
    try:
        response = check_object_exist(filename, 2, offset)
        assert response is not None, "can't find {} but it's a script bug".format(filename)
        rs, shape = response
        return rs
    except AssertionError as e:
        print(e)
        try:
            response = check_object_exist("hp_app_icon.png")
            assert response is not None, "can't find hp_app_icon but it's a script bug"
            rs, shape = response
            return rs
        except AssertionError as e:
            print(e)
    return


def check_cancel_icon(filename="hp_regulatory_docs_app.png", assertion=True):
    response = check_object_exist(filename)
    if response:
        rs = response[0]
        return rs


def check_open_icon(filename, assertion=True):
    response = check_object_exist(filename)
    if response:
        rs = response[0]

        return rs


def sglclick(location):
    x, y = location
    time.sleep(0.5)
    return click(x, y)


def dblclick(location):
    x, y = location
    clicknum = 2
    time.sleep(0.5)
    return click(x, y, clicknum)


def prepare_check(cancel_ico, home_img):
    name = prepare_check.__name__
    try:
        preparation()
        events(check_home_exist, home_img, annotation=(name, "can't find hp_regulatory_docs_app"))
        events(check_cancel_icon, cancel_ico, sglclick, "fromtest", annotation=(name, "can't find cancel icon"))
        events(check_home_exist, home_img, assertion=False, annotation=(name, "cancel icon can't work"))
    except AssertionError as e:
        print(e)
        if "check_home_exist" in repr(e):
            return False
    except Exception as e:
        print(e)
        return False
    return True


def test_func_type1(*args):
    name = test_func_type1.__name__
    home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn = args
    try:
        events(check_subfolders_exist, flder, dblclick, "fromtest", annotation=(name,))
        events(check_flder_can_open, flder, assertion=False, annotation=(name,))
        events(check_pdf_in_subfolders, pdf, dblclick, "fromtest", annotation=(name,))
        events(check_pdf_can_open, pdf, assertion=False, annotation=(name,))
        events(close_pdf, pdfclosebtn, sglclick, "fromtest", annotation=(name,))
        events(check_backing_out, fl_back, dblclick, "fromtest", annotation=(name,))
        events(check_backing_out, fl_back, assertion=False, annotation=(name,))
    except AssertionError as e:
        print(e)
        print("repreation()")
        try:
            repreparation(cancel_ico)
        except:
            traceback.print_exc()
    return


def test_func_type2(*args):
    name = test_func_type2.__name__
    home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn = args
    try:
        events(check_subfolders_exist, flder, sglclick, "fromtest", annotation=(name,))
        events(check_open_icon, open_ico, sglclick, "fromtest", annotation=(name,))
        events(check_flder_can_open, flder, assertion=False, annotation=(name,))
        events(check_pdf_in_subfolders, pdf, sglclick, "fromtest", annotation=(name,))
        events(check_open_icon, open_ico, sglclick, "fromtest", annotation=(name,))
        events(check_pdf_can_open, pdf, assertion=False, annotation=(name,))
        events(close_pdf, pdfclosebtn, sglclick, "fromtest", annotation=(name,))
        events(check_upicon_color, up_en_cio, sglclick, "fromtest", annotation=(name,))
        events(check_backing_out, up_en_cio, assertion=False, annotation=(name,))
    except AssertionError as e:
        print(e)
        print("repreation()")
        try:
            repreparation(cancel_ico)
        except:
            traceback.print_exc()
    return


def test_func_type3(*args):
    name = test_func_type3.__name__
    home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn = args
    try:
        events(check_subfolders_exist, flder, dblclick, "fromtest", annotation=(name,))
        events(check_flder_can_open, flder, assertion=False, annotation=(name,))
        events(check_pdf_in_subfolders, pdf, sglclick, "fromtest", annotation=(name,))
        events(check_open_icon, open_ico, sglclick, "fromtest", annotation=(name,))
        events(check_pdf_can_open, pdf, assertion=False, annotation=(name,))
        events(close_pdf, pdfclosebtn, sglclick, "fromtest", annotation=(name,))
        events(check_upicon_color, up_en_cio, sglclick, "fromtest", annotation=(name,))
        events(check_backing_out, up_en_cio, assertion=False, annotation=(name,))
    except AssertionError as e:
        print(e)
        print("repreation()")
        try:
            repreparation(cancel_ico)
        except:
            traceback.print_exc()
    return


def miscell_test(*args):
    name = miscell_test.__name__
    home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn, rtf = args
    try:
        preparation()
        events(check_open_icon, open_ico, sglclick, "fromtest", annotation=(name, "can't find icon"))
        events(check_upicon_color, "up_disabled.png", sglclick, "fromtest", annotation=(name,))
        events(check_home_exist, home_img, annotation=(name, "up icon amaz"
                                                             "ingly work!"))

        events(check_trfpdf_exist, rtf, dblclick, "fromtest", annotation=(name,))
        events(check_pdf_can_open, rtf, assertion=False, annotation=(name,))
        events(close_pdf, pdfclosebtn, sglclick, "fromtest", annotation=(name,))
    except AssertionError as e:
        print(e)
        print("repreation()")
        try:
            repreparation(cancel_ico)
        except:
            traceback.print_exc()
    return


def start(case_name, **kwargs):
    SwitchThinProMode(switch_to='admin')
    ip = get_ip()
    path = get_root_path("Test_Report/{}.yaml".format(ip))
    new_cases_result(path, case_name)
    home_img = "hp_regulatory_docs_app.png"
    check_dic = {"EULA.png": "PDFLIST1.png",
                 "RSEN.png": "PDFLIST1.png",
                 "SCG.png": "PDFLIST1.png",
                 "UG.png": "PDFLIST1.png",
                 "Warranty.png": "PDFLIST1.png"}
    flderiter = iter(check_dic)
    flder = next(flderiter)
    pdf = "PDFLIST1.png"
    fl_back = "folderback.png"
    open_ico = "open.png"
    cancel_ico = "cancel.png"
    up_en_cio = "up_enabled.png"
    pdfclosebtn = "pdfclosebtn.png"
    rtf = "RTF.png"
    # test_precondition
    flag = prepare_check(cancel_ico, home_img)
    if flag:
        # miscell test
        miscell_test(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn, rtf)

        # testevents
        test_func_type1(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)

        # testevents
        flder = next(flderiter)
        pdf = check_dic.get(flder)
        test_func_type2(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)

        # testevents
        flder = next(flderiter)
        pdf = check_dic.get(flder)
        test_func_type3(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)

        # testevents
        flder = next(flderiter)
        pdf = check_dic.get(flder)
        test_func_type2(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)

        # testevents
        flder = next(flderiter)
        pdf = check_dic.get(flder)
        test_func_type1(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)
    else:
        press_keys([keyboard.control_l_key, keyboard.alt_l_key, 's'], 1)
        print("fail at start")
    try:
        events(check_cancel_icon, cancel_ico, sglclick, "fromtest")
    except:
        pass
    return


if __name__ == "__main__":
    start()
    # home_img = "hp_regulatory_docs_app.png"
    # check_dic = {"EULA.png": "PDFLIST1.png",
    #              "RSEN.png": "PDFLIST1.png",
    #              "SCG.png": "PDFLIST1.png",
    #              "UG.png": "PDFLIST1.png",
    #              "Warranty.png": "PDFLIST1.png"}
    # flderiter = iter(check_dic)
    # flder = next(flderiter)
    # pdf = "PDFLIST1.png"
    # fl_back = "folderback.png"
    # open_ico = "open.png"
    # cancel_ico = "cancel.png"
    # up_en_cio = "up_enabled.png"
    # pdfclosebtn = "pdfclosebtn.png"
    # rtf = "RTF.png"
    # name = "af"
