from Common.tool import *
import time, traceback
from Test_Script.ts_precheck.precheck_function import SwitchThinProMode
from Common.common_function import *


class Edocs_App:
    def __init__(self, case_name):
        self.case_name = case_name

    def prepare(self):
        press_keys([keyboard.control_l_key, keyboard.alt_l_key, 's'], 1)
        type_string('hp regulatory docs', 1)
        press_key(keyboard.down_key)
        press_key(keyboard.enter_key)

    def preparation(self):
        '''
        get the hp regulatory docs window
        :return:
        '''
        press_keys([keyboard.control_l_key, keyboard.alt_l_key, 's'])
        type_string('hp regulatory docs')
        press_key(keyboard.down_key)
        press_key(keyboard.enter_key)
        return True

    def repreparation(self, filename):
        '''
        if step fail, you can restart preparation() to continue checking
        :param filename: path
        :return:
        '''
        rs = self.check_cancel_icon(filename)
        if rs:
            self.dblclick(rs)
        time.sleep(0.5)
        return self.preparation()

    @staticmethod
    def check_home_exist(filename, assertion=True):
        return check_object_exist(filename, 2)

    @staticmethod
    def check_subfolders_exist(filename, assertion=True):
        response = check_object_exist(filename)
        if response:
            rs, shape = response
            return rs
        return

    @staticmethod
    def check_trfpdf_exist(filename, assertion=True):
        offset = (5, 5)
        response = check_object_exist(filename, offset=offset)
        if response:
            rs, shape = response
            print(rs)
            return rs
        return

    @staticmethod
    def check_pdf_in_subfolders(filename, assertion=True):
        offset = (10, 30)
        response = check_object_exist(filename, 2, offset=offset)
        if response:
            rs, shape = response
            return rs
        return

    @staticmethod
    def check_backing_out(filename, assertion=True):
        offset = (5, 5)
        response = check_object_exist(filename, 2, offset=offset)
        if response:
            rs = response[0]
            return rs
        else:
            return response

    @staticmethod
    def check_upicon_color(filename, assertion=True):
        offset = (15, 15)
        response = check_object_exist(filename, offset=offset)
        if response:
            rs = response[0]
            return rs
        return

    @staticmethod
    def check_flder_can_open(filename, assertion=True):
        response = check_object_exist(filename, 2)
        return response

    def check_pdf_can_open(self, filename, assertion=True):
        return self.check_flder_can_open(filename, assertion=assertion)

    @staticmethod
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

    @staticmethod
    def check_cancel_icon(filename="hp_regulatory_docs_app.png", assertion=True):
        response = check_object_exist(filename)
        if response:
            rs = response[0]
            return rs

    @staticmethod
    def check_open_icon(filename, assertion=True):
        response = check_object_exist(filename)
        if response:
            rs = response[0]

            return rs

    @staticmethod
    def sglclick(location):
        x, y = location
        time.sleep(0.5)
        return click(x, y)

    @staticmethod
    def dblclick(location):
        x, y = location
        clicknum = 2
        time.sleep(0.5)
        return click(x, y, clicknum)

    def prepare_check(self, cancel_ico, home_img):
        name = self.prepare_check.__name__
        try:
            self.preparation()
            events(self.check_home_exist, home_img, annotation=(name, "can't find hp_regulatory_docs_app"),
                   case_name=self.case_name)
            events(self.check_cancel_icon, cancel_ico, self.sglclick, "fromtest", annotation=(name, "can't find cancel icon"),
                   case_name=self.case_name)
            events(self.check_home_exist, home_img, assertion=False, annotation=(name, "cancel icon can't work"),
                   case_name=self.case_name)
        except AssertionError as e:
            print(e)
            if "check_home_exist" in repr(e):
                return False
        except Exception as e:
            print(e)
            return False
        return True

    def test_func_type1(self, *args):
        name = self.test_func_type1.__name__
        home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn = args
        try:
            events(self.check_subfolders_exist, flder, self.dblclick, "fromtest", annotation=(name,),
                   case_name=self.case_name)
            events(self.check_flder_can_open, flder, assertion=False, annotation=(name,), case_name=self.case_name)
            events(self.check_pdf_in_subfolders, pdf, self.dblclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_pdf_can_open, pdf, assertion=False, annotation=(name,), case_name=self.case_name)
            events(self.close_pdf, pdfclosebtn, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_backing_out, fl_back, self.dblclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_backing_out, fl_back, assertion=False, annotation=(name,), case_name=self.case_name)
        except AssertionError as e:
            print(e)
            print("repreation()")
            try:
                self.repreparation(cancel_ico)
            except:
                traceback.print_exc()
        return

    def test_func_type2(self, *args):
        name = self.test_func_type2.__name__
        home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn = args
        try:
            events(self.check_subfolders_exist, flder, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_open_icon, open_ico, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_flder_can_open, flder, assertion=False, annotation=(name,), case_name=self.case_name)
            events(self.check_pdf_in_subfolders, pdf, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_open_icon, open_ico, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_pdf_can_open, pdf, assertion=False, annotation=(name,), case_name=self.case_name)
            events(self.close_pdf, pdfclosebtn, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_upicon_color, up_en_cio, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_backing_out, up_en_cio, assertion=False, annotation=(name,), case_name=self.case_name)
        except AssertionError as e:
            print(e)
            print("repreation()")
            try:
                self.repreparation(cancel_ico)
            except:
                traceback.print_exc()
        return

    def test_func_type3(self, *args):
        name = self.test_func_type3.__name__
        home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn = args
        try:
            events(self.check_subfolders_exist, flder, self.dblclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_flder_can_open, flder, assertion=False, annotation=(name,), case_name=self.case_name)
            events(self.check_pdf_in_subfolders, pdf, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_open_icon, open_ico, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_pdf_can_open, pdf, assertion=False, annotation=(name,), case_name=self.case_name)
            events(self.close_pdf, pdfclosebtn, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_upicon_color, up_en_cio, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_backing_out, up_en_cio, assertion=False, annotation=(name,), case_name=self.case_name)
        except AssertionError as e:
            print(e)
            print("repreation()")
            try:
                self.repreparation(cancel_ico)
            except:
                traceback.print_exc()
        return

    def miscell_test(self, *args):
        name = self.miscell_test.__name__
        home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn, rtf = args
        try:
            self.preparation()
            events(self.check_open_icon, open_ico, self.sglclick, "fromtest", annotation=(name, "can't find icon"), case_name=self.case_name)
            events(self.check_upicon_color, "up_disabled.png", self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_home_exist, home_img, annotation=(name, "up icon amazingly work!"), case_name=self.case_name)

            events(self.check_trfpdf_exist, rtf, self.dblclick, "fromtest", annotation=(name,), case_name=self.case_name)
            events(self.check_pdf_can_open, rtf, assertion=False, annotation=(name,), case_name=self.case_name)
            events(self.close_pdf, pdfclosebtn, self.sglclick, "fromtest", annotation=(name,), case_name=self.case_name)
        except AssertionError as e:
            print(e)
            print("repreation()")
            try:
                self.repreparation(cancel_ico)
            except:
                traceback.print_exc()
        return


