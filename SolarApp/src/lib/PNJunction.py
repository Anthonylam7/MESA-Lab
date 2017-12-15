from .particles import ParticleManager, Particle
from .gl_constants import PROTON_FS, PROTON_VS
from .screenContext import BaseScreen
from .utilities import HelpButton

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.dropdown import DropDown
from kivy.vector import Vector
from kivy.clock import Clock

from random import random

class Ions(Particle):
    def __init__(self, **kwargs):
        super().__init__()
        self.width = kwargs.get("width", 100)
        self.height = kwargs.get("height", 100)
        self.pos_hint = kwargs.get("pos_hint", (random(),random()))
        self.pos = kwargs.get("pos", (0,0))
        x, y = self.pos
        w, h = self.width, self.height
        self.color = (0., 1., 1.)
        self.vertices = [
            x - w / 2., y - h / 2., 0., 0., x, y, *self.color,
            x - w / 2., y + h / 2., 0., 1., x, y, *self.color,
            x + w / 2., y + h / 2., 1., 1., x, y, *self.color,
            x + w / 2., y - h / 2., 1., 0., x, y, *self.color,
        ]

    def updateVertices(self):
        vertices = self._manager._vertices
        index = self._index
        x, y = self.pos
        w, h = self.width, self.height
        self.vertices = [
            x - w / 2., y - h / 2., 0., 0., x, y, *self.color,
            x - w / 2., y + h / 2., 0., 1., x, y, *self.color,
            x + w / 2., y + h / 2., 1., 1., x, y, *self.color,
            x + w / 2., y - h / 2., 1., 0., x, y, *self.color,
        ]
        vertices[index: index + self._formatLength * 4] = self.vertices

    def update(self, dt):
        """
        :param dt:
        :return:
        """
        self.updateVertices()


class freeCharges(Particle):
    def __init__(self, **kwargs):
        super().__init__()
        self.width = kwargs.get("width", 100)
        self.height = kwargs.get("height", 100)
        self.pos_hint = kwargs.get("pos_hint", (random(),random()))
        self.pos = kwargs.get("pos", (0., 0.))
        self.bounds = kwargs.get("bounds", [0,1,0,1])
        self.vel = Vector(random()-0.5,random()-0.5)
        x, y = self.pos
        w, h = self.width, self.height
        self.color = (0.5, 1., 0.5)
        self.vertices = [
            x - w / 2., y - h / 2., 0., 0., x, y, *self.color,
            x - w / 2., y + h / 2., 0., 1., x, y, *self.color,
            x + w / 2., y + h / 2., 1., 1., x, y, *self.color,
            x + w / 2., y - h / 2., 1., 0., x, y, *self.color,
        ]

    def updateVertices(self):
        vertices = self._manager._vertices
        index = self._index
        x, y = self.pos
        w, h = self.width, self.height
        self.vertices = [
            x - w / 2., y - h / 2., 0., 0., x, y, *self.color,
            x - w / 2., y + h / 2., 0., 1., x, y, *self.color,
            x + w / 2., y + h / 2., 1., 1., x, y, *self.color,
            x + w / 2., y - h / 2., 1., 0., x, y, *self.color,
        ]
        vertices[index: index + self._formatLength * 4] = self.vertices

    def update(self, dt):
        """
        :param dt:
        :return:
        """
        if self.pos[0] > self.bounds[1] or self.pos[0] < self.bounds[0]:
            self.vel[0] *= -1
        if self.pos[1] > self.bounds[3] or self.pos[1] < self.bounds[2]:
            self.vel[1] *= -1
        self.pos = self.vel + self.pos
        self.updateVertices()



