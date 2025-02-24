from machine import Pin, PWM
import time

# 定义舵机控制引脚
SERVO_PIN = 15

# 初始化 PWM 对象
pwm = PWM(Pin(SERVO_PIN), freq=50)


# 定义舵机角度转换函数
def set_angle(angle):
    # 舵机角度范围为 0 到 180 度
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180

    # 舵机的脉冲宽度范围通常为 0.5ms 到 2.5ms
    # 对应 PWM 占空比范围为 2.5% 到 12.5%
    # 这里将角度映射到占空比
    duty = int((angle / 180) * (125 - 25) + 25)
    pwm.duty(duty)


if __name__ == '__main__':

    # 舵机转到 0 度
    set_angle(0)
    time.sleep(1)

    # 舵机转到 180 度
    set_angle(180)
    time.sleep(1)

    # 舵机转到 90 度
    set_angle(90)
    time.sleep(1)
