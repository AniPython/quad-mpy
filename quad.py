# -- OttoDIY Python Project, 2020

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
    return (g * math.pi) / 180


class Quad:
    def __init__(self):
        self._servo_totals = 8
        self._servo = []
        for i in range(0, self._servo_totals):
            self._servo.append(oscillator.Oscillator())
        self._servo_pins = [-1] * self._servo_totals
        self._servo_trim = [0] * self._servo_totals
        self._servo_position = [90] * self._servo_totals
        self._final_time = 0
        self._partial_time = 0
        self._increment = [0] * self._servo_totals
        self._isOttoResting = True
        self._reverse = [False] * 8

    def deinit(self):
        self.detachServos()

    def init(self, FRH, FLH, FRL, FLL, BRH, BLH, BRL, BLL):
        self._servo_pins[0] = FRH
        self._servo_pins[1] = FLH
        self._servo_pins[2] = FRL
        self._servo_pins[3] = FLL
        self._servo_pins[4] = BRH
        self._servo_pins[5] = BLH
        self._servo_pins[6] = BRL
        self._servo_pins[7] = BLL

        self.attachServos()
        self.setRestState(False)

        for i in range(0, self._servo_totals):  # -- this could be eliminated as we already initialize
            self._servo_position[i] = 90  # -- the array from __init__() above ...

    # -- Attach & Detach Functions
    def attachServos(self):
        for i in range(0, self._servo_totals):
            self._servo[i].attach(self._servo_pins[i])

    def detachServos(self):
        for i in range(0, self._servo_totals):
            self._servo[i].detach()

    # -- Oscillator trims
    def setTrims(self, FRH, FLH, FRL, FLL, BRH, BLH, BRL, BLL):
        self._servo[0].SetTrim(0 if FRH is None else FRH)
        self._servo[1].SetTrim(0 if FLH is None else FLH)
        self._servo[2].SetTrim(0 if FRL is None else FRL)
        self._servo[3].SetTrim(0 if FLL is None else FLL)
        self._servo[4].SetTrim(0 if BRH is None else BRH)
        self._servo[5].SetTrim(0 if BLH is None else BLH)
        self._servo[6].SetTrim(0 if BRL is None else BRL)
        self._servo[7].SetTrim(0 if BLL is None else BLL)

    # -- Basic Motion Functions
    def _moveServos(self, period, servo_target):
        self.attachServos()
        if self.getRestState():
            self.setRestState(False)
        if period > 10:
            for i in range(0, self._servo_totals):
                self._increment[i] = ((servo_target[i]) - self._servo_position[i]) / (period / 10.0)
            self._final_time = utime.ticks_ms() + period
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

    def _moveSingle(self, position, servo_number):
        if position > 180 or position < 0:
            position = 90
        self.attachServos()
        if self.getRestState() == True:
            self.setRestState(False)
        self._servo[servo_number].SetPosition(position)
        self._servo_position[servo_number] = position

    def oscillateServos(self, amplitude, offset, period, phase, cycle=1.0):
        for i in range(0, self._servo_totals):
            self._servo[i].SetO(offset[i])
            self._servo[i].SetA(amplitude[i])
            self._servo[i].SetT(period[i])
            self._servo[i].SetPh(phase[i])

        ref = float(utime.ticks_ms())
        x = ref
        while x <= period[0] * cycle + ref:
            for i in range(0, self._servo_totals):
                self._servo[i].refresh()
            x = float(utime.ticks_ms())

    def _execute(self, amplitude, offset, period, phase, steps=1.0):

        phase_rad = [DEG2RAD(i) for i in phase]

        self.attachServos()
        if self.getRestState() == True:
            self.setRestState(False)

        # -- Execute complete cycles
        cycles = int(steps)
        if cycles >= 1:
            i = 0
            while i < cycles:
                self.oscillateServos(amplitude, offset, period, phase_rad)
                i += 1
        # -- Execute the final not complete cycle
        self.oscillateServos(amplitude, offset, period, phase_rad, float(steps - cycles))

    def getRestState(self):
        return self._isOttoResting

    def setRestState(self, state):
        self._isOttoResting = state

    def home(self):
        if self.getRestState() == False:  # -- Go to rest position only if necessary
            homes = [90] * self._servo_totals  # -- All the servos at rest position
            self._moveServos(500, homes)  # -- Move the servos in half amplitude second
            self.detachServos()
            self.setRestState(True)


    def walk(self, t=360):
        a = 16
        ao = 50
        b = 5
        c = -30
        co = 10

        step1 = [90 + 2.0 * a - ao, 90 - 4.0 * a + ao,
                 90 + c + 5 * b, 90 - c - 4 * b,
                 90 + 3.0 * a - co, 90 - 1.0 * a + co,
                 90 - c - 4 * b - 10, 90 + c + 6 * b]  # 右前(1,3)最后
        step2 = [90 + 2.3 * a - ao, 90 - 2.0 * a + ao,
                 90 + c + 5 * b, 90 - c - 0 * b,
                 90 + 3.3 * a - co, 90 - 1.3 * a + co,
                 90 - c - 4 * b - 10, 90 + c + 6 * b]  # 抬起 3
        step3 = [90 + 3.0 * a - ao, 90 - 1.0 * a + ao,
                 90 + c + 4 * b, 90 - c - 6 * b,
                 90 + 4.0 * a - co, 90 - 2.0 * a + co,
                 90 - c - 4 * b - 10, 90 + c + 5 * b]  # 左后(4,6)最后
        step4 = [90 + 3.3 * a - ao, 90 - 1.3 * a + ao,
                 90 + c + 4 * b, 90 - c - 6 * b,
                 90 + 2.0 * a - co, 90 - 2.3 * a + co,
                 90 - c - 0 * b - 10, 90 + c + 5 * b]  # 抬起 6
        step5 = [90 + 4.0 * a - ao, 90 - 2.0 * a + ao,
                 90 + c + 4 * b, 90 - c - 5 * b,
                 90 + 1.0 * a - co, 90 - 3.0 * a + co,
                 90 - c - 6 * b - 10, 90 + c + 4 * b]  # 左前(0,2)最后
        step6 = [90 + 2.0 * a - ao, 90 - 2.3 * a + ao,
                 90 + c + 0 * b, 90 - c - 5 * b,
                 90 + 1.3 * a - co, 90 - 3.3 * a + co,
                 90 - c - 6 * b - 10, 90 + c + 4 * b]  # 抬起 2
        step7 = [90 + 1.0 * a - ao, 90 - 3.0 * a + ao,
                 90 + c + 6 * b, 90 - c - 4 * b,
                 90 + 2.0 * a - co, 90 - 4.0 * a + co,
                 90 - c - 5 * b - 10, 90 + c + 4 * b]  # 右后(5,7)最后
        step8 = [90 + 1.3 * a - ao, 90 - 3.3 * a + ao,
                 90 + c + 6 * b, 90 - c - 4 * b,
                 90 + 2.3 * a - co, 90 - 2.0 * a + co,
                 90 - c - 5 * b - 10, 90 + c + 0 * b]  # 抬起 7

        self._moveServos(t, step1)
        self._moveServos(t / 3, step2)
        self._moveServos(t, step3)
        self._moveServos(t / 3, step4)
        self._moveServos(t, step5)
        self._moveServos(t / 3, step6)
        self._moveServos(t, step7)
        self._moveServos(t / 3, step8)


    def walk1(self, steps=3, t=1000, dir=FORWARD):

        self.attachServos()
        if self.getRestState() == True:
            self.setRestState(False)

        amplitude = [
            15, 15, 20, 20,
            15, 15, 20, 20,
        ]
        period = [t, t, t / 2, t / 2,
                  t, t, t / 2, t / 2]
        offset = [0, 0, 0, 0, 0, 0, 0, 0]
        phase = [
            90, 90, 270, 90,
            270, 270, 90, 270
        ]

        if dir == BACKWARD:
            phase[0] = phase[1] = 270
            phase[4] = phase[5] = 90

        for i in range(self._servo_totals):
            self._servo[i].SetO(offset[i])
            self._servo[i].SetA(amplitude[i])
            self._servo[i].SetT(period[i])
            self._servo[i].SetPh(phase[i])

        _final_time = float(utime.ticks_ms()) + period[0] * steps
        _init_time = float(utime.ticks_ms())

        while float(utime.ticks_ms()) < _final_time:
            side = int((float(utime.ticks_ms()) - _init_time) / (period[0] / 2)) % 2
            self._servo[0].refresh()
            self._servo[1].refresh()
            self._servo[4].refresh()
            self._servo[5].refresh()
            if side == 0:
                self._servo[3].refresh()
                self._servo[6].refresh()
            else:
                self._servo[2].refresh()
                self._servo[7].refresh()

            utime.sleep(0.001)

    def forward(self, steps=3, t=800):

        x_amp = 15
        z_amp = 15
        ap = 10
        hi = 15
        front_x = 6
        period = [t] * self._servo_totals
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [0 + ap - front_x,
                  0 - ap + front_x,
                  0 - hi,
                  0 + hi,
                  0 - ap - front_x,
                  0 + ap + front_x,
                  0 + hi,
                  0 - hi
                  ]
        phase = [0, 0, 90, 90,
                 180, 180, 90, 90]
        self._execute(amplitude, offset, period, phase, steps)

    def backward(self, steps=3, t=800):

        x_amp = 15
        z_amp = 15
        ap = 10
        hi = 15
        front_x = 6
        period = [t] * self._servo_totals
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [0 + ap - front_x,
                  0 - ap + front_x,
                  0 - hi,
                  0 + hi,
                  0 - ap - front_x,
                  0 + ap + front_x,
                  0 + hi,
                  0 - hi
                  ]
        phase = [180, 180, 90, 90,
                 0, 0, 90, 90]
        self._execute(amplitude, offset, period, phase, steps)

    def turn_L(self, steps=2, t=1000):
        x_amp = 15
        z_amp = 15
        ap = 5
        hi = 23
        period = [t] * self._servo_totals
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [ap, -ap, -hi, +hi, -ap, ap, hi, -hi]
        phase = [180, 0, 90, 90, 0, 180, 90, 90]

        self._execute(amplitude, offset, period, phase, steps)

    def turn_R(self, steps=2, t=1000):
        x_amp = 15
        z_amp = 15
        ap = 5
        hi = 23
        period = [t] * self._servo_totals
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [ap, -ap, -hi, +hi, -ap, ap, hi, -hi]
        phase = [0, 180, 90, 90, 180, 0, 90, 90]

        self._execute(amplitude, offset, period, phase, steps)

    def omni_walk(self, steps=2, t=1000, side=True, turn_factor=2):
        x_amp = 15
        z_amp = 15
        ap = 0
        hi = 23
        front_x = 6 * (1 - pow(turn_factor, 2))
        period = [t] * self._servo_totals
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [
            0 + ap - front_x,
            0 - ap + front_x,
            0 - hi,
            0 + hi,
            0 - ap - front_x,
            0 + ap + front_x,
            0 + hi,
            0 - hi
        ]

        phase = [0] * self._servo_totals
        if side:
            phase1 = [0, 0, 90, 90, 180, 180, 90, 90]
            phase2R = [0, 180, 90, 90, 180, 0, 90, 90]
            for i in range(self._servo_totals):
                phase[i] = phase1[i] * (1 - turn_factor) + phase2R[i] * turn_factor
        else:
            phase1 = [0, 0, 90, 90, 180, 180, 90, 90]
            phase2L = [180, 0, 90, 90, 0, 180, 90, 90]
            for i in range(self._servo_totals):
                phase[i] = phase1[i] * (1 - turn_factor) + phase2L[i] * turn_factor + self._servo[
                    i]._phase

        self._execute(amplitude, offset, period, phase, steps)

    def dance(self, steps=3, t=2000):
        x_amp = 0
        z_amp = 30
        ap = 0
        hi = 20
        period = [t] * self._servo_totals
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [ap, -ap, -hi, +hi, -ap, ap, hi, -hi]
        phase = [0, 0, 0, 270, 0, 0, 90, 180]

        self._execute(amplitude, offset, period, phase, steps)

    def front_back(self, steps=2, t=1000):
        x_amp = 30
        z_amp = 20
        ap = 15
        hi = 30
        period = [t] * self._servo_totals
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [ap, -ap, -hi, hi, -ap, ap, hi, -hi]
        phase = [0, 180, 270, 90, 0, 180, 90, 270]

        self._execute(amplitude, offset, period, phase, steps)

    def moonwalk_L(self, steps=4, t=2000):
        z_amp = 25
        o = 5
        period = [t] * self._servo_totals
        amplitude = [0, 0, z_amp, z_amp, 0, 0, z_amp, z_amp]
        offset = [0, 0, -z_amp - o, z_amp + o, 0, 0, z_amp + o, -z_amp - o]
        phase = [0, 0, 0, 80, 0, 0, 160, 290]

        self._execute(amplitude, offset, period, phase, steps)

    def up_down(self, steps=2, t=2000):
        x_amp = 0
        z_amp = 35
        ap = 10
        hi = 15
        front_x = 0
        period = [t] * self._servo_totals
        amplitude = [x_amp, x_amp, z_amp, z_amp, x_amp, x_amp, z_amp, z_amp]
        offset = [
            ap - front_x,
            -ap + front_x,
            -hi,
            hi,
            -ap - front_x,
            ap + front_x,
            hi,
            -hi
        ]
        phase = [0, 0, 90, 270, 180, 180, 270, 90]

        self._execute(amplitude, offset, period, phase, steps)

    def push_up(self, steps=2, t=2000):
        z_amp = 40
        x_amp = 45
        hi = 0
        b = 35
        period = [t] * self._servo_totals
        amplitude = [0, 0, z_amp, z_amp, 0, 0, 0, 0]
        offset = [0, 0, -hi, hi, x_amp, -x_amp, b, -b]
        phase = [0, 0, 90, -90, 0, 0, 0, 0]

        self._execute(amplitude, offset, period, phase, steps)

    def hello(self):
        self.attachServos()
        if self.getRestState():
            self.setRestState(False)

        a = 50
        b = 30
        c = 20
        d = 70
        state1 = [90 - a, 90, 90 + c, 90 - c,
                  90 + c, 90 - c, 90 - d, 90 + d]

        state2 = [90 - a, 90 + b, 90 + c, 90 + d,
                  90 + c, 90 - c, 90 - d, 90 + d]

        state3 = [90 - a, 90 - b, 90 + c, 90 + d,
                  90 + c, 90 - c, 90 - d, 90 + d]

        state4 = [90] * 8

        self._moveServos(300, state1)

        for i in range(3):
            self._moveServos(200, state2)
            self._moveServos(200, state3)

        utime.sleep_ms(300)
        self._moveServos(200, state4)

    def wave_hand(self, steps=3, t=2000):
        period = [t] * self._servo_totals
        amplitude = [20, 0, 0, 30, 0, 0, 0, 0]
        offset = [-50, 0, 20, 60, 0, 0, 0, 0]
        phase = [0] * self._servo_totals

        self._execute(amplitude, offset, period, phase, steps)

    def hide(self, steps=1.0, t=2000):
        a = 60
        b = 70
        period = [t] * self._servo_totals
        amplitude = [0, 0, 0, 0, 0, 0, 0, 0]
        offset = [-a, a, b, -b, a, -a, -b, b]
        phase = [0, 0, 0, 0, 0, 0, 0, 0]

        self._execute(amplitude, offset, period, phase, steps)

    def scared(self):
        ap = 10
        hi = 40

        sentado = [90 - 15, 90 + 15, 90 - hi, 90 + hi,  90 - 20, 90 + 20, 90 + hi, 90 - hi]
        salto = [90 - ap, 90 + ap, 160, 20, 90 + ap * 3, 90 - ap * 3, 20, 160]

        self._moveServos(600, sentado)
        self._moveServos(1000, salto)
        utime.sleep_ms(1000)


# end
if __name__ == '__main__':
    quad = Quad()
    quad.init(12, 16, 25, 18, 13, 17, 26, 19)
    quad.home()

    while True:
        quad.forward()
        utime.sleep(0.5)