class PNJunction(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PNJunctionScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # components
        self._junction = PNJunction()

        # attributes
        self.ions = []
        self.freeCharges = []
        self._grid_dim = (8, 8)
        self._field = [0 for _ in range(self._grid_dim[0]*self._grid_dim[1])]

        # setup
        self._attach_particle_engine()
        self._add_ions()
        self._add_component()
        self._junction.bind(size=self.reposition, pos=self.reposition)

    def _attach_particle_engine(self):
        self._particle_engine = ParticleManager()
        self._particle_engine.set_shader(fs=PROTON_FS, vs=PROTON_VS)
        self._particle_engine.format_mesh(
            format=
            (
                (b'vPosition', 2, "float"),
                (b"vTexture0", 2, "float"),
                (b"vCenter", 2, "float"),
                (b"vColor", 3, "float")
            )
        )
        self._particle_engine.canvas["pSize"] = (self.width / 10, self.width / 10)
        self._particle_engine.draw()

    def _add_ions(self):
        x, y = self._junction.pos
        rows, cols = self._grid_dim
        w, h = self._junction.size
        w /= cols
        h /= rows
        width, height = (self.width / 10, self.width / 10)
        for i in range(rows*cols):
            if (i%2 and i//rows%2) or (i%2==0 and i//rows%2==0):
                pos = (i%cols * w + x + w/2, i//cols * h + y + h/2)
                pos_hint = ((pos[0]-x)/w/cols, (pos[1]-y)/h/rows)
                d = Ions(pos=pos, width=width, height=height, pos_hint=pos_hint)
                if i%cols >= cols//2:
                    d.color = (1.0, 1.0, 0.0)
                self._field[i] = 1
                self.ions.append(d)
                self._particle_engine.addParticle(d)

    def _add_component(self):
        self.add_widget(self._junction)
        # self.add_widget(self._next)
        # self.add_widget(self._prev)
        # self.add_widget(self._dropdown)
        # self.add_widget(self._num_partices)
        # self.add_widget(self._help)
        self.add_widget(self._particle_engine)

    def _add_free_charges(self, n):
        w,h = self._junction.size
        x,y = self._junction.pos
        width, height = (self.width/10, self.width/10)
        for _ in range(n):
            bounds = [x, x + w, y, y + h]
            pos_hint = (random(),random())
            pos = (pos_hint[0]*w + x, pos_hint[1]*h + y)
            a = freeCharges(pos=pos, width=width, height=height, bounds=bounds, pos_hint=pos_hint)
            self.freeCharges.append(a)
            self._particle_engine.addParticle(a)

    def on_touch_up(self, touch):
        if not len(self.freeCharges) and self._junction.collide_point(*touch.pos):
            # self._add_ions()
            pass
        if len(self.ions) < 100 and self._junction.collide_point(*touch.pos):
            self._add_free_charges(1)

    def reposition(self, wid, size):
        w, h = self._junction.size
        x, y = self._junction.pos
        if self.ions:
            for ion in self.ions+self.freeCharges:
                ion.width, ion.height = (size[0]/10, size[1]/10)
                ion.pos = (ion.pos_hint[0]*w + x, ion.pos_hint[1]*h + y)




    def things_to_implement(self):
        self._next = Button(text="Next",
                            size_hint=(0.2, 0.1),
                            pos_hint={'x': 0.7,
                                      'y': 0.1})
        self._prev = Button(text="Prev",
                            size_hint=(0.2, 0.1),
                            pos_hint={'x': 0.48,
                                      'y': 0.1})
        self._num_partices = Slider(size_hint=(0.2, 0.1),
                                    pos_hint={
                                        'x': 0.75,
                                        'y': 0.6
                                    }
                                    )
        self._stages = DropDown()
        for i in range(10):
            b = Button(text="Stage: " + i.__repr__(), size_hint_y=None)
            b.bind(on_release=lambda instance: self._stages.select(instance.text))
            self._stages.add_widget(b)
        self._dropdown = Button(
            text="Select",
            size_hint=(0.3, 0.05),
            pos_hint={
                'x': 0.7,
                'y': 0.7
            }
        )
        self._dropdown.bind(on_release=self._stages.open)
        self._stages.bind(on_select=lambda instance, text: self._dropdown.__setattr__("text", text))
        self._help = HelpButton()


if __name__ == "__main__":
    from kivy.app import App
    from kivy.core.window import EventLoop
    from random import random
    class PN(App):
        def build(self):
            EventLoop.ensure_window()
            P = PNJunctionScreen()
            return P

    PN().run()