def start(case_name, **kwargs):
    SwitchThinProMode(switch_to='admin')
    # ip = get_ip()
    ip = check_ip_yaml()
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
    edoc_app = Edocs_App(case_name)
    flag = edoc_app.prepare_check(cancel_ico, home_img)
    if flag:
        # miscell test
        edoc_app.miscell_test(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn, rtf)

        # testevents
        edoc_app.test_func_type1(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)

        # testevents
        flder = next(flderiter)
        pdf = check_dic.get(flder)
        edoc_app.test_func_type2(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)

        # testevents
        flder = next(flderiter)
        pdf = check_dic.get(flder)
        edoc_app.test_func_type3(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)

        # testevents
        flder = next(flderiter)
        pdf = check_dic.get(flder)
        edoc_app.test_func_type2(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)

        # testevents
        flder = next(flderiter)
        pdf = check_dic.get(flder)
        edoc_app.test_func_type1(home_img, flder, pdf, fl_back, open_ico, cancel_ico, up_en_cio, pdfclosebtn)
    else:
        press_keys([keyboard.control_l_key, keyboard.alt_l_key, 's'], 1)
        print("fail at start")
    try:
        events(edoc_app.check_cancel_icon, cancel_ico, edoc_app.sglclick, "fromtest", case_name=case_name)
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
