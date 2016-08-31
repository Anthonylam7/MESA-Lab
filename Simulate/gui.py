'''
Created on Aug 17, 2016

@author: anthony
'''

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.vector import Vector

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread


HOST = ''
PORT = 2266

class Car(Widget):
    currPos = ListProperty([400, 400])
    angle = NumericProperty(0)
    angleDelta = 0
    
    def __init__(self,**kwargs):
        super(Car,self).__init__(**kwargs)
        self.velocity = [0,0]
        
        Clock.schedule_interval(self._update_pos, 1/60.)
    
    def _update_pos(self,*args):
        self.currPos = Vector(self.currPos) + Vector(self.velocity).rotate(self.angle)
        self.angle += self.angleDelta
        


class GUI(App):
    '''
    classdocs
    
    '''


    def __init__(self, **kwargs):
        super(GUI, self).__init__(**kwargs)
        self.l = FloatLayout()
        
        
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.getsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind((HOST,PORT))
        
        self.t = Thread(target = self.startListen)
        self.t.start()
        
    def build(self):
        self.c = Car()
        self.l.add_widget(self.c)
        return self.l
        
        
    def startListen(self, *args):
        print('Started listening')
        
        self.socket.listen()
        client, addr = self.socket.accept()
        
        print('Connected to {}...'.format(addr))
        
        with client:
            while True:
                data = client.recv(1024)
                try:           
                    item1, val1, item2, val2 = data.split()
                    #testing inputs
                    #print('{} {}'.format(val1, val2))
                    #self.c.currPos = [self.c.currPos[0] + float(val2)/100, self.c.currPos[1] + float(val1)/100]
                    print(val1, val2)
                    self.c.velocity = [0 , float(val1)/50]
                    self.c.angleDelta = -float(val2)/20
                    
                    print(self.c.currPos)
                except Exception as e:
                    pass
                
                
if __name__ == '__main__':
    GUI().run()
                
                
                
                
                
        