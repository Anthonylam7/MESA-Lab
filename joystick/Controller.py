'''
Created on Jul 16, 2016

@author: Anthony
'''
from threading import Thread
from bluetooth import BluetoothSocket, discover_devices

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button

from kivy.lang import Builder
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.clock import Clock
from bluetooth.bluez import find_service
from bluetooth.btcommon import RFCOMM

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from kivy.uix.floatlayout import FloatLayout

Builder.load_file('controller.kv')



class Queue():
    '''
    Queuing object used to transmit instructions to vehicle
    Sets a meximum buffer size for the queue.
    
    '''
    def __init__(self, maxsize):
        self.queue = []
        self.MAXSIZE = maxsize
        
    def inqueue(self,item):
        if len(self.queue) <= self.MAXSIZE:
            self.queue.append(item)
        
    def dequeue(self):
        if len(self.queue) >0:
            return self.queue.pop(0)
    
    

class ControlStick(Widget):
    '''
        To be used with relative layout as parent to construct a joystick behavior
        
        
        TBD:
        move constants into a single list variable, self.offsets = [self.parent.width/2.0 + self.parent.x, self.parent.height/2.0 + self.parent.y]
        
        add logic to include on_touch_up events to make multiple joysticks independent.
        
    '''
    def __init__(self,**kwargs):
        super(ControlStick, self).__init__(**kwargs)

    
    def on_touch_down(self,touch):
        if self.withinInnerBounds(touch.pos):
            self.pos = (touch.x, touch.y)
        elif self.withinOuterBounds(touch.pos):
            angle = -Vector(1,0).angle((touch.x - self.parent.width/2.0 - self.parent.x ,touch.y - self.parent.height/2.0 -self.parent.y))
            maxdisp = Vector(self.parent.width/2.0,0).rotate(angle)
            self.pos = maxdisp + (self.parent.width/2.0 + self.parent.x, self.parent.height/2.0 + self.parent.y)
    
    def on_touch_move(self, touch):
        if self.withinInnerBounds(touch.pos):
            self.pos = (touch.x, touch.y)
        elif self.withinOuterBounds(touch.pos):
            angle = -Vector(1,0).angle((touch.x - self.parent.width/2.0 -self.parent.x ,touch.y - self.parent.height/2.0 - self.parent.y ))
            maxdisp = Vector(self.parent.width/2.0,0).rotate(angle)
            self.pos = maxdisp + (self.parent.width/2.0 + self.parent.x, self.parent.height/2.0 + self.parent.y)
        return Widget.on_touch_move(self, touch)
    
    def on_touch_up(self, touch):
        self.pos = (self.parent.width/2.0 + self.parent.x , self.parent.height/2.0 + self.parent.y)
        return Widget.on_touch_up(self, touch)
    
    def withinInnerBounds(self,pos):
        '''
        Test to determine if an input is within an inner circlular bound of the widget's parent
        When True, the widget simply updates to the parent's position.
        '''
        if Vector(pos).distance2((self.parent.width/2.0 + self.parent.x , self.parent.height/2.0 + self.parent.y)) < (self.parent.width/2.0)**2:
            return True
        return False
    
    def withinOuterBounds(self,pos):
        '''
        Test to determine if a widget is within the max input range
        widget pos will default to max displacement from center.
        '''
        
        if Vector(pos).distance2((self.parent.width/2.0 + self.parent.x , self.parent.height/2.0 + self.parent.y)) < (self.parent.width*1.1)**2:
            return True
        return False
    
    def displacement(self):
        '''
        Returns the displacement from parent's center
        '''
        return (self.x - self.parent.width/2.0 - self.parent.x, self.y - self.parent.height/2.0 - self.parent.y)
    
    
    

