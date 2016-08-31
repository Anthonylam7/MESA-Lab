#!/usr/bin/python
'''
Created on Jul 25, 2016

@author: anthony
'''
from RPi.GPIO import GPIO as GPIO
from socket import import *
from time import time




HOST = ''
PORT = 21000
BUFFSIZE = 1024
MANUAL_MODE = True



server = socket(AF_INET, SOCK_STREAM)
server.bind((HOST,PORT))
server.listen(1)

'''
commands = {
            'fwd': func,
            'rev': func,
            'turn': func,
            'stop': func,
            'camPanLR':func,
            'camPanUD':func
            }

'''

while MANUAL_MODE:
    print(' Waiting for controller to connect... ')
    
    controller, controlAddr = server.accept()
        
    print( 'Connected to {} at {}'.format(controller, controlAddr))
    
    while controller:
        data = controller.recv(BUFFSIZE)
        
        