"""
舵机与 esp32 引脚接线图, 数据口方向为后 (tail)

    前 (head)
        -----               -----
        |  2  |             |  3  |
        |pin25|             |Pin18|
        ----- -----   ----- -----
            |  0  | |  1  |
            |Pin12| |Pin16|
             -----   -----
            |  4  | |  5  |
            |Pin13| |Pin17|
        ----- -----   ----- -----
        |  6  |             |  7  |
        |Pin26|             |Pin19|
        -----               -----
    后 (tail)
"""


from quad import Quad
from robot_wifi import RobotWifi

ifconfig = ("192.168.2.182", "255.255.255.0", "192.168.2.1", "8.8.8.8")

robot = Quad()
robot.init(12, 16, 25, 18, 13, 17, 26, 19)
robot.setTrims(0, 0, 0, 0, 0, 0, 0, 0)

robot_wifi = RobotWifi(robot=robot)

# AP模式(没有路由使用这种模式, 这时候 esp32 变成了一个热点, 手机或电脑连接这个热点, 即可控制机器人)
# robot_wifi.create_connect_ap(essid="Otto", password="88889999", ifconfig=ifconfig)

# 路由模式(局域网内的手机或电脑都可以通过 wifi 控制机器人)
robot_wifi.create_connect_route(ssid='小亦站', password='88889999', ifconfig=ifconfig)

robot_wifi.create_server()
