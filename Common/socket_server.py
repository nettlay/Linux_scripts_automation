import threading
import socket
import getpass
import time
import os, re
from Common.log import log
from Common.common_function import get_current_dir
from Common.file_operator import YamlOperator
from Common.file_transfer import FTPUtils

encoding = 'utf-8'
BUFSIZE = 1024

'''
Socket server will be built to an executable file and put to ftp.
'''

User_List = ["autotest" + "{}".format(i + 1) for i in range(5)]


class MultiUserManger:
    def __init__(self):
        self.download_base_file = 'download_temp.txt'
        self.file_path = get_current_dir("Test_Data/td_multiple_display/{}".format(self.download_base_file))

    @property
    def remote_base_file(self):
        path = "//15.83.248.197/ftproot/Files/multiple_display/user_list.yml"
        tree = path.split('/')
        remote_file = '/'.join(tree[4:])
        return remote_file

    @property
    def ftp(self):
        ip = "15.83.248.197"
        user = "Administrator"
        pwd = "Shanghai2020"
        ftp_obj = FTPUtils(ip, user, pwd)
        return ftp_obj

    def get_a_available_key(self, key="user", available="available"):
        self.ftp.download_file(self.remote_base_file, self.file_path)
        yaml_obj = YamlOperator(self.file_path)
        total_users = yaml_obj.read().get(key, {})
        for k, v in total_users.items():
            if v.lower() in available:
                dic_key = k
                break
        else:
            dic_key = ''
        if dic_key:
            self.lock_key(dic_key, key)
        else:
            log.info('no available user could be assigned')
        return dic_key

    def get_a_specify_value(self, key="user", **other_keys):
        self.ftp.download_file(self.remote_base_file, self.file_path)
        yaml_obj = YamlOperator(self.file_path)
        total_users = yaml_obj.read()
        value = total_users.get(key, {})
        key_list = other_keys.values()
        for i in key_list:
            value = value.get(i, "")
            if not isinstance(value, dict):
                break
        return value

    def change_key_state(self, user_name, state, key="user"):
        self.ftp.download_file(self.remote_base_file, self.file_path)
        time.sleep(2)
        yaml_obj = YamlOperator(self.file_path)
        total_users = yaml_obj.read()
        value = total_users.get(key).get(user_name)
        if value:
            total_users[key][user_name] = state
            yaml_obj.write(total_users)
            self.ftp.upload_file(self.file_path, self.remote_base_file)
        else:
            log.error('invalid user {}'.format(user_name))
            return False
        return True

    def reset_key(self, user_name, key="user"):
        return self.change_key_state(user_name, 'available', key)

    def lock_key(self, user_name, key="user"):
        return self.change_key_state(user_name, 'busy', key)


user_manager = MultiUserManger()


# A read thread, read data from remote
class Process(threading.Thread):
    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.client_socket: socket.socket = client_socket
        self.user = self.get_user().lower()
        if self.user in User_List:
            ip = self.client_socket.getsockname()[0]
            try:
                user_manager.change_key_state(self.user, ip)
            except Exception as e:
                log.error("change key {} fail {} : {}".format(self.user, ip, e))

    def run(self):
        while True:
            data = self.client_socket.recv(BUFSIZE)
            print(data, "[socket server][run]data")
            if not data:
                log.info('[socket server][run]No response. Close the client connection {0}.'.format(self.client_socket.getpeername()))
                # self.client_socket.sendall('No data received. Connection closed.'.encode(encoding))
                # print('socket connection disconnect')
                break
            string = bytes.decode(data, encoding).strip()
            log.info("[socket server][run]Content from client: {}.".format(string))
            if string.upper() == 'GET_USER':
                user = self.get_user()
                if user:
                    self.client_socket.sendall('{}'.format(user).encode(encoding))
                else:
                    self.client_socket.sendall('[socket server][run]get_user fail'.encode(encoding))
            elif string.upper() == 'LOGOFF':
                logoff = self.log_off()
                if logoff:
                    self.client_socket.sendall('[socket server][run]logoff done'.encode(encoding))
                else:
                    self.client_socket.sendall('[socket server][run]logoff fail'.encode(encoding))
            elif 'WAKEUP' in string.upper():
                # wakeup mac time(s)
                log.info("[socket server][run]Send 'Accept {}'".format(string))
                self.client_socket.sendall('Accept {}'.format(string).encode(encoding))
                info = string.split(" ")[1:]
                log.info("[socket server][run]start wakeup {}".format(" ".join(info)))
                self.wake_up(*info)
            elif string.upper() == 'GETINFO':
                info = self.get_info()
                if info:
                    self.client_socket.sendall('{}'.format(info).encode(encoding))
                else:
                    self.client_socket.sendall('[socket server][run]get_info fail'.encode(encoding))
            else:
                log.error('[socket server][run]Invalid message {}.'.format(string))
                break
        self.client_socket.close()

    @staticmethod
    def get_user():
        try:
            user = getpass.getuser()
            return user
        except Exception as e:
            log.error("[socket server][get_user]Error while getting user: {}".format(e))
            return ""

    @staticmethod
    def log_off():
        try:
            os.system("shutdown -l")
            print('logoff')
            time.sleep(5)
            return True
        except Exception as e:
            log.error("[socket server][log_off]Error while logging off: {}".format(e))
            return False

    @staticmethod
    def wake_up(mac, *args):
        try:
            tool_path = r".\wol.exe"
            time.sleep(int(args[0]))
            for i in range(8):
                time.sleep(1)
                log.info("Send: {} {}".format(tool_path, mac))
                os.system("{} {}".format(tool_path, mac))
            return True
        except Exception as e:
            log.error(e)
            log.error("[socket server][wake_up]Wakeup fail")
            return True

    @staticmethod
    def get_info():
        """
        get wol server ip, mac, gateway
        :return: tuple
        """
        res = os.popen("ipconfig /all").read()
        print(res)
        res = re.findall(
            r"(?i): (.{2}-.{2}-.{2}-.{2}-.{2}-.{2}).{0,250}?ipv4.{0,100}?(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}).{0,250}?"
            r"gateway.{0,100}?(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3})",
            res,
            re.S)
        print(res)
        assert res != [], "[socket server][get_info]Can't get a usable information"
        return res[0]


# A listen thread, listen remote connect
# When a remote machine request to connect, it will create a Process thread to handle
class Listener(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # self.sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 5*1000, 2*1000))
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen(0)

    def run(self):
        log.info("Socket server Listener started.")
        try:
            while True:
                client_socket, client_addr = self.sock.accept()
                # print("Accept a connect from client {}.".format(client_addr[0]))
                log.info("Accept a connect from client {}.".format(client_addr))
                client_socket.sendall('Hi, I got your request. We can start to communicate.'.encode(encoding))
                Process(client_socket).start()
        except Exception as e:
            log.error(e)
            log.error("socket client error, and break")


if __name__ == "__main__":
    listener = Listener(9011)  # Create a listen thread
    listener.start()  # then start


