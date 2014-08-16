import Adafruit_BBIO.PWM as PWM

H_SERVO="P9_14"
V_SERVO="P8_13"

PWM_FREQ=60.0

DUTY_MIN=3
DUTY_MAX=14.5
DUTY_SPAN=DUTY_MAX-DUTY_MIN


def getDuty(angle):
        return ((angle/180.0)*DUTY_SPAN+DUTY_MIN)

class Servo:

        def servo_setup(self):
                PWM.start(self.pin,getDuty(self.angle),60)

        def servo_shutdown(self):
                PWM.stop(self.pin)

        def servo_set_direct(self,duty):
                PWM.set_duty_cycle(self.pin,duty)

        def servo_set_angle(self):
                PWM.set_duty_cycle(self.pin,getDuty(self.angle))

        def set_angle(self,angle):
                self.angle=angle
                #print self.pin , " to " , self.angle
                self.servo_set_angle()

        def get_angle(self):
                #print self.pin , " is at " , self.angle
                return self.angle

        def delta_angle(self,angle):
                self.set_angle(self.angle+angle)

        def __init__(self, pin, angle):
                self.pin=pin
                self.angle=angle
                self.servo_setup()

def setupServos():
		servo_h=Servo(H_SERVO,70.0)
		servo_v=Servo(V_SERVO,70.0)
		return (servo_h,servo_v)

def shutdownServos():
	PWM.stop(H_SERVO)
	PWM.stop(V_SERVO)
	PWM.cleanup()
