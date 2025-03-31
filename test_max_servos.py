"""
测试 usb2.0 做为电源最大舵机数量
"""

from machine import Pin, PWM
import time

# LED指示灯
led = Pin(2, Pin.OUT)

# 舵机引脚列表
SERVO_PINS = [15, 4, 16, 17, 5, 18, 19, 21]

# 存储所有舵机的PWM对象
servos = {}


def init_servos():
    # 初始化所有舵机
    for pin in SERVO_PINS:
        try:
            pwm = PWM(Pin(pin), freq=50)
            servos[pin] = pwm
        except Exception as e:
            print(f"初始化舵机失败，引脚：{pin}，错误：{e}")


def set_angle(angle):
    # 角度限制
    angle = max(0, min(180, angle))
    # 计算占空比
    duty = int((angle / 180) * (125 - 25) + 25)

    # 同时设置所有舵机角度
    for servo in servos.values():
        servo.duty(duty)


def cleanup():
    # 释放所有PWM资源
    for servo in servos.values():
        servo.deinit()


# 初始化舵机
init_servos()

try:
    while True:
        # 设置70度
        set_angle(70)
        led.on()
        time.sleep(0.5)

        # 设置110度
        set_angle(110)
        led.off()
        time.sleep(0.5)

        print(time.time())

except KeyboardInterrupt:
    print("程序终止")
finally:
    cleanup()
