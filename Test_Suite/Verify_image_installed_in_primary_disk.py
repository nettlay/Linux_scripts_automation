from Common import common_function
from Test_Script.ts_precheck import network_function
import Test_Script.ts_precheck.precheck_function as common_function_tp
from Test_Script.ts_precheck import precheck_function
from Common.tool import get_root_path
from Common.common_function import *


class CheckStorage:
    def __init__(self):
        self.para = common_function.load_global_parameters()
        self.platform = self.para['platform']
        self.config = self.para['config']
        self.storage = precheck_function.storage_info(self.platform, self.config)
        self.primary_card_label = ''
        self.primary_card_size_current = ''
        # self.primary_storage = self.storage[0]
        # self.primary_storage_size = ''
        # self.secondary_storage_size = ''
        self.log = common_function.log
        self.log.info("-" * 60)
        self.log.info("case name: Verify image installed in primary disk")
        self.log.info('target platform: {}, target config: {}'.format(self.platform, self.config))

    def get_size_matrix(self, pri_or_second):
        size_info = ''
        if pri_or_second == 'primary':
            size_info = self.storage[0]
        elif pri_or_second == 'secondary':
            size_info = self.storage[1]
        if size_info:
            for info in size_info.split(' '):
                if not info:
                    continue
                if info[-1] == 'G':
                    return info[:-1]
                elif info[-2:] == 'GB':
                    return info[:-2]
                else:
                    continue
        else:
            self.log.info('Failed to get size info from matrix for {} storage.'.format(pri_or_second))

    def check_image_in_primary_disk(self):
        primary_storage_size_matrix = self.get_size_matrix('primary')
        self.log.info('primary storage size from matrix: {}'.format(primary_storage_size_matrix))
        self.primary_card_label = precheck_function.primary_card_label()
        if not self.primary_card_label:
            self.log.info('Fail to get primary card label.')
            return 'fail'
        self.log.info('primary_card_label: {}'.format(self.primary_card_label))
        self.primary_card_size_current = precheck_function.card_size(self.primary_card_label)
        self.log.info('primary_card_size_current with bytes: {}'.format(self.primary_card_size_current[1]))
        if not self.primary_card_size_current:
            self.log.info('Fail to get current primary card size.')
            return 'fail'
        if abs(int(self.primary_card_size_current[1][:-9]) - int(primary_storage_size_matrix)) <= 2:
            self.log.info('Image installed in primary disk {}.'.format(self.primary_card_label))
            return True
        else:
            self.log.info('Image is not installed in primary disk.')
            return False

    def check_disk_extended(self):
        partition_size = precheck_function.partition_size(self.primary_card_label)
        pri_size_GiB = self.primary_card_size_current[0]
        partition_size_unified = self.unified_size(partition_size)
        pri_size_GiB_unified = self.unified_size(pri_size_GiB)
        if partition_size_unified == pri_size_GiB_unified:
            self.log.info('Disk is extended.')
            return True
        else:
            self.log.info('Disk is not extended. Primary disk size is {0} GiB. Partition size is {1} GiB.'.
                          format(pri_size_GiB, partition_size))
            return False
        # print(partition_size)
        # print(pri_size_GiB)

    # If size has decimal, discard the value after decimal.
    def unified_size(self, size):
        if size:
            return size.split('.')[0]
        else:
            self.log.info('Invalid size {}'.format(size))


def start(case_name, **kwargs):
    common_function_tp.SwitchThinProMode(switch_to='admin')
    # report_file = network_function.system_ip() + '.yaml'
    # ip = common_function.check_ip_yaml()
    # report_file = get_root_path("Test_Report/{}.yaml".format(ip))
    base_name = get_report_base_name()
    report_file = get_current_dir('Test_Report', base_name)
    common_function.new_cases_result(report_file, case_name)  # new report
    check_storage = CheckStorage()
    primary_result = check_storage.check_image_in_primary_disk()
    if primary_result is True:
        step1 = {'step_name': 'Check whether image installed in primary disk',
                 'result': 'Pass',
                 'expect': 'in primary disk',
                 'actual': 'in primary disk',
                 'note': 'none'}
    elif primary_result == 'fail':
        step1 = {'step_name': 'Check whether image installed in primary disk',
                 'result': 'Fail',
                 'expect': 'in primary disk',
                 'actual': 'Fail to get primary card label or fail to get current primary card size',
                 'note': 'none'}
    else:
        step1 = {'step_name': 'Check whether image installed in primary disk',
                 'result': 'Fail',
                 'expect': 'in primary disk',
                 'actual': 'not in primary disk',
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step1)
    if primary_result is not True:
        return False
    extended_result = check_storage.check_disk_extended()
    if extended_result is True:
        step2 = {'step_name': 'Check whether disk is extended',
                 'result': 'Pass',
                 'expect': 'extended',
                 'actual': 'extended',
                 'note': 'none'}
    else:
        step2 = {'step_name': 'Check whether disk is extended',
                 'result': 'Fail',
                 'expect': 'extended',
                 'actual': 'not extended',
                 'note': 'none'}
    common_function.update_cases_result(report_file, case_name, step2)


