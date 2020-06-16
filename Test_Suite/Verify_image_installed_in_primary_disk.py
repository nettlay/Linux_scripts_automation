from Common import common_function
from Common import report
import Test_Script.ts_precheck.precheck_function as common_function_tp
from Test_Script.ts_precheck import precheck_function


class CheckStorage:
    def __init__(self):
        self.para = common_function.load_global_parameters()
        # self.config_name = '{}_{}'.format(self.para['platform'], self.para['config'])
        self.platform = self.para['platform']
        self.config = self.para['config']
        print('target platform: {}, target config: {}'.format(self.platform, self.config))

        self.storage = precheck_function.storage_info(self.platform, self.config)
        self.primary_card_label = ''
        self.primary_card_size_current = ''
        # self.primary_storage = self.storage[0]
        # self.primary_storage_size = ''
        # self.secondary_storage_size = ''
        self.log = common_function.log()
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
            print('Failed to get size info from matrix for {} storage.'.format(pri_or_second))
            self.log.info('Failed to get size info from matrix for {} storage.'.format(pri_or_second))

    def check_image_in_primary_disk(self):
        primary_storage_size_matrix = self.get_size_matrix('primary')
        print('primary storage size from matrix: {}'.format(primary_storage_size_matrix))
        self.log.info('primary storage size from matrix: {}'.format(primary_storage_size_matrix))
        self.primary_card_label = precheck_function.primary_card_label()
        print('primary_card_label: {}'.format(self.primary_card_label))
        self.log.info('primary_card_label: {}'.format(self.primary_card_label))
        self.primary_card_size_current = precheck_function.card_size(self.primary_card_label)
        print('primary_card_size_current with bytes: {}'.format(self.primary_card_size_current[1]))
        self.log.info('primary_card_size_current with bytes: {}'.format(self.primary_card_size_current[1]))
        if self.primary_card_size_current[1][:-9] == primary_storage_size_matrix:
            print('Image installed in primary disk {}.'.format(self.primary_card_label))
            self.log.info('Image installed in primary disk {}.'.format(self.primary_card_label))
            return True
        else:
            print('Image is not installed in primary disk.')
            self.log.info('Image is not installed in primary disk.')
            return False

    def check_disk_extended(self):
        partition_size = precheck_function.partition_size(self.primary_card_label)
        pri_size_GiB = self.primary_card_size_current[0]
        partition_size_unified = self.unified_size(partition_size)
        pri_size_GiB_unified = self.unified_size(pri_size_GiB)
        if partition_size_unified == pri_size_GiB_unified:
            print('Disk is extended.')
            self.log.info('Disk is extended.')
            return True
        else:
            print('Disk is not extended. Primary disk size is {0} GiB. Partition size is {1} GiB.'
                  .format(pri_size_GiB, partition_size))
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
            print('Invalid size {}'.format(size))
            self.log.info('Invalid size {}'.format(size))


def start(case_name, **kwargs):
    common_function_tp.SwitchThinProMode(switch_to='admin')
    report1 = report.Report(case_name)
    check_storage = CheckStorage()
    primary_result = check_storage.check_image_in_primary_disk()
    if primary_result is True:
        report1.reporter('Check whether image installed in primary disk', 'Pass', 'in primary disk', 'in primary disk',
                         'none')
    elif primary_result is False:
        report1.reporter('Check whether image installed in primary disk', 'Fail', 'in primary disk', 'not in primary '
                                                                                                     'disk', 'none')
    else:
        pass
    extended_result = check_storage.check_disk_extended()
    if extended_result is True:
        report1.reporter('Check whether disk is extended', 'Pass', 'extended', 'extended', 'none')
    elif extended_result is False:
        report1.reporter('Check whether disk is extended', 'Fail', 'extended', 'not extended', 'none')
    else:
        pass
    report1.generate()


