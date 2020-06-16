import socket
import time


class SocketClient:

    def __init__(self, host_ip, host_port):
        self.sock = socket.socket()
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # self.sock.settimeout(20)  # 20 seconds
        try:
            self.sock.connect((host_ip, host_port))
            print("Socket client: connect success.")
            response = self.sock.recv(1024)
            print('Response from server:', response.decode('utf-8'))
        except socket.error as e:
            print("Socket Connect Error: {}".format(str(e)))

    def request(self, message):
        try:
            if message == 'break':
                print('Break request got. Socket connection {} is going to close.'.format(self.sock.getsockname()))
                self.sock.close()
                return False  # to be modified
            else:
                self.sock.sendall(message.encode("utf-8"))
                while True:
                    time_flag = 0
                    data = self.sock.recv(1024)
                    if len(data) > 0:
                        recv_data = data.decode('utf-8')
                        print('Response from server after sending message:', recv_data)
                        return recv_data.strip()
                    else:
                        time_flag += 1
                        continue
                    if time_flag > 20:
                        print('No response from server after sending message for more than 20s.')
                        return False
        except socket.error as e:
            print('Socket running error: {}'.format(str(e)))


if __name__ == "__main__":
    socket_client = SocketClient('127.0.0.1', 9011)
    # socket_client = socket_client.SocketClient('192.168.1.118', 9011)
    while True:
        request_type = input('What request do you want?\n 1. get user\n 2. logoff\n 3. break\n '
                             'Please choose the number:\n')
        if request_type == '3':
            message = 'break'
            response = socket_client.request(message)
            print('\nRequest finished, you can do the next testing step.\n', response)
            break
        elif str(request_type) == '1':
            message = 'get_user'
            response = socket_client.request(message)
            print(response)
        elif str(request_type) == '2':
            message = 'logoff'
            response = socket_client.request(message)
            print(response)
        time.sleep(1)
