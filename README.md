# quad-mpy
四足机器人 micropython 代码

拼多多: https://mobile.yangkeduo.com/goods2.html?goods_id=703833751916  

B站: https://www.bilibili.com/video/BV1vePeepEV4/


#### `main.py` 文件中, 需要根据自己的路由器修改 wifi 信息

1. 首先修改 wifi 信息
```
ifconfig = ("192.168.x.182", "255.255.255.0", "192.168.x.1", "8.8.8.8")
```
修改 x 值与路由器一致, 例如在 windows 下查看:   
设置->网络和Internet->以太网->IPv4地址/IPv4 DNS 服务器
比如我在电脑到的是:
```
IPv4地址: 192.168.2.10
IPv4 DNS 服务器: 192.168.2.1
```
那么 `main.py` 中 ifconfig 就应该是:
```
ifconfig = ("192.168.2.182", "255.255.255.0", "192.168.2.1", "8.8.8.8")
```
然后可以以电脑或手机上打开浏览器, 输入: `192.168.2.182` 就可以看到控制界面了

2. 修改成你自己的 wifi 名称和密码
```
robot_wifi.create_connect_route(ssid='名称', password='密码', ifconfig=ifconfig)
```