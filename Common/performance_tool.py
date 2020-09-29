import psutil
import time
import functools


def get_net_info():
    """
    decorator for Performance
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            if self._net_key:
                recv = psutil.net_io_counters(pernic=True).get(self._net_key).bytes_recv
                sent = psutil.net_io_counters(pernic=True).get(self._net_key).bytes_sent
                time.sleep(1)
                recv_new = psutil.net_io_counters(pernic=True).get(self._net_key).bytes_recv
                sent_new = psutil.net_io_counters(pernic=True).get(self._net_key).bytes_sent
                net_recv = float('%.2f' % (recv_new - recv)) / 1024
                net_send = float('%.2f' % (sent_new - sent)) / 1024
            else:
                net_recv = 0
                net_send = 0
            cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cpu_slv, syl_nc = func(*args, **kwargs)
            return cur_time, cpu_slv, syl_nc, net_recv, net_send

        return wrapper

    return decorator


class Performance:
    # _Gpus = None
    _memory = None
    _net_key = ""

    # @classmethod
    # def _get_gpu_objects(cls):
    #     cls._Gpus = GPUtil.getGPUs()
    #     return cls._Gpus

    # @classmethod
    # def get_gpu_info(cls):
    #     gpu_objs = cls._get_gpu_objects()
    #     total = 0
    #     for o in gpu_objs:
    #         total += round((o.memoryTotal) / 1024)
    #     return total

    @classmethod
    def _get_virtual_memory(cls):
        cls._memory = psutil.virtual_memory()
        return cls._memory

    @classmethod
    def _get_net_keys(cls):
        keys = psutil.net_io_counters(pernic=True).keys()
        if "Ethernet" in keys:
            cls._net_key = "Ethernet"
        elif "以太网" in keys:
            cls._net_key = "以太网"
        elif "Wi-Fi" in keys:
            cls._net_key = "Wi-Fi"
        elif "eth0" in keys:
            cls._net_key = "eth0"
        return

    @classmethod
    def get_cpu_info(cls):
        cpu_count = psutil.cpu_count(logical=False)  # 1代表单核CPU，2代表双核CPU
        xc_count = psutil.cpu_count()  # 线程数，如双核四线程
        return cpu_count, xc_count

    @classmethod
    def get_memory_info(cls):
        memory = cls._get_virtual_memory()
        total_nc = round((float(memory.total) / 1024 / 1024 / 1024), 2)
        return total_nc

    @classmethod
    def get_system_obj(cls):
        cpu_count, xc_count = cls.get_cpu_info()
        total_nc = cls.get_memory_info()
        print("|{:^10}|{:^10}|{:^10}|".format("CPU核数", "CPU线程数", "总内存（G）"))
        print(" {:^12} {:^12} {:^12.2f} ".format(cpu_count, xc_count, total_nc))
        return cls(cpu_count, xc_count, total_nc)

    def __init__(self, cpu_count, xc_count, total_nc):
        self.cpu_count = cpu_count
        self.xc_count = xc_count
        self.total_nc = total_nc
        self._get_net_keys()
        self.file = None

    @get_net_info()
    def get_system_info(self):
        cpu_slv = round((psutil.cpu_percent(1)), 2)  # cpu使用率
        memory = self._get_virtual_memory()
        syl_nc = round((float(memory.used) / float(memory.total) * 100), 2)  # 内存使用率
        return cpu_slv, syl_nc

    def start(self, times=30) -> None:
        t = 0
        while t <= times:
            t += 1
            cur_time, cpu_slv, syl_nc, net_recv, net_send = self.get_system_info()
            if self.file:
                with open(self.file, "a+", encoding="utf-8") as f:
                    print("[{}]CPU Usage(%):{} Memory Usage(%):{} Receive:{:.2f}KB/s Send:{:.2f}KB/s".format(
                        cur_time, cpu_slv, syl_nc, net_recv, net_send), file=f)
            else:
                print("[{}]CPU使用率(%):{} 内存使用率(%):{} Receive:{:.2f}KB/s Send:{:.2f}KB/s".format(
                    cur_time, cpu_slv, syl_nc, net_recv, net_send))


if __name__ == '__main__':
    p = Performance.get_system_obj()
    p.file = "./test.txt"
    p.start()
