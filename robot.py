
from micropython import const
import oscillator, utime, math

# -- Constants
FORWARD = const(1)
BACKWARD = const(-1)
LEFT = const(1)
RIGHT = const(-1)
SMALL = const(5)
MEDIUM = const(15)
BIG = const(30)


def DEG2RAD(g):
    """角度转弧度"""
    return (g * math.pi) / 180


class Robot:
    def __init__(self, servo_totals):
        self._servo_totals = servo_totals
        self._servo = [oscillator.Oscillator() for _ in range(self._servo_totals)]
        self._servo_pins = [-1] * self._servo_totals
        self._servo_trim = [0] * self._servo_totals
        self._servo_position = [90] * self._servo_totals
        self._final_time = 0
        self._partial_time = 0
        self._increment = [0] * self._servo_totals
        self._isResting = True

    def init(self, *args, **kwargs):
        raise NotImplementedError

    def setTrims(self, *args, **kwargs):
        raise NotImplementedError

    def attachServos(self):
        for i in range(0, self._servo_totals):
            self._servo[i].attach(self._servo_pins[i])

    def deinit(self):
        self.detachServos()

    def detachServos(self):
        for i in range(0, self._servo_totals):
            self._servo[i].detach()

    def getRestState(self):
        return self._isResting

    def setRestState(self, state):
        self._isResting = state

    def moveServos(self, T, servo_target):
        self.attachServos()
        if self.getRestState():
            self.setRestState(False)
        if T > 10:
            for i in range(0, self._servo_totals):
                self._increment[i] = ((servo_target[i]) - self._servo_position[i]) / (T / 10.0)
            self._final_time = utime.ticks_ms() + T
            iteration = 1
            while utime.ticks_ms() < self._final_time:
                self._partial_time = utime.ticks_ms() + 10
                for i in range(0, self._servo_totals):
                    self._servo[i].SetPosition(int(self._servo_position[i] + (iteration * self._increment[i])))
                while utime.ticks_ms() < self._partial_time:
                    pass  # pause
                iteration += 1
        else:
            for i in range(0, self._servo_totals):
                self._servo[i].SetPosition(servo_target[i])
        for i in range(0, self._servo_totals):
            self._servo_position[i] = servo_target[i]

    def oscillateServos(self, A, O, T, phase_diff, cycle=1.0):
        for i in range(0, self._servo_totals):
            self._servo[i].SetO(O[i])
            self._servo[i].SetA(A[i])
            self._servo[i].SetT(T)
            self._servo[i].SetPh(phase_diff[i])

        ref = float(utime.ticks_ms())
        x = ref
        while x <= T * cycle + ref:
            for i in range(0, self._servo_totals):
                self._servo[i].refresh()
            x = float(utime.ticks_ms())

    def execute(self, A, O, T, phase_diff, steps=1.0):
        self.attachServos()
        if self.getRestState() == True:
            self.setRestState(False)

        # -- Execute complete cycles
        cycles = int(steps)
        if cycles >= 1:
            i = 0
            while i < cycles:
                self.oscillateServos(A, O, T, phase_diff)
                i += 1
        # -- Execute the final not complete cycle
        self.oscillateServos(A, O, T, phase_diff, float(steps - cycles))
