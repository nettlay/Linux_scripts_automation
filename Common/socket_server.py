import threading
import socket
import getpass
import os
from Common.log import log

encoding = 'utf-8'
BUFSIZE = 1024


'''
Socket server will be built to an executable file and put to ftp.
'''


# A read thread, read data from remote
class Process(threading.Thread):
    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket

    def run(self):
        while True:
            data = self.client_socket.recv(BUFSIZE)
            if not data:
                log.info('No response. Close the client connection {0}.'.format(self.client_socket.getpeername()))
                # self.client_socket.sendall('No data received. Connection closed.'.encode(encoding))
                # print('socket connection disconnect')
                break
            string = bytes.decode(data, encoding)
            log.info("Content from client: {}.".format(string))
            string_list = string.split(':', 1)
            if string_list[0].strip().upper() == 'SCRIPTS':
                scripts = string_list[1].strip()
                run_result = self.run_scripts(scripts)
                if run_result is False:
                    self.client_socket.sendall('run scripts fail'.encode(encoding))
                elif len(run_result) > 0:
                    result_str = '\n'.join(run_result)
                    self.client_socket.sendall(result_str.encode(encoding))
                else:
                    self.client_socket.sendall('run scripts done with no return value'.encode(encoding))
            elif string_list[0].strip().upper() == 'GET_USER':
                user = self.get_user()
                if user:
                    self.client_socket.sendall('{}'.format(user).encode(encoding))
                else:
                    self.client_socket.sendall('get_user fail'.encode(encoding))
            elif string_list[0].strip().upper() == 'LOGOFF':
                self.log_off()
                # self.client_socket.sendall('logoff done'.encode(encoding))
            else:
                log.info('Invalid message {}.'.format(string))
                break
        self.client_socket.close()

    @staticmethod
    def get_user():
        try:
            user = getpass.getuser()
            return user
        except Exception as e:
            log.info(e)
            return False

    @staticmethod
    def log_off():
        try:
            log.info('going to logoff')
            os.system("shutdown -l")
            # time.sleep(5)
            # return True
        except Exception as e:
            log.info(e)
            # return False

    @staticmethod
    def run_scripts(scripts):
        try:
            result = os.popen(scripts).readlines()
            return result
        except Exception as e:
            log.info(e)
            return False


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
        while True:
            client_socket, client_addr = self.sock.accept()
            # print("Accept a connect from client {}.".format(client_addr[0]))
            log.info("Accept a connect from client {}.".format(client_addr))
            client_socket.sendall('Hi, I got your request. We can start to communicate.'.encode(encoding))
            Process(client_socket).start()


if __name__ == "__main__":
    listener = Listener(9011)  # Create a listen thread
    listener.start()  # then start

