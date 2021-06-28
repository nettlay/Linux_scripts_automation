import os
from Common import picture_operator, file_operator
import pyautogui
from Common.exception import PathNotFoundError, PicNotFoundError, ClickError, TimeOutError, CaseRunningError
from Common.common_function import get_current_dir, open_window, new_cases_result, check_ip_yaml, update_cases_result, get_folder_items
from Common.picture_operator import capture_screen, capture_screen_by_loc, compare_pic_similarity
from Common.log import log
import time
import subprocess
from abc import abstractmethod


def run_command(commands, timeout=15):
    log.info(f":: Start run Command: {commands}")
    result = subprocess.Popen(commands, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              shell=True)
    try:
        output, error = result.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise TimeOutError(str(e))
    return output.decode('utf8')


def window_close(name):
    log.info(f'close window {name} by command')
    run_command(f"wmctrl -c '{name}'")


def check_window(name):
    result = run_command(f"wmctrl -l | grep -i '{name}'")
    return result


def search_file_from_usb(file_name):
    """
    :return str, absolute file path, name can be a grep in linux
    """
    folder = run_command("ls /media").strip()
    result = run_command(f"find /media/{folder} -type f -iname '{file_name}'").strip()
    if not result:
        raise CaseRunningError(f"File {file_name} not found  in /media/{folder}")
    log.info(f'Find the File: {result}')
    return result


class Window:
    open_window_name: str = ''
    close_windows_name: tuple = ()

    def open(self):
        open_window(self.open_window_name)
        self.check_window_has_opened()

    def close(self):
        time.sleep(2)
        for window in self.close_windows_name:
            time.sleep(2)
            window_close(window)

    def check_window_has_opened(self):
        pass


class PicObjectModel:
    pic_settings = {}

    def __init__(self, loc, name, pic_path):
        self.name = name
        self.loc = loc
        self.pic_path = pic_path

    def __str__(self):
        return f':: Name: {self.name} Loc: {self.loc} Path: {self.pic_path}'

    def __getattr__(self, item):
        log.info(f"-> Find Item: {item}")
        pic_path, offset, position = self.pic_settings.get(item, (None, ()))
        if not pic_path:
            raise KeyError(f"pic settings doesn't have Item: {item}")
        icon_path = get_current_dir(pic_path)
        if not os.path.exists(icon_path):
            raise PathNotFoundError(f"Pic Path: '{icon_path}' Not Exists, Current Path: {icon_path}")
        if not self.loc:
            element_shape = picture_operator.wait_element(icon_path, offset=(0, 0))
        else:
            element_shape = self.__capture_part_screen(icon_path=icon_path, position=position)
        if not element_shape:
            raise PicNotFoundError(f"Item: '{item}' Icon not found, Current Path: {icon_path}")
        loc = self.__calculate_midpoint(loc=element_shape[0], size=element_shape[1], offset=offset)
        flow_obj = self.__class__(loc=loc, name=item, pic_path=pic_path)
        log.info(flow_obj)
        return flow_obj

    def __capture_part_screen(self, icon_path, position: tuple) -> tuple:
        save_path = get_current_dir("loc_demo.png")
        if not position:
            return picture_operator.wait_element(icon_path, offset=(0, 0))
        if not len(position) == 4:
            raise KeyError("Position must be a tuple as: (left, top, width, height)")
        left, top, width, height = position
        current_x, current_y = self.loc
        pos = {"left": current_x + left, "top": current_y + top, "width": width, "height": height}
        capture_screen_by_loc(file_path=save_path, loc_dic=pos)
        items = get_folder_items(icon_path, file_only=True, filter_name=".png")
        pic_path_list = list(map(lambda file_name: icon_path + f"/{file_name}", items))
        for pic_item in pic_path_list:
            element_shape = compare_pic_similarity(img=pic_item, tmp=save_path)
            if element_shape:
                loc, size = element_shape
                loc_x, loc_y = loc
                current_left, current_top = current_x + left + loc_x, current_y + top + loc_y
                return (current_left, current_top), size
        return ()

    @staticmethod
    def __calculate_midpoint(loc: tuple, size: tuple, offset: tuple = (0, 0)) -> tuple:
        """
        get the pic center point
        """
        loc_x, loc_y = loc
        size_x, size_y = size[1], size[0]
        offset_x, offset_y = offset
        return loc_x + int(size_x / 2) + offset_x, loc_y + int(size_y / 2) + offset_y

    @classmethod
    def create_object(cls):
        name = cls.pic_settings.get("Name", cls.__name__)
        return cls(loc=(), name=name, pic_path='')

    def click(self):
        time.sleep(1)
        if not self.loc:
            raise ClickError(f"Can't click, Operation object not declared, Current object: {self.name}, Current Path:{self.pic_path}")
        log.info(f"Click Loc: X: {self.loc[0]}, Y: {self.loc[1]}")
        pyautogui.click(*self.loc)

    def double_click(self):
        if not self.loc:
            raise ClickError(f"Can't click, Operation object not declared, Current object: {self.name}, Current Path:{self.pic_path}")
        log.info(f"Click Loc: X: {self.loc[0]}, Y: {self.loc[1]}")
        pyautogui.click(*self.loc, clicks=2, interval=0.05)

    @staticmethod
    def clear():
        pyautogui.keyDown('backspace')
        time.sleep(4)
        pyautogui.keyUp('backspace')
        pyautogui.keyDown('delete')
        time.sleep(4)
        pyautogui.keyUp('delete')

    def send_keys(self, send_string):
        self.click()
        self.clear()
        pyautogui.typewrite(send_string, interval=0.3)

    # def check_box_status(self):
    #     temp_path = str(BASE_DIR)+"/demo.png"
    #     if not os.path.exists(temp_path):
    #         raise PathNotFoundError(f"Pic Path: '{temp_path}' Not Exists")
    #     loc_x, loc_y = self.x, self.y
    #     offset_x, offset_y = -35, -15
    #     loc = {"left": loc_x + offset_x, "top": loc_y + offset_y, "width": 30, "height": 30}
    #     capture_screen_by_loc(temp_path, loc)
    #     enable = str(self.pic_path) + '/enable'
    #     disable = str(self.pic_path) + '/disable'
    #     enable_list = get_folder_items(enable, file_only=True, filter_name=".png")
    #     disable_list = get_folder_items(disable, file_only=True, filter_name=".png")
    #     flag = None
    #     for i in enable_list:
    #         if compare_pic_similarity(enable + f'/{i}', temp_path):
    #             flag = True
    #             break
    #     for i in disable_list:
    #         if compare_pic_similarity(disable + f'/{i}', temp_path):
    #             flag = False
    #             break
    #     return flag


