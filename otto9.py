
from robot import *
import utime


class Otto9(Robot):
    def __init__(self, servo_totals):
        super().__init__(servo_totals)

    def init(self, YL, YR, RL, RR):
        self._servo_pins[0] = YL
        self._servo_pins[1] = YR
        self._servo_pins[2] = RL
        self._servo_pins[3] = RR

        self.attachServos()
        self.setRestState(False)

    def setTrims(self, YL, YR, RL, RR):
        self._servo[0].SetTrim(YL)
        self._servo[1].SetTrim(YR)
        self._servo[2].SetTrim(RL)
        self._servo[3].SetTrim(RR)

    def home(self):
        if self.getRestState() == False:  # -- Go to rest position only if necessary
            homes = [90, 90, 90, 90]  # -- All the servos at rest position
            self.moveServos(500, homes)  # -- Move the servos in half a second
            self.detachServos()
            self.setRestState(True)

    def walk(self, steps=3, T=1000, dir=BACKWARD):
        # -- Oscillator parameters for walking
        # -- Hip sevos are in phase
        # -- Feet servos are in phase
        # -- Hip and feet are 90 degrees out of phase
        # --      -90 : Walk forward
        # --       90 : Walk backward
        # -- Feet servos also have the same offset (for tiptoe a little bit)
        A = [30, 30, 20, 20]
        O = [0, 0, 0, 0]
        phase_diff = [0, 0, DEG2RAD(dir * -90), DEG2RAD(dir * -90)]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)


    # -- Otto movement: Jump
    # --  Parameters:
    # --    steps: Number of steps
    # --    T: Period
    def jump(self, steps=2, T=300):
        up = [90, 90, 160, 20]
        down = [90, 90, 90, 90]
        self.moveServos(T, up)
        self.moveServos(T, down)

    # -- Otto gait: Walking  (forward or backward)
    # --  Parameters:
    # --    * steps:  Number of steps
    # --    * T : Period
    # --    * Dir: Direction: FORWARD / BACKWARD
    def walk(self, steps=3, T=1000, dir=BACKWARD):
        # -- Oscillator parameters for walking
        # -- Hip sevos are in phase
        # -- Feet servos are in phase
        # -- Hip and feet are 90 degrees out of phase
        # --      -90 : Walk forward
        # --       90 : Walk backward
        # -- Feet servos also have the same offset (for tiptoe a little bit)
        A = [30, 30, 30, 30]
        O = [0, 0, 0, 0]
        phase_diff = [0, 0, DEG2RAD(dir * -90), DEG2RAD(dir * -90)]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    def forward(self, steps=3, T=1000, dir=FORWARD):
        self.walk(steps=steps, T=T, dir=dir)

    def backward(self, steps=3, T=1000, dir=BACKWARD):
        self.walk(steps=steps, T=T, dir=dir)

    # -- Otto gait: Turning (left or right)
    # --  Parameters:
    # --   * Steps: Number of steps
    # --   * T: Period
    # --   * Dir: Direction: LEFT / RIGHT
    def turn(self, steps, T, dir):
        # -- Same coordination than for walking (see Otto.walk)
        # -- The Amplitudes of the hip's oscillators are not igual
        # -- When the right hip servo amplitude is higher, steps taken by
        # -- the right leg are bigger than the left. So, robot describes an left arc
        A = [30, 30, 30, 30]
        O = [0, 0, 0, 0]
        phase_diff = [0, 0, DEG2RAD(-90), DEG2RAD(-90)]
        if dir == LEFT:
            A[0] = 30  # -- Left hip servo
            A[1] = 10  # -- Right hip servo
        else:
            A[0] = 10
            A[1] = 30

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    def turn_left(self, steps=2, T=1000, dir=LEFT):
        self.turn(steps=steps, T=T, dir=dir)

    def turn_right(self, steps=2, T=1000, dir=RIGHT):
        self.turn(steps=steps, T=T, dir=dir)

    # -- Otto gait: Lateral bend
    # --  Parameters:
    # --    steps: Number of bends
    # --    T: Period of one bend
    # --    dir: RIGHT=Right bend LEFT=Left bend
    def bend(self, steps, T, dir):
        # -- Parameters of all the movements. Default: Left bend
        bend1 = [90, 90, 40, 35]
        bend2 = [90, 90, 40, 105]
        homes = [90, 90, 90, 90]

        # -- Time of one bend, in order to avoid movements too fast.
        # T = max(T, 600)

        # -- Changes in the parameters if right direction is chosen
        if dir == RIGHT:
            bend1[2] = 180 - 50
            bend1[3] = 180 - 80  # -- Not 65. Otto is unbalanced
            bend2[2] = 180 - 105
            bend2[3] = 180 - 60

        # -- Time of the bend movement. Fixed parameter to avoid falls
        T2 = 800

        # -- Bend movement
        i = 0
        while i < steps:
            self.moveServos(T2 / 2, bend1)
            self.moveServos(T2 / 2, bend2)
            utime.sleep_ms(int((T * 0.8)))
            self.moveServos(500, homes)
            i += 1

    def bend_left(self, steps=1, T=1000, dir=LEFT):
        self.bend(steps=steps, T=T, dir=dir)

    def bend_right(self, steps=1, T=1000, dir=RIGHT):
        self.bend(steps=steps, T=T, dir=dir)

    # -- Otto gait: Shake a leg
    # --  Parameters:
    # --    steps: Number of shakes
    # --    T: Period of one shake
    # --    dir: RIGHT=Right leg LEFT=Left leg
    def shake_leg(self, steps, T, dir):
        # -- This variable change the amount of shakes
        numberLegMoves = 2

        # -- Parameters of all the movements. Default: Right leg
        shake_leg1 = [90, 90, 40, 35]
        shake_leg2 = [90, 90, 40, 120]
        # shake_leg3 = [90, 90, 70, 60]
        shake_leg3 = [90, 90, 40, 60]
        homes = [90, 90, 90, 90]

        # -- Changes in the parameters if right leg is chosen
        if dir == RIGHT:
            shake_leg1[2] = 180 - 15
            shake_leg1[3] = 180 - 40
            shake_leg2[2] = 180 - 120
            shake_leg2[3] = 180 - 58
            shake_leg3[2] = 180 - 60
            shake_leg3[3] = 180 - 58

        # -- Time of the bend movement. Fixed parameter to avoid falls
        T2 = 1000

        # -- Time of one shake, in order to avoid movements too fast.
        T = T - T2
        T = max(T, 200 * numberLegMoves)

        j = 0
        while j < steps:
            # -- Bend movement
            self.moveServos(T2 / 2, shake_leg1)
            self.moveServos(T2 / 2, shake_leg2)

            # -- Shake movement
            i = 0
            while i < numberLegMoves:
                self.moveServos(T / (2 * numberLegMoves), shake_leg3)
                self.moveServos(T / (2 * numberLegMoves), shake_leg2)
                self.moveServos(500, homes)  # -- Return to home position
                i += 1
            j += 1
        utime.sleep_ms(T)

    def shake_leg_left(self, steps=1, T=1500, dir=LEFT):
        self.shake_leg(steps=steps, T=T, dir=dir)

    def shake_leg_right(self, steps=1, T=1500, dir=RIGHT):
        self.shake_leg(steps=steps, T=T, dir=dir)

    # -- Otto movement: up & down
    # --  Parameters:
    # --    * steps: Number of jumps
    # --    * T: Period
    # --    * h: Jump height: SMALL / MEDIUM / BIG
    # --              (or a number in degrees 0 - 90)
    def updown(self, steps=2, T=1500, h=30):
        # -- Both feet are 180 degrees out of phase
        # -- Feet amplitude and offset are the same
        # -- Initial phase for the right foot is -90, that it starts
        # --   in one extreme position (not in the middle)
        A = [0, 0, h, h]
        O = [0, 0, h, -h]
        phase_diff = [0, 0, DEG2RAD(-90), DEG2RAD(90)]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    # -- Otto movement: swinging side to side
    # --  Parameters:
    # --     steps: Number of steps
    # --     T : Period
    # --     h : Amount of swing (from 0 to 50 aprox)
    def swing(self, steps=2, T=1000, h=30):
        # -- Both feets are in phase. The offset is half the amplitude
        # -- It causes the robot to swing from side to side
        A = [0, 0, h, h]
        O = [0, 0, h / 2, -h / 2]
        phase_diff = [0, 0, DEG2RAD(0), DEG2RAD(0)]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    # -- Otto movement: swinging side to side without touching the floor with the heel
    # --  Parameters:
    # --     steps: Number of steps
    # --     T : Period
    # --     h : Amount of swing (from 0 to 50 aprox)
    def tiptoeSwing(self, steps=2, T=1000, h=30):
        # -- Both feets are in phase. The offset is not half the amplitude in order to tiptoe
        # -- It causes the robot to swing from side to side
        A = [0, 0, h, h]
        O = [0, 0, h, -h]
        phase_diff = [0, 0, 0, 0]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    # -- Otto gait: Jitter
    # --  Parameters:
    # --    steps: Number of jitters
    # --    T: Period of one jitter
    # --    h: height (Values between 5 - 25)
    def jitter(self, steps=2, T=1000, h=30):
        # -- Both feet are 180 degrees out of phase
        # -- Feet amplitude and offset are the same
        # -- Initial phase for the right foot is -90, that it starts
        # --   in one extreme position (not in the middle)
        # -- h is constrained to avoid hit the feets
        h = min(25, h)
        A = [h, h, 0, 0]
        O = [0, 0, 0, 0]
        phase_diff = [DEG2RAD(-90), DEG2RAD(90), 0, 0]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    # -- Otto gait: Ascending & turn (Jitter while up&down)
    # --  Parameters:
    # --    steps: Number of bends
    # --    T: Period of one bend
    # --    h: height (Values between 5 - 15)
    def ascendingTurn(self, steps=2, T=1000, h=50):
        # -- Both feet and legs are 180 degrees out of phase
        # -- Initial phase for the right foot is -90, that it starts
        # --   in one extreme position (not in the middle)
        # -- h is constrained to avoid hit the feets
        h = min(23, h)
        A = [h, h, h, h]
        O = [0, 0, h + 4, -h + 4]
        phase_diff = [DEG2RAD(-90), DEG2RAD(90), DEG2RAD(-90), DEG2RAD(90)]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    # -- Otto gait: Moonwalker. Otto moves like Michael Jackson
    # --  Parameters:
    # --    Steps: Number of steps
    # --    T: Period
    # --    h: Height. Typical valures between 15 and 40
    # --    dir: Direction: LEFT / RIGHT
    def moonwalker(self, steps, T, h, dir):
        # -- This motion is similar to that of the caterpillar robots: A travelling
        # -- wave moving from one side to another
        # -- The two Otto's feet are equivalent to a minimal configuration. It is known
        # -- that 2 servos can move like a worm if they are 120 degrees out of phase
        # -- In the example of Otto, two feet are mirrored so that we have:
        # --    180 - 120 = 60 degrees. The actual phase difference given to the oscillators
        # --  is 60 degrees.
        # --  Both amplitudes are equal. The offset is half the amplitud plus a little bit of
        # -   offset so that the robot tiptoe lightly
        A = [0, 0, h, h]
        O = [0, 0, h / 2 + 2, -h / 2 - 2]
        phi = -dir * 90
        phase_diff = [0, 0, DEG2RAD(phi), DEG2RAD(-60 * dir + phi)]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    def moonwalker_left(self, steps=3, T=1000, h=45, dir=LEFT):
        self.moonwalker(steps=steps, T=T, h=h, dir=dir)

    def moonwalker_right(self, steps=3, T=1000, h=45, dir=RIGHT):
        self.moonwalker(steps=steps, T=T, h=h, dir=dir)

    # -- Otto gait: Crusaito. A mixture between moonwalker and walk
    # --   Parameters:
    # --     steps: Number of steps
    # --     T: Period
    # --     h: height (Values between 20 - 50)
    # --     dir:  Direction: LEFT / RIGHT
    def crusaito(self, steps, T, h, dir):
        A = [25, 25, h, h]
        O = [0, 0, h / 2 + 4, -h / 2 - 4]
        phase_diff = [90, 90, DEG2RAD(0), DEG2RAD(-60 * dir)]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    def crusaito_left(self, steps=2, T=1000, h=35, dir=LEFT):
        self.crusaito(steps=steps, T=T, h=h, dir=dir)

    def crusaito_right(self, steps=2, T=1000, h=35, dir=RIGHT):
        self.crusaito(steps=steps, T=T, h=h, dir=dir)

    # -- Otto gait: Flapping
    # --  Parameters:
    # --    steps: Number of steps
    # --    T: Period
    # --    h: height (Values between 10 - 30)
    # --    dir: direction: FOREWARD, BACKWARD
    def flapping(self, steps, T, h, dir):
        A = [12, 12, h, h]
        O = [0, 0, h - 10, -h + 10]
        phase_diff = [DEG2RAD(0), DEG2RAD(180), DEG2RAD(-90 * dir), DEG2RAD(90 * dir)]

        # -- Let's oscillate the servos!
        self.execute(A, O, T, phase_diff, steps)

    def flapping_left(self, steps=2, T=1000, h=35, dir=LEFT):
        self.flapping(steps=steps, T=T, h=h, dir=dir)

    def flapping_right(self, steps=2, T=1000, h=35, dir=RIGHT):
        self.flapping(steps=steps, T=T, h=h, dir=dir)


