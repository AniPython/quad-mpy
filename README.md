# quad 四足机器人 micropython 代码

## 相关链接
- **本项目的 arduino-wifi 版本**: [仓库链接](https://github.com/AniPython/quad-arduino-wifi)
- **拼多多**: [商品链接](https://mobile.yangkeduo.com/goods2.html?goods_id=703833751916)
- **B站**: [视频链接](https://www.bilibili.com/video/BV1vePeepEV4/)

## `main.py` 文件中 wifi 信息修改说明

### 1. 修改 IP 配置信息
在 `main.py` 文件中，需要根据自己的路由器修改 wifi 信息。首先修改 IP 配置信息：
```python
ifconfig = ("192.168.x.182", "255.255.255.0", "192.168.x.1", "8.8.8.8")
```
将 x 值修改为与路由器一致。例如，在 Windows 系统下查看 IP 信息的步骤如下：

打开 设置 -> 网络和 Internet -> 以太网。
查看 IPv4 地址 和 IPv4 DNS 服务器。
示例：
```
IPv4地址: 192.168.2.10
IPv4 DNS 服务器: 192.168.2.1
```
那么 `main.py` 中 `ifconfig` 就应该是:
```
ifconfig = ("192.168.2.182", "255.255.255.0", "192.168.2.1", "8.8.8.8")
```
然后可以以电脑或手机上打开浏览器, 输入 `192.168.2.182` 就可以看到控制界面了

### 2. 修改成你自己的 wifi 名称和密码
```
robot_wifi.create_connect_route(ssid='wifi名称', password='wifi密码', ifconfig=ifconfig)
```