class ResultControl:

    case_name = None
    yml_path = None

    def __init__(self, case_name):
        ip = check_ip_yaml()
        self.yml_path = get_current_dir("Test_Report/{}.yaml".format(ip))
        self.case_name = case_name

    def update_class_property(self):
        """
        abstract method
        :return:
        """
        pass

    def __update_result(self):
        """
        abstract method
        :return:
        """
        pass

    def start(self):
        """
        abstract method
        :return:
        """
        pass


class ResultHandler(ResultControl):
    flag = None
    event_method_name = None
    error_msg = None
    success_msg = None
    capture = True

    def __init__(self, case_name):
        super().__init__(case_name)
        new_cases_result(self.yml_path, self.case_name)

    def update_class_property(self, **kwargs):
        self.flag = kwargs.get("return", False)
        self.event_method_name = kwargs.get("event_method").__name__
        self.error_msg = kwargs.get("error_msg", {})
        self.success_msg = kwargs.get("success_msg", {})
        self.capture = kwargs.get("capture", True)

    def __update_result(self):
        step = {'step_name': '',
                'result': 'PASS',
                'expect': '',
                'actual': '',
                'note': ''}
        step.update({'step_name': self.event_method_name})
        if not self.flag:
            if self.capture:
                path = get_current_dir("Test_Report/img/{}__{}_exception.png".format(self.case_name, self.event_method_name))
                log.warning(f"capture path: {path}")
                capture_screen(path)
            step.update({'result': 'Fail',
                         'expect': self.error_msg.get("expect", ""),
                         'actual': self.error_msg.get("actual", ""),
                         'note': '{}__{}_exception.png'.format(self.case_name, self.event_method_name) if self.capture else ""})
        else:

            step.update(self.success_msg)
        update_cases_result(self.yml_path, self.case_name, step)
        return

    def start(self):
        return self.__update_result()


