from Common.log import *
from Common import common_function as cf
import subprocess


def start(case_name, **kwargs):
    # report_file = os.path.join(cf.get_current_dir(), "Test_Report", "{}.yaml".format(cf.check_ip_yaml()))
    # cf.new_cases_result(report_file, case_name)
    base_name = cf.get_report_base_name()
    report_file = get_current_dir('Test_Report', base_name)
    cf.new_cases_result(report_file, case_name)  # new report

    log.info("{:-^80}".format("start a case test"))
    log.info("case name:" + case_name)
    """Get the image_id and sp in the yaml file"""
    t = cf.load_global_parameters()
    image_id = t.get("image_id")
    sp = t.get("sp")
    """Get the system version number"""
    version_id = subprocess.getoutput("cat /etc/imageid")
    version = subprocess.getoutput("dpkg -l | grep hptc-sp-thinpro.*-sp")
    if not version:
        log.info("version number is a empty")
        version_number = ''
    else:
        version_number ="".join(subprocess.getoutput("dpkg -l | grep hptc-sp-thinpro.*-sp").replace(" ","").split("-")[3][0:6].split("."))[2:]
    if image_id.upper() == version_id.upper() and sp == version_number:
        log.info("version_id and version_number are the same as image_id and sp")
        report = {'result': 'Pass',
                  'expect': "version_id and version_number are the same as image_id and sp",
                  'actual': "version_id {0} and version_number {1} are the same as image_id {2} and sp {3}".format(
                      version_id, version_number, image_id, sp),
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        return True
    else:
        log.error("version_id and version_number are different from  image_id and sp")
        report = {'result': 'Fail',
                  'expect': "version_id and version_number are different from image_id and sp",
                  'actual': "version_id {0} and version_number {1} are different from image_id {2} and sp {3}".format(
                      version_id, version_number, image_id, sp),
                  'note': ''}
        cf.update_cases_result(report_file, case_name, report)
        return False
