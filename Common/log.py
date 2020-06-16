import os
import time
from Common import common_function


class Logging:
    def __init__(self, output=True):
        self.__report_path = os.path.join(common_function.get_current_dir(), 'Test_Report')
        self.__log_path = os.path.join(self.__report_path, 'log')
        if not os.path.exists(self.__report_path):
            os.mkdir(self.__report_path)
        if not os.path.exists(self.__log_path):
            os.mkdir(self.__log_path)
        self.__log_name = time.strftime("%Y-%m-%d-%H", time.localtime()) + ".log"
        self.log_file_path = os.path.join(self.__log_path, self.__log_name)
        self.style = '\033[1;31;1m#msg#\033[0m'
        self.print = output

    def log(self, rank, log):
        if not os.path.exists(self.__log_path):
            os.makedirs(self.__log_path)

        cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print_msg = "{} \t {} \t {}".format(cur_time, rank, log)
        line = "[{}] \t".format(cur_time) + print_msg + '\n'

        if not os.access(self.log_file_path, os.F_OK):
            with open(self.log_file_path, "w", encoding='utf-8') as f:
                f.writelines(line)
        else:
            with open(self.log_file_path, "a", encoding='utf-8') as f:
                f.writelines(line)

        if self.print:
            print(self.style.replace('#msg#', print_msg))


class Logger(Logging):
    def __init__(self, output=True):
        super().__init__(output=output)

    def info(self, log):
        rank = '[INFO]'
        self.style = '\033[1;21;1m#msg#\033[0m'
        self.log(rank, log)

    def warning(self, log):
        self.style = '\033[1;33;1m#msg#\033[0m'
        rank = '[WARNING]'
        self.log(rank, log)

    def error(self, log):
        self.style = '\033[1;31;1m#msg#\033[0m'
        rank = '[ERROR]'
        self.log(rank, log)
