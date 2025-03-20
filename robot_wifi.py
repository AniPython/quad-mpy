
import machine
import usocket as socket
import network
import time
import json


class RobotWifi:

    def __init__(self, robot, html_path='index.html'):
        self.robot = robot
        with open(html_path, 'r', encoding='utf-8') as file:
            self.html = file.read()

    # 创建并启动热点
    def create_connect_ap(self, essid, password, ifconfig=None):
        """AP 模式: 手机和esp32直连(不通过路由)"""
        ap = network.WLAN(network.AP_IF)
        if ifconfig:
            ap.ifconfig(ifconfig)
        ap.active(True)
        ap.config(essid=essid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)
        print('Access Point created!')
        machine.PWM(machine.Pin(2), duty=512)
        ip = ap.ifconfig()[0]
        print("ip:", ip)
        return ip

    def create_connect_route(self, ssid, password, ifconfig=None):
        """STA 模式: esp32连路由，手机连路由"""
        wlan = network.WLAN(network.STA_IF)
        if ifconfig:
            # 自定义固定的 ip 在址，否则每次连接的 ip 可能会不一样
            wlan.ifconfig(ifconfig)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(ssid, password)
            i = 1
            while not wlan.isconnected():
                print("正在链接...{}".format(i))
                i += 1
                time.sleep(1)
        ip = wlan.ifconfig()[0]
        machine.PWM(machine.Pin(2), duty=512)
        print("ip:", ip)
        return ip

    def handle_post_request(self, post_data):
        command = json.loads(post_data).get("command")
        if command:
            try:
                print(command)
                method = getattr(self.robot, command)
                method()
                return json.dumps({"status": "200", "msg": command})
            except Exception as e:
                err = "Error executing command:" + str(e)
                print(err)
                return json.dumps({"status": "500", "msg": err})

    def handle_get_request(self):
        response_headers = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
        return response_headers + self.html

    def handle_request(self, client_socket):
        request = client_socket.recv(1024)
        request_str = request.decode('utf-8')
        request_lines = request_str.split('\r\n')
        method, path, _ = request_lines[0].split()

        if method == "POST" and path == "/control":
            post_data = request_lines[-1]
            response = self.handle_post_request(post_data)

        else:
            response = self.handle_get_request()

        client_socket.send(response.encode('utf-8'))
        client_socket.close()

    # 创建HTTP服务器
    def create_server(self):
        # 创建 TCP/IP 套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置套接字选项，允许地址重用
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 绑定套接字到本地地址和端口
        server_socket.bind(('', 80))
        # 开始监听传入连接，能够同时处理的最大连接数为 128
        server_socket.listen(128)
        print('HTTP server started!')

        while True:
            # 接受一个客户端连接
            client_socket, addr = server_socket.accept()
            # 处理客户端请求
            self.handle_request(client_socket)
