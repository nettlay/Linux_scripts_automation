import subprocess


# get country id of the build id in the thinpro
def sys_build_id():
    # build_id = subprocess.getoutput("dmidecode | grep -i BUILDID")
    n = subprocess.getoutput("dmidecode | grep -n BUILDID | awk -F: '{print $1}'")
    output = subprocess.getoutput("dmidecode | sed -n '{}, {}p'".format(n, str(int(n) + 1)))
    country_id = output.split("#")[-1]
    if 'String 2' in country_id:
        country_id = country_id.replace('String 2:', '').replace('\n', '').replace('\t', '').replace(' ', '')[1:4]
    else:
        country_id = country_id[1:4]
    return country_id

