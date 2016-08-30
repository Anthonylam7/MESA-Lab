#!/usr/bin/env python
'''
Created on Aug 17, 2016

@author: anthony

The Actuator class serves as the central control for all movable parts
connected to the Raspberry Pi.

The pins are declared in the individual py modules currently.

Commands are made by passing a data string to the parseCmd method.



TBD:
--------
1. Interact with config files
2. Improve parseCmd
3. Add more complex behaviors to be used with autonomous mode
4. Add in an autonomous method that loops in a the background until status changes
5. Implement a change state callable to switch between auto and manual
 

'''

from PiCam import Cam
from PiMotor import Motors




class Actuator(object):
    def __init__(self, **kwargs):
        super(Actuator, self).__init__(**kwargs)
        
        self.motors = Motors()
        self.cam = Cam()
        
        self.instructions = {
                             'fwd': self.motors.foward,
                             'rev': self.motors.reverse,
                             'turn': self.motor.turn,
                             'camLR': self.cam.panLR,
                             'camUP': self.cam.panUD
                             }
    
    
    
    def parseCmd(self, data):
        '''
            This method parses a data string and calls the corresponding function.
            
            Pass in a string argument into the parseCMD method
            in the format of
            '[fwd, rev] val turn val'
            or
            'camLR val camUD val'
        '''
        
        cmdStr = data.split(' ')
        self.instructions.get(cmdStr[0])(cmdStr[1])
        self.instructions.get(cmdStr[2])(cmdStr[3])
        
        
    '''
    TBD:
    complex motion s.a. parallel park, 3pt turn, cam scan
    extended part library s.a. mech arm, sensors
    
    '''