class Joystick(Widget):
    '''
        Constructor for a joystick interface.
        dataOut takes a reference to a Queue for storage
        OpType takes a string either [motor or cam] 
            that determines the operation
    '''
    def __init__(self, dataOut = None, OpType = 'motor', **kwargs):
        super(Joystick,self).__init__(**kwargs)
        self.cstick = ControlStick(pos = (self.x + self.width/2.0, self.y + self.height/2.0))
        self.add_widget(self.cstick)
        self.dataOut = dataOut
        self.operation = OpType
        self.cstick.bind(
            x = self.storeVal,
            y = self.storeVal
            )
        
        
    def storeVal(self, *args):
        '''
        This function is called whenever a change is made to the joystick.
        It stores the current displacement of the inner "nub" relative to the center.
        '''
        userInput = self.cstick.displacement()
        if self.operation == 'motor':
            direction = 'fwd'
            if userInput[1] < 0:
                direction = 'rev'
            #dataStream = '{} {:>2} turn {:>2}'.format(direction, int(abs(userInput[1])), int(userInput[0]))
            dataStream = '{} {:>2} turn {:>2}'.format(direction, int(userInput[1]), int(userInput[0]))
 
        else:
            dataStream = 'CamUD {:>2} CamLR {:>2}'.format(int(userInput[1]), int(userInput[0]))
        
        print(dataStream)
        self.dataOut.inqueue(dataStream)
        
        

class ActionBut(Button):
    
    '''
        Extension of button class for sending commands
        'action' takes a string argument
        'data' takes a reference to a data queue instance 
        
        The action string is stored into a queue data structure on press
    '''   
        
    
    
    
    def __init__(self,action=None,data=None, **kwargs):
        super(ActionBut, self).__init__(**kwargs)
        self.action = action
        self.data = data
        self.text = action

            
    def on_release(self, *args):
        self.data.inqueue(self.action)

        
    


class Controller(Widget):
    '''
    classdocs
    
    This class serves as the interface for control of the vehicle via bluetooth.
    The find_device function is called and a thread is created that searches for the raspberry to connect to.
    Otherwise the controller will only print commands to console
    

    
    User input are stored into a queue as a string.
    An event scheduler will dequeue and transmit the data at 60 hz whil data is in the queue.
    
    
    
    '''


    def __init__(self, **kwargs):
        '''
        Constructor
        
        Relative Layout handles the boundary for the 'joystick'
        
        
        '''
        super(Controller,self).__init__(**kwargs)
        self.queue = Queue(20)
        self.device = None
        self.sock = None
        self.jStick = Joystick(
            dataOut = self.queue,
            OpType = 'motor' ,          
            pos = (Window.width * 0.07, Window.height * 0.15),
            size = (Window.height * 0.3, Window.height * 0.3) 
           )
        
        self.camStick = Joystick(
            dataOut = self.queue,
            OpType = 'cam' ,          
            pos = (Window.width * 0.7, Window.height * 0.15),
            size = (Window.height * 0.3, Window.height * 0.3) 
           )
        
        self.add_widget(self.jStick)
        self.add_widget(self.camStick)
        
        
        self.test = ActionBut(action = 'Default', data = self.queue, pos = (500, 400), size = (70,70))
        self.add_widget(self.test)
        
        #Clock.schedule_interval(self.sendinput, 1/60.)
        
        
        
        

    def sendinput(self,*args):
        '''
        Dequeues the available data and prints data to the console.
        If a devices is connected then data is sent to the device.
        '''
        
        userInput = self.queue.dequeue()
        
        if userInput:
            print(userInput)
            if self.sock:
                self.sock.send(userInput)


    def find_device(self):
        '''
            find_device is called to connect the controller class with a host and must be called in order for 
            the controller to send via bluetooth. Otherwise, the controls will just print to console. 
        '''
        
        def inner():
            self.devices = []
            attempts = 0
            print('Searching')
            while len(self.devices) == 0 and attempts < 3:
                
                self.devices = discover_devices(duration=1, lookup_names=True, flush_cache=True, lookup_class=False)
        
                if len(self.devices) == 0:
                    print('No devices found. Attempt = {}'.format(attempts))
                else:
                    print(self.devices)
                    try:
                        self.server = find_service(address= self.devices[0])
                        self.sock = BluetoothSocket(RFCOMM)
                        self.sock.connect((self.server['host'], self.server['port']))
                    except Exception as e:
                        print(e)
                attempts += 1
            print('Failed')
        t = Thread(target = inner)
        t.start()

            
    def print_device(self):
        if len(self.devices) > 0:
            for addr, name in self.devices:
                print(name)
        else:
            print('No devices found')
            
    
    def connect(self):
        def inner():
            s = socket()
            s.getsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.connect(('',2266))
            while True:
                try:
                    s.send(self.queue.dequeue().encode('utf-8'))
                    
                except:
                    pass
        t = Thread(target = inner)
        t.start()

        
        
class TestApp(App):
    def build(self):
        c = Controller()
        #c.find_device()
        c.connect()
        
        return c
        
        
if __name__ == '__main__':
    TestApp().run()