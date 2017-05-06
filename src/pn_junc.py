
# kivy graphical imports
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout

# kivy behavioral imports
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.lang import Builder
#
from random import random

Builder.load_string(
    '''
    #: import window kivy.core.window

<Particles>:
    size_hint: None, None
    size: 10, 10
	canvas:
		Color:
			rgba: [1, 1, 1, 1]
		Ellipse:
			size: self.size
			pos: self.x-self.width/2.0, self.y-self.height/2.0

<Electron>:
    size_hint: None, None
    size: 10, 10
	canvas:
		Color:
			rgba: [0, 1, 1, 1]
		Ellipse:
			size: self.size
			pos: self.x-self.width/2.0, self.y-self.height/2.0

<Hole>:
    size_hint: None, None
    size: 10, 10
	canvas:
		Color:
			rgba: [1, 1, 0, 1]
		Ellipse:
			size: self.size
			pos: self.x-self.width/2.0, self.y-self.height/2.0


<PNJunction>:
    size_hint: None, None
    id: PNJunc
    size: window.Window.width * 0.5, window.Window.height * 0.3
    pos_hint: {'x':0.25,'y': 0.4}
    canvas:

        Color:
            rgba: [1, 0.2, 0.2, 1]

        Rectangle:
            pos: self.pos
            size: self.width/2, self.height

        Color:
            rgba: [0.2, 0.2, 1, 1]
        Rectangle:
            pos: self.x + self.width/2, self.y
            size: self.width/2, self.height

        Color:
            rgba: [1, 1, 1, self.depleted * 0.7]
        Rectangle:
            size: self.depletion_width, self.height
            pos: self.x + self.width/2 - self.depletion_width/2, self.y

    Label:
        text: 'N'
        font_size: PNJunc.width/8
        size_hint: None,None
        size: PNJunc.width/8, PNJunc.width/8
        pos_hint_x: None
        pos_hint_y: None
        pos: PNJunc.x, PNJunc.y + PNJunc.height*3/4
    Label:
        text: 'P'
        font_size: PNJunc.width/8
        size_hint: None,None
        size: PNJunc.width/8, PNJunc.width/8
        pos_hint_x: None
        pos_hint_y: None
        pos: PNJunc.x + PNJunc.width*7/8, PNJunc.y + PNJunc.height*3/4


    '''
)

'''
    TBD:
        1. Fwd Rev bias
        2. Labels and interaction
        3. Full implementation container

'''


class Particles(Widget):
    def __init__(self,**kwargs):
        super(Particles,self).__init__(**kwargs)
        self.speed = 5 * random()
        self.angle = 360 * random()
        self.xbound = (0,0)
        self.ybound = (0,0)
        self.x_update = None
        self.y_update = None


    def move(self,*args):
        self.pos = Vector(self.speed,0).rotate( self.angle ) + self.pos
        if self.x_update and self.x_update[0] < self.x < self.x_update[1]:
            self.xbound = self.x_update
        if self.y_update and self.y_update[0] < self.y < self.y_update[1]:
            self.ybound = self.y_update

        if self.y > self.ybound[1] or self.y < self.ybound[0]:
            self.angle = -self.angle

        if self.x > self.xbound[1] or self.x < self.xbound[0]:
            self.angle = (-self.angle + 180)%360

    def collide_widget(self, wid):
        return Vector(self.pos).distance(wid.pos)  <= (self.width + wid.width)/2


class Electron(Particles):
    count = 0
    def __init__(self,**kwargs):
        super(Electron,self).__init__(**kwargs)
        type(self).count += 1


class Hole(Particles):
    count = 0
    def __init__(self,**kwargs):
        super(Hole,self).__init__(**kwargs)
        type(self).count += 1




class PNJunction(FloatLayout):
    depleted = NumericProperty(0)
    depletion_width = NumericProperty(0)

    def __init__(self,**kwargs):
        super(PNJunction,self).__init__(** kwargs)
        self.particle_list = []
        self.state = 'unbiased'
        self.finished_transition = True
        self.state_changed = False
        self._has_init = False
        self.depletion_width = self.width * 0.20
        self.num_particles = 50

        Clock.schedule_interval(self.move_particle, 1/60.)


    def pn_init(self):
        '''
            Populates the PN junction
        :return:
        '''
        for i in range(0, self.num_particles):
            self.add_particle('electron')
            self.add_particle('hole')
        self._has_init = True



    def add_particle(self, *args):

        if args[0] == 'electron':
            px, py = self.x + self.width/2.0 * random(), self.y + self.height * random()
            p = Electron(pos = (px,py) )
            p.ybound = (self.y, self.y+self.height)
            p.xbound = (self.x, self.x + self.width/2)

        elif args[0] == 'hole':
            px, py = self.x + self.width/2.0 * random() + self.width/2, self.y + self.height * random()
            p = Hole(pos = (px,py) )
            p.ybound = (self.y, self.y+self.height)
            p.xbound = (self.x + self.width/2, self.x + self.width)
        else:
            print('invalid')

        self.add_widget(p)
        self.particle_list.append(p)


    def change_state(self, *args):
        if args[0]:
            self.state = args[0]
            self.state_changed = False

        if self.finished_transition and self.state_changed:
            self.finished_transition = False
            print(self.state)
            if self.state == 'unbiased':
                for particle in self.particle_list:
                    if isinstance(particle, Electron):
                        particle.x_update = (self.x, self.x + self.width/2)
                    elif isinstance(particle, Hole):
                        particle.x_update = (self.x + self.width/2, self.x + self.width)

            if self.state == 'fwd biased':
                e_count = 0
                h_count = 0
                for particle in self.particle_list:
                    if isinstance(particle, Electron) and e_count < Electron.count * 0.1:
                        particle.x_update = (self.x + self.width/2 - self.depletion_width/2,
                                           self.x + self.width/2 + self.depletion_width/2)
                        e_count += 1

                    elif isinstance(particle, Electron) and e_count >= Electron.count * 0.1:
                        particle.x_update = (self.x, self.x + self.width/2 - self.depletion_width/2)

                    if isinstance(particle, Hole) and h_count < Hole.count * 0.1:
                        particle.x_update = (self.x + self.width/2 - self.depletion_width/2,
                                           self.x + self.width/2 + self.depletion_width/2)
                        h_count += 1

                    elif isinstance(particle, Hole) and h_count >= Hole.count * 0.1:
                        particle.x_update = (self.x + self.width / 2 + self.depletion_width/2, self.x + self.width)
                    self.depleted = 1

            if self.state == 'rev biased':
                for particle in self.particle_list:
                    if isinstance(particle, Electron):
                        particle.x_update = (self.x, self.x + self.width / 2)
                    elif isinstance(particle, Hole):
                        particle.x_update = (self.x + self.width / 2, self.x + self.width)

            self.state_changed = False
            self.finished_transition = True


    def move_particle(self, *args):
        if self.particle_list:
            for particle in self.particle_list:
                particle.move()
        else:
            pass

    def clean_up(self, *args):
        for i in range(0, len(self.particle_list)):
            particle = self.particle_list[0]
            particle.canvas.clear()
            self.particle_list.remove(particle)
            self.remove_widget(particle)
        print(len(self.particle_list))
        self._has_init = False

    def on_touch_down(self, touch):
        if not self._has_init:
            self.pn_init()
        else:
            self.clean_up()





class pn_junc(App):
    def build(self):
        f = FloatLayout()
        p = PNJunction( pos = (200,200))
        f.add_widget(p)


        return f




if __name__ == '__main__':
    pn_junc().run()