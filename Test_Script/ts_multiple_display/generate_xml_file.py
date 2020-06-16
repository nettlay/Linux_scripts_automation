import os
import subprocess

from Common.file_operator import XMLOperator
import copy
"""
class DisplaySetting
- generate(self)
"""


class DisplaySetting:
    def __init__(self, layout, resolution, save_file='displays.xml'):
        self.save_file = save_file
        self.layout = layout
        self.resolution = resolution
        self.ports_name_list = self.check_dp_port()
        self.xml_file = self.xml_file_path()
        self.tree = XMLOperator(self.xml_file)
        self.resolution_list = []
        self.port_list = []
        self.generate_list()
        self.resolution_count = 0
        self.port_count = len(self.resolution.keys())
        self.primary = False
        self.generate_coordinate()

    @staticmethod
    def check_dp_port():
        # get all connected port
        ports_output = os.popen('xrandr -q | grep connected').readlines()
        ports_name_list = [port.split(' dis')[0].strip() for port in [ports_info_list.split('connected')[0]
                                                              for ports_info_list in ports_output]]
        print(ports_name_list)
        return ports_name_list

    def xml_file_path(self):
        if len(self.ports_name_list) > 6:
            print('Exceeded template length')
            raise FileNotFoundError
        xml_file_name = 'displays_template.xml'
        return './Test_Data/td_multiple_display/' + xml_file_name

    def generate_list(self):
        for i in self.resolution.keys():
            self.resolution_list.append(self.resolution[i][0])
            self.port_list.append(i)

    def check_ports_exist(self):
        for i in self.port_list:
            if i not in self.ports_name_list:
                return False

    # todo
    def check_monitor_number(self):
        pass

    def generate_coordinate(self):
        if 'landscape' in self.layout.lower():
            monitor_layout = self.layout.lower().split('landscape ')[-1]
            vertical, horizon = int(monitor_layout.split('x')[0]), int(monitor_layout.split('x')[1])
            print(vertical, horizon)
            self.coordinate = self.landscape_portrait_coordinate(vertical, horizon, [[0, 0]], 'Landscape')
            for i in self.coordinate:
                i.append(0)
            if self.layout.lower() == 'landscape 2x1':
                self.primary = True
        elif 'Portrait' in self.layout:
            monitor_layout = self.layout.lower().split('portrait ')[-1]
            vertical, horizon = int(monitor_layout.split('x')[0]), int(monitor_layout.split('x')[1])
            self.coordinate = self.landscape_portrait_coordinate(vertical, horizon, [[0, 0]], 'Portrait')
            for i in self.coordinate:
                i.append(90)
            if self.layout.lower() != 'portrait 2x1':
                self.primary = True
        elif 'l left' in self.layout.lower():
            self.l_left_coordinate()
        elif 'left l' in self.layout.lower():
            self.left_l_coordinate()
        elif 'mixed' in self.layout.lower() and '+' in self.layout:
            self.mixed_add()
        elif 'mixed' in self.layout.lower() and 'x' in self.layout:
            self.mixed_multiply()

    def landscape_portrait_coordinate(self, vertical, horizon, init_coordinate, rotation):
        # 3x2
        if rotation == 'Landscape':
            x, y = 0, 1
        else:
            x, y = 1, 0
        if horizon == 0:
            return []
        for i in range(vertical):
            if i == 0:
                continue
            init_coordinate.append(
                [(init_coordinate[i - 1][0] + int(self.resolution_list[self.resolution_count - 1].split('x')[x])),
                 init_coordinate[0][1]])

        self.resolution_count += 1
        return init_coordinate + self.landscape_portrait_coordinate(vertical, horizon - 1, [
            [0, init_coordinate[0][1] + int(self.resolution_list[self.resolution_count - vertical].split('x')[y])]],
                                                                    rotation)

    def l_left_coordinate(self):
        if int(self.resolution_list[1].split('x')[0]) < int(self.resolution_list[0].split('x')[-1]):
            return False
        self.coordinate = [
            [0, int(self.resolution_list[1].split('x')[0]) - int(self.resolution_list[0].split('x')[-1]), 0],
            [int(self.resolution_list[0].split('x')[0]), 0, 270]]

    def left_l_coordinate(self):
        horizon_number = self.port_count // 2 + 1
        vertical_number = self.port_count - horizon_number
        horizon_display_y = sum([int(i.split('x')[-1]) for i in self.resolution_list[horizon_number:]])
        self.coordinate = [[0, horizon_display_y, 0]]
        for i in range(1, horizon_number):
            self.coordinate.append(
                [int(self.resolution_list[i - 1].split('x')[0]) + self.coordinate[i - 1][0], horizon_display_y, 0])
        vertical_display_x, vertical_display_y = self.coordinate[-1][0], self.coordinate[-1][1]
        for i in range(vertical_number, 0, -1):
            self.coordinate.append(
                [vertical_display_x, vertical_display_y - int(self.resolution_list[self.port_count - i].split('x')[1]),
                 0])

    def mixed_add(self):
        temp_port_list = copy.deepcopy(self.port_list)
        dic = {}
        for i in self.resolution.keys():
            dic[int(self.resolution[i][0].split('x')[0])] = i
        dic_1 = dict(sorted(dic.items(), key=lambda t: t[0], reverse=True))
        dic_2 = {}
        for i in dic_1.values():
            dic_2[i] = self.resolution[i]
        self.resolution = dic_2
        self.coordinate = [[0, 0, 0], [], []]
        self.port_list.clear()
        self.resolution_list.clear()
        self.generate_list()
        for i in self.resolution.keys():
            if i == temp_port_list[0]:
                self.coordinate[self.port_list.index(i)] = [
                    int(self.resolution_list[0].split('x')[0]) - int(self.resolution[i][0].split('x')[0]),
                    int(self.resolution_list[0].split('x')[1]), 0]
                break
        count = 1
        for i in self.resolution.keys():
            if count == 1:
                count += 1
                continue
            if i != temp_port_list[0]:
                self.coordinate[self.port_list.index(i)] = [int(self.resolution_list[0].split('x')[0]), 0, 270]
                break

    def mixed_multiply(self):
        self.coordinate = [[] for i in range(len(self.port_list))]
        self.coordinate[-1] = [0, 0, 90]
        self.coordinate[0] = [int(self.resolution_list[-1].split('x')[1]), 0, 0]
        for i in range(1, len(self.port_list) - 1):
            self.coordinate[i] = [self.coordinate[i - 1][0] + int(self.resolution_list[i - 1].split('x')[0]), 0, 0]
        self.coordinate[-2][2] = 90

    def generate(self):
        count = 0
        for i in self.resolution.keys():
            self.resolution[i].append(self.coordinate[count])
            count += 1
        self.set_active_monitors()
        self.set_primary_monitor()
        self.tree.write('./Test_Data/' + self.save_file)
        return self.resolution

    def set_primary_monitor(self):
        primary_monitor_port = ''
        if self.primary:
            for i in self.resolution.keys():
                primary_monitor_port = i
        else:
            for i in self.resolution.keys():
                primary_monitor_port = i
                break
        for dp_node in self.tree.find_nodes('property/property'):
            if self.tree.get_value(dp_node, 'name') != primary_monitor_port:
                continue
            for setting_parameter in self.tree.iter(dp_node):
                if self.tree.get_value(setting_parameter, 'name') == 'Primary':
                    self.tree.set_value(setting_parameter, 'value', 'true')
                    break
            break

    def set_active_monitors(self):
        port_index = 0
        coordinate_index = 0
        for dp_node in self.tree.find_nodes('property/property'):
            if port_index == len(self.ports_name_list):
                break
            self.tree.set_value(dp_node, 'name', self.ports_name_list[port_index])
            if self.ports_name_list[port_index] in self.port_list:
                for setting_parameter in self.tree.iter(dp_node):
                    if self.tree.get_value(setting_parameter, 'name') == 'Active':
                        self.tree.set_value(setting_parameter, 'value', 'true')
                    if self.tree.get_value(setting_parameter, 'name') == 'RefreshRate':
                        self.tree.set_value(setting_parameter, 'value', '%.6f' % self.resolution[self.ports_name_list[
                            port_index]][1])
                    if self.tree.get_value(setting_parameter, 'name') == 'Resolution':
                        self.tree.set_value(setting_parameter, 'value',
                                            self.resolution[self.ports_name_list[port_index]][0])
                    if self.tree.get_value(setting_parameter, 'name') == 'Rotation':
                        self.tree.set_value(setting_parameter, 'value',
                                            str(self.resolution[self.ports_name_list[port_index]][2][2]))
                    if self.tree.get_value(setting_parameter, 'name') == 'X':
                        self.tree.set_value(setting_parameter, 'value',
                                            str(self.resolution[self.ports_name_list[port_index]][2][0]))
                    if self.tree.get_value(setting_parameter, 'name') == 'Y':
                        self.tree.set_value(setting_parameter, 'value',
                                            str(self.resolution[self.ports_name_list[port_index]][2][1]))
                        coordinate_index += 1
                        port_index += 1
            else:
                for setting_parameter in self.tree.iter(dp_node):
                    if self.tree.get_value(setting_parameter, 'name') == 'Active':
                        self.tree.set_value(setting_parameter, 'value', 'false')
                        port_index += 1
