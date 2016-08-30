#!/usr/bin/env python

import Sunfounder_PWM_Servo_Driver.Servo_init as servo
import RPi.GPIO as GPIO


'''
The Motor class contains all the relevant methods to using the motors

TBD:
-----------
1. Implement config read/write
2. Implement map speed method



'''

class Motors(object):
    def __init__(self,**kwargs):
        super(Motors,self).__init__(**kwargs)
        self.steering = {
                         'NEUTRAL': 450,
                         'offset_angle': 0
                         }
        self.motor_pin = {
                       'left_motor_fwd':11,
                       'lef_motor_rev':12,
                       'right_motor_fwd':13,
                       'right_motor_rev':15
                      }
        self.i2c_pin = {
                       'LEFT_SPEED': 4,
                       'RIGHT_SPEED': 5,
                       'servo_pin': 0
                        }
        
        
        self.CONFIG = {
                       'STEERING_MIN': 0,
                       'STEERING_MAX': 800,
                       'SPEED_MIN': 0,
                       'SPEED_MAX': 100,
                       'STEERING_IN_MIN': 0,
                       'STEERING_IN_MAX': 100
                                             
                       }
        
        self.i2c_pwm = servo.init()
        self.init()
        
    
    def init(self):
        GPIO.setmode(GPIO.BOARD)
        for pin in self.i2c_pin:
            GPIO.setup(pin, GPIO.OUT)
            
    def mapAngle(self, angle):
        '''
            Maps the input angle to the allowable steering servo angle values and returns that value.
            This is implemented as:
            val = (input - min_in) * (maxOut - minOut) / (maxIn -minIn) + minOut
        '''
        
        inputMin, inputMax = self.CONFIG['STEERING_IN_MIN','STEERING_IN_MAX']
        steerMin, steerMax = self.CONFIG['STEERING_MIN','STEERING_MAX']
        
        return (self.angle - self.inputMin) * (steerMax - steerMin)/ (inputMax - inputMin) + steerMin
    
    def mapSpeed(self):
        pass
        
    def turn(self, angle):
        angle = self.mapAngle(angle)
        self.i2c_pwm.setPWM(self.i2c_pin['servo_pin'], 0, angle )
    
    def set_spd(self,spd):
        spd *= 40
        self.i2c_pwm.setPWM(self.i2c_pin['LEFT_SPEED'], 0 , spd)
        self.i2c_pwm.setPWM(self.i2c_pin['RIGHT_SPEED'], 0 , spd)
        pass
    
    
    def foward(self, spd = 50):
        
        self.set_spd(spd)        
        GPIO.output( self.motor_pin['left_motor_fwd'], GPIO.LOW )
        GPIO.output( self.motor_pin['left_motor_rev'], GPIO.HIGH )
        GPIO.output( self.motor_pin['right_motor_fwd'], GPIO.LOW )
        GPIO.output( self.motor_pin['right_motor_rev'], GPIO.HIGH )
        
        
    def reverse(self, spd = 50):
        
        self.set_spd(spd)
        GPIO.output( self.motor_pin['left_motor_fwd'], GPIO.HIGH )
        GPIO.output( self.motor_pin['left_motor_rev'], GPIO.LOW )
        GPIO.output( self.motor_pin['right_motor_fwd'], GPIO.HIGH )
        GPIO.output( self.motor_pin['right_motor_rev'], GPIO.LOW )
        
    def stop(self):
        
        GPIO.output( self.motor_pin['left_motor_fwd'], GPIO.LOW )
        GPIO.output( self.motor_pin['left_motor_rev'], GPIO.LOW )
        GPIO.output( self.motor_pin['right_motor_fwd'], GPIO.LOW )
        GPIO.output( self.motor_pin['right_motor_rev'], GPIO.LOW ) 
        
          
        
        