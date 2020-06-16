import subprocess


# get country id of the build id in the thinpro
def sys_build_id():
    build_id = subprocess.getoutput("dmidecode | grep -i BUILDID")
    country_id = build_id.split("#")[-1][1:4]
    return country_id

