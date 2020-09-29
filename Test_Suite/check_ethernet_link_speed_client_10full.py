# case_name: check_ethernet_link_speed_when_client_side_set_to_10full_and_switch_set_to_auto
# nick.lu

from Test_Suite import check_ethernet_link_speed_client_auto as auto


def start(case_name, **kwargs):
    if auto.start(case_name, ethernet_speed="10/Full", speed="10Mb/s", duplex="Full", auto_negotiation="off"):
        return True
    else:
        return False
