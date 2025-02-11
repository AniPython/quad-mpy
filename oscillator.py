# -- MicroPython driver to Generate sinusoidal oscillations in the servos
# -- Oscillator.pde: GPL license (c) Juan Gonzalez-Gomez (Obijuan), 2011
# -- OttoDIY Python Project, 2020

import math
import time
import machine


class Servo:
    def __init__(self, freq=50, max_ang=180):
        self.freq = freq
        self.max_ang = max_ang
        self.pin = None
        self.pwm = None
        self._attached = False

    def attach(self, pin):
        self.pin = machine.Pin(pin)
        self.pwm = machine.PWM(self.pin, freq=self.freq)
        self._attached = True

    def detach(self):
        self.pwm.deinit()
        self._attached = False

    def attached(self):
        return self._attached

    def write(self, degrees):
        """Move to the specified angle in ``degrees``."""
        degrees = degrees % 360
        if degrees < 0:
            degrees += 360
        if degrees > 180:
            degrees = 180
        duty = int(degrees * 102 / 180 + 26)
        self.pwm.duty(duty)

    def __deinit__(self):
        self.pwm.deinit()


class Oscillator:
    def __init__(self, trim=0):
        # Oscillators parameters
        self._A = 0  # Amplitude (degrees)
        self._O = 0  # Offset (degrees)
        self._T = 0  # Period (ms)
        self._phase0 = 0.0  # Phase (radians)

        # Internal variables
        self._servo = Servo()  # Servo that is attached to the oscillator
        self._pos = 0  # Current servo pos
        self._trim = trim  # Calibration offset
        self._phase = 0.0  # Current phase
        self._inc = 0.0  # Increment of phase
        self._N = 0.0  # Number of samples
        self._TS = 0  # sampling period (ms)
        self._previousMillis = 0
        self._currentMillis = 0
        self._stop = True  # Oscillation mode. If true, the servo is stopped
        self._rev = False  # Reverse mode

    # -- Attach an oscillator to a servo
    # -- Input: pin is the pin were the servo is connected
    def attach(self, pin, rev=False):
        if not self._servo.attached():  # -- If the oscillator is detached,
            self._servo.attach(pin)  # -- Attach the servo and move it to the home position
            self._servo.write(90 + self._trim)

            # -- Initialization of oscilaltor parameters
            self._TS = 30
            self._T = 2000
            self._N = self._T / self._TS
            self._inc = 2 * math.pi / self._N
            self._previousMillis = 0

            # -- Default parameters
            self._A = 45
            self._phase = 0
            self._phase0 = 0
            self._O = 0
            self._stop = False

            # -- Reverse mode
            self._rev = rev

    # -- Detach an oscillator from his servo
    def detach(self):
        if self._servo.attached():  # -- If the oscillator is attached,
            self._servo.detach()

    # --  Set the oscillator Amplitude (degrees)
    def SetA(self, A):
        self._A = A

    # -- Set the oscillator Offset (degrees)
    def SetO(self, O):
        self._O = O

    # -- Set the oscillator Phase (radians)
    def SetPh(self, Ph):
        self._phase0 = Ph

    # -- Set the oscillator period, ms
    def SetT(self, T):
        self._T = T  # -- Assign the period
        self._N = self._T / self._TS  # -- Recalculate the parameters
        self._inc = 2 * math.pi / self._N

    # -- Manual set of the position
    def SetPosition(self, position):
        self._servo.write(position + self._trim)

    # -- SetTrim
    def SetTrim(self, trim):
        self._trim = trim

    # -- getTrim
    def getTrim(self):
        return self._trim

    # -- Stop
    def Stop(self):
        self._stop = True

    # -- Play
    def Play(self):
        self._stop = False

    # -- Reset
    def Reset(self):
        self._phase = 0

    # -- should be taken (i.e. the TS time has passed since
    # -- the last sample was taken
    def __next_sample(self):
        self._currentMillis = time.ticks_ms()  # -- Read current time
        if self._currentMillis - self._previousMillis > self._TS:
            self._previousMillis = self._currentMillis;
            return True
        return False

    """
    This function should be periodically called
    in order to maintain the oscillations. It calculates
    if another sample should be taken and position the servo if so
    """

    def refresh(self):
        if self.__next_sample():  # -- Only When TS milliseconds have passed, sample is obtained
            if not self._stop:  # -- If the oscillator is not stopped, the servo position
                self._pos = round(self._A * math.sin(
                    self._phase + self._phase0) + self._O)  # -- Sample the sine function and set the servo pos
                if self._rev:
                    self._pos = -self._pos
                self._servo.write(self._pos + 90 + self._trim)

            # -- Increment the phase
            # -- It is always increased, when the oscillator is stop
            # -- so that the coordination is always kept
            self._phase = self._phase + self._inc


if __name__ == '__main__':
    # 振荡器
    os = Oscillator()
    os.attach(pin=25)

    # (参考)正弦函数公式: y = A⋅sin(2πx/T + Ph) + O

    # A（Amplitude）：振幅(角度 degrees -90~90)，它决定了舵机摆动的幅度。
    os.SetA(A=20)

    # O（Offset）：偏移量(角度 degrees -90~90)，y轴偏移值, 它可以用来设置舵机的初始位置。
    os.SetO(O=10)

    # T（Period）：周期(毫秒 ms)，振荡器一个完整周期的时间长度
    os.SetT(T=1000)

    # Ph（Phase）：相位(弧度 radians 0~2π)，x轴偏移值
    os.SetPh(Ph=0)

    while True:
        os.refresh()