class CaseFlowControl:
    """
    Extend the Class and rewrite method: set_method_list
    the case extended the class will create a step file at ./Test_Report/temp/<case_name>.yaml
    if <case_name>.yaml not exists, case will start from beginning
    if -1 in <case_name>.yaml shows that the case has ended
    :exception Set an expected Exception(Default) will be catch while running
    for example:
    use create_list_index_file(1): write 1(index) into file,
    then read_a_file(): return 1
    it will exec from the method_name_list[1:]
    :return: False, if no steps run or any exception happens
             True, if no error happens
    """
    default_save_path: str = get_current_dir("Test_Report/temp/{}.yaml")

    def __init__(self, script_name, case_name, exception: tuple):
        self.__dic = dict(self.__class__.__dict__)
        self.__class_name = self.__class__.__name__
        self.end_function_name = self.end_flow.__name__
        self.__dic.update({self.end_function_name:
                               CaseFlowControl.__dict__.get(self.end_function_name)})
        self.__method_name_list = []
        self.__exec = True
        self.default_save_path = self.default_save_path.format(script_name)
        self.current_step: int = -1
        self.__skip_list = []
        self.__work_around_list_fail = []
        self.__work_around_list_success = []
        self.result_handler = ResultHandler(case_name=case_name)
        self.exception = exception

    def update_dic(self, dic: dict):
        """
        the method will update self.__class__.__dict__
        for example:
        update_dict(CaseFlowControl.__dict__) will get a dic that has both CaseFlowControl method
        and SubClass method, if method name is the same, Subclass will instead of Parent method
        :param dic:
        :return:
        """
        dic = dict(dic)
        dic.update(self.__dic)
        self.__dic = dic

    def end_flow(self, save_path=""):
        """
        create a -1 file and stop the flow
        """
        self.create_list_index_file_and_suspend(index=-1, save_path=save_path)
        log.info("Flow {} Ended".format(self.__class_name))

    def suspend_exec(self):
        """
        stop the flow
        :return:
        """
        self.__exec = False

    def skip(self, name_list: list):
        self.__skip_list = name_list

    def set_callback_fail(self, around_list: list):
        self.__work_around_list_fail = around_list

    def extend_callback_fail(self, around_list: list):
        """
        extend the __work_around_list when work around has started
        """
        self.__work_around_list_fail.extend(around_list)

    def extend_callback_success(self, around_list: list):
        self.__work_around_list_success.extend(around_list)

    def set_callback_success(self, around_list: list):
        self.__work_around_list_success = around_list

    def exec_callback(self, around_list: list):
        while around_list:
            around_name = around_list[0]
            around_list.remove(around_name)
            around_method = self.__dic.get(around_name)
            assert around_method, "{} Not Exist".format(around_name)
            log.info("Start Callback: {}".format(around_name))
            around_method(self)
        self.__work_around_list_success = []
        self.__work_around_list_fail = []

    def __set(self):
        self.__method_name_list = self.set_method_list()
        self.__method_name_list.append("{}".format(self.end_function_name))

    @abstractmethod
    def set_method_list(self) -> list:
        """
        :return: ["a name list contains which method you want to exec", ]
        """
        pass

    def create_list_index_file_and_suspend(self, index: int = 0, save_path="", suspend=True):
        """
        the start method will stop if create the file
        :param suspend: bool, stop the flow immediately, next method will not exec
        :param index: the order in method_name_list
        :param save_path: abs_path
        :return: None
        """
        if not save_path:
            save_path = self.default_save_path
        path = os.path.dirname(save_path)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            log.warning("Create path {}".format(path))
        self.default_save_path = save_path
        file_operator.YamlOperator(save_path).write(str(index))
        if suspend and index != -1:
            log.warning(
                "Create {} Index: {}, Flow {} wil be stop immediately!".format(save_path, index, self.__class_name))
            self.suspend_exec()
        return

    def read_a_file(self, path=""):
        """
        :param path:
        :return: Index of the method_name_list,
        """
        if not path:
            path = self.default_save_path
        if not os.path.exists(path):
            return 0
        res = file_operator.YamlOperator(path).read()
        # os.remove(p)
        try:
            return int(res)
        except:
            return -1

    def start(self):
        self.__set()
        assert self.__method_name_list, "Need a method list!"
        index = self.read_a_file()
        log.info("Get Status: {}".format(index))
        if index == -1:
            log.info(" This {} Flow has Ended".format(self.__class_name))
            return
        flag = True
        self.current_step = index
        new_list = self.__method_name_list[index:]
        for method_name in new_list:
            if method_name in self.__skip_list:
                self.current_step += 1
                continue
            method = self.__dic.get(method_name)
            assert method, "{} Not Exist".format(method_name)
            log.info("Start Step Method {}".format(method_name))
            try:
                result_dict = {"event_method": method,
                               "return": True}
                method(self)
                self.result_handler.update_class_property(**result_dict)
                self.result_handler.start()
                self.exec_callback(self.__work_around_list_success)
            except self.exception as e:
                flag = False
                self.suspend_exec()
                self.end_flow()
                log.error(e)
                result_dict = {"event_method": method,
                               "error_msg": {"actual": "Fail at Index {} : {}".format(self.current_step, e)},
                               "return": False}
                self.result_handler.update_class_property(**result_dict)
                self.result_handler.start()
                self.exec_callback(self.__work_around_list_fail)
            if not self.__exec:
                break
            self.current_step += 1
        log.debug("Capture Flag Return : {}".format(flag))
        return flag


def create_count(file: str, count: int):
    with open(file, "w") as f:
        f.write(f"{count}")
    return count


def read_count(file: str) -> int:
    if not os.path.exists(file):
        return 0
    with open(file, "r") as f:
        count = int(f.read())
    return count