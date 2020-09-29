import socket
import time
from Common.log import log


class SocketClient:

    def __init__(self, host_ip, host_port):
        self.sock = socket.socket()
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # self.sock.settimeout(20)  # 20 seconds
        self.log = log
        self.log.info('Host to be connected: {}, {}'.format(host_ip, host_port))
        try:
            self.sock.connect((host_ip, host_port))
            self.log.info("Socket client: connect success.")
            response = self.sock.recv(1024)
            self.log.info('Response from server: {}'.format(response.decode('utf-8')))
        except socket.error as e:
            self.log.info("Socket Connect Error: {}".format(str(e)))

    def request(self, message):
        try:
            if message == 'break':
                self.log.info('Break request got. Socket connection {} '
                              'is going to close.'.format(self.sock.getsockname()))
                self.sock.close()
                return False  # to be modified
            else:
                self.sock.sendall(message.encode("utf-8"))
                time_flag = 0
                while True:
                    # data = self.sock.recv(1024)
                    data = self.sock.recv(2048)
                    if len(data) > 0:
                        recv_data = data.decode('utf-8')
                        self.log.info('Response from server after sending message: {}'.format(recv_data))
                        return recv_data.strip()
                    else:
                        time.sleep(1)
                        time_flag += 1
                        # continue
                    if time_flag >= 20:
                        self.log.info('No response from server after'
                                      ' sending message for more than {}s.'.format(time_flag))
                        return False
        except socket.error as e:
            self.log.info('Socket running error: {}'.format(str(e)))
            return ""


if __name__ == "__main__":
    client = SocketClient('127.0.0.1', 9011)
    time.sleep(3)
    user = client.request('get_user')
    print(user)
    # time.sleep(3)
    # client.request('logoff')
    result = client.request('scripts: dir c:\\lena')
    # result = client.request('scripts: dir c:\\')
    print(result)
