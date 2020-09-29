import yaml
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class XMLOperator:
    def __init__(self, file_path):
        self.tree = ET.parse(file_path)

    def get_root(self):
        return self.tree.getroot()

    def find_nodes(self, path):
        return self.tree.findall(path)

    @staticmethod
    def attrib(node):
        return node.attrib

    @staticmethod
    def tag(node):
        return node.tag

    def write(self, file_path):
        self.tree.write(file_path)

    @staticmethod
    def get_value(node, name):
        return node.attrib[name]

    @staticmethod
    def set_value(node, name, value):
        node.set(name, value)

    @staticmethod
    def iter(node):
        return node.iter()


class YamlOperator:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        f = open(self.file_path, 'r')
        return yaml.safe_load(f)

    def write(self, content):
        with open(self.file_path, 'w')as f1:
            yaml.safe_dump(content, f1)

