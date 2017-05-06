#!/usr/bin/env python
'''
Created on Aug 16, 2016

@author: anthony

The Cam class contains all relevant method needed to make use of the phoenix camera
used to stream video feed.

TBD:
--------
1. Add a startup script in the init dunder to start camera streaming to port 25210
2. Implement a read config method to update settings.
3. Implement a write to config method to set callibration.

4. Read in camera raw data to detect objects

'''
import Sunfounder_PWM_Servo_Driver.Servo_init as servo




class Cam(object):
    def __init__(self, **kwargs):
        super(Cam, self).__init__(**kwargs)
        
        self.servo_pins = {
                           'LR' : 14,
                           'UD' : 15
                           }
        
        self.config = {
                       'max' : 700,
                       'min' : 200,
                       'maxIn' : 100,
                       'minIn' : 0,
                       'x_off' : 0,
                       'y_off' : 0,
                       'xNeutral': (self.config['max'] + self.config['min'] + 2 * self.config['x_off']) / 2,
                       'xNeutral': (self.config['max'] + self.config['min'] + 2 * self.config['y_off']) / 2,
                       }
        
        self.servo = servo.init()
 
    
    
    def mapAngle(self,angle):
        '''
            Maps the input angle to the allowable servo angle values and returns that value.
            This is implemented as:
            val = (input - min_in) * (maxOut - minOut) / (maxIn -minIn) + minOut
        '''
                
        return (angle - self.config['minIn']) * (self.config['max'] - self.config['min']) / (self.config['maxIn'] - self.config['minIn']) + self.config['min']
    
    
    def panLR(self, angle):

        angle = self.mapAngle(angle) + self.config['x_off']
        self.servo.setPWM(self.servo_pins['LR'], angle)
        
    def panUD(self, angle):
        
        angle = self.mapAngle(angle) + self.config['y_off']
        self.servo.setPWM(self.servo_pins['UD'], angle)