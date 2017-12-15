from src.lib.particles import ParticleEngine
from src.lib.screenContext import BaseScreen
from src.lib.gl_constants import ANGLE_FS, ANGLE_VS
from src.lib.utilities import AttributeSlider, HelpButton, ScrollableDescription
from src.lib.constants import FLUX

from kivy.clock import Clock
from kivy.properties import NumericProperty

from math import sin, cos


class AngleDemo(BaseScreen):

    flux = NumericProperty(0.0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pitch, self.roll, self.yaw = 0, 0, 0
        self.arrowPos = 100

        self.engine = ParticleEngine()
        self.pitchSlider = AttributeSlider(target=self, attribute="pitch",
                                           size_hint=(0.3, 0.1),
                                           pos_hint={"x":0.015, "y":0.1}
                                           )
        self.yawSlider = AttributeSlider(target=self,
                                         attribute="yaw",
                                         size_hint=(0.3, 0.1),
                                         pos_hint={"x":0.345, "y":0.1}
                                         )
        self.rollSlider = AttributeSlider(target=self,
                                          attribute="roll",
                                          size_hint=(0.3, 0.1),
                                          pos_hint={"x":0.675, "y":0.1}
                                          )
        self.helpDialog = ScrollableDescription(FLUX)
        self.helpDialog.text.font_size = self.height/5
        self.help = HelpButton(title="What is flux?",
                               content=self.helpDialog)


        self.configureEngine()
        self.configureSliders()
        self.addBox()
        self.addArrow()
        self.engine.draw()


        self.add_widget(self.engine)
        self.add_widget(self.pitchSlider)
        self.add_widget(self.yawSlider)
        self.add_widget(self.rollSlider)
        self.add_widget(self.help)

        self._update = Clock.schedule_interval(self.update, 1/60.)

    def configureSliders(self):
        self.rollSlider.value = 0
        self.pitchSlider.value = 0
        self.yawSlider.value = 0

    def configureEngine(self):
        fmt = (
            (b"vPosition", 3, "float"),
            (b"vTexCoords0", 2, "float"),
            (b"vAngle", 3, "float"),
            (b"vOffsets", 2, "float"),
            (b"vNorm", 3, "float")
        )

        self.engine.set_shader(fs=ANGLE_FS, vs=ANGLE_VS)
        self.engine.format_mesh(fmt)

    def addBox(self):
        self.box = Shape(self.engine, 13)
        points = [
            -100., -100.,  10., 0., 0., 0., 0., 0., 400., 300., -1, -1,  1.,
            -100.,  100.,  10., 0., 0., 0., 0., 0., 400., 300., -1,  1,  1.,
             100.,  100.,  10., 0., 0., 0., 0., 0., 400., 300.,  1,  1,  1.,
             100., -100.,  10., 0., 0., 0., 0., 0., 400., 300.,  1, -1,  1.,
            -100., -100., -10., 0., 0., 0., 0., 0., 400., 300., -1, -1, -1.,
            -100.,  100., -10., 0., 0., 0., 0., 0., 400., 300., -1,  1, -1.,
             100.,  100., -10., 0., 0., 0., 0., 0., 400., 300.,  1,  1, -1.,
             100., -100., -10., 0., 0., 0., 0., 0., 400., 300.,  1, -1, -1.
        ]
        indices = [
            0, 1, 2,
            2, 3, 0,

            4, 5, 6,
            6, 7, 4,

            0, 1, 5,
            5, 4, 0,

            2, 3, 7,
            7, 6, 2,

            0, 3, 7,
            7, 4, 0,

            1, 2, 6,
            6, 5, 1

        ]
        self.box.addVertices(points, indices)
        self.box.setPos((self.width * 5/8, self.height * 0.67))
        self.box.rotate((0., 0.5, 0.))

    def addArrow(self):
        self.arrow = Shape(self.engine, 13)
        points = [
            -50., -20.,  10., 0., 0., 0., 0., 0., 400., 300., -1., -1.,  1.,
            -50.,  20.,  10., 0., 0., 0., 0., 0., 400., 300., -1.,  1.,  1.,
             50.,  20.,  10., 0., 0., 0., 0., 0., 400., 300.,  0.,  1.,  1.,
             50., -20.,  10., 0., 0., 0., 0., 0., 400., 300.,  0., -0.,  1.,
            -50., -20., -10., 0., 0., 0., 0., 0., 400., 300., -1., -1., -1.,
            -50.,  20., -10., 0., 0., 0., 0., 0., 400., 300., -1.,  1., -1.,
             50.,  20., -10., 0., 0., 0., 0., 0., 400., 300.,  0.,  1., -1.,
             50., -20., -10., 0., 0., 0., 0., 0., 400., 300.,  0., -0., -1.,

             50.,  45.,  10., 0., 0., 0., 0., 0., 400., 300., -1., 1.,  10.,
             50., -45.,  10., 0., 0., 0., 0., 0., 400., 300., -1., -1.,  10.,
             150.,   0.,  10., 0., 0., 0., 0., 0., 400., 300., 1., 0.,  10.,

             50.,  45., -10., 0., 0., 0., 0., 0., 400., 300., -1., 1., -10.,
             50., -45., -10., 0., 0., 0., 0., 0., 400., 300., -1., -1., -10.,
             150.,   0., -10., 0., 0., 0., 0., 0., 400., 300., 1., 0., -10.,
        ]
        indices = [
            0, 1, 2,
            2, 3, 0,

            4, 5, 6,
            6, 7, 4,

            0, 1, 5,
            5, 4, 0,

            0, 3, 7,
            7, 4, 0,

            1, 2, 6,
            6, 5, 1,

            8, 10, 9,

            11, 13, 12,

            8, 11, 6,
            8, 2, 6,

            9, 12, 7,
            9, 3, 7,

            8, 10, 13,
            8, 11, 13,

            9, 10, 13,
            9, 12, 13
        ]
        indices = [x+8 for x in indices]
        self.arrow.addVertices(points, indices)

    def update(self, dt):
        # self.box.rotate((self.arrowPos/100, self.arrowPos/100, self.arrowPos/10000))
        self.arrow.rotate((self.arrowPos * 8 / self.width, 0., 0.))
        self.arrow.setPos((self.arrowPos, self.height * 0.67))
        if self.arrowPos > self.width * 0.4:
            self.arrowPos = 0
        self.arrowPos = (self.arrowPos+3)
        self.box.rotate((self.pitch * 3.14, self.yaw * 3.14, self.roll * 3.14))
        self.flux = self.getFlux()

    def on_size(self, inst, value):
        self.box.setPos((self.width * 5 / 8, self.height * 0.67))

    def getFlux(self):
        # Assuming rotation order Z, Y, X
        a, b, c = self.pitch, self.yaw*3.14, self.roll*3.14
        return cos(a)*sin(b)*100


# import random
class Shape:
    """
    Shape classs to be used with particle engine
    """
    def __init__(self, engine, formatLen):
        self.engine = engine
        self.formatLen = formatLen
        self.len = 0
        self.numVertex = 0
        self.index = len(engine._vertices)

    def addVertices(self, vertices, indices):
        self.engine.add_vertex(vertices)
        if indices:
            self.engine.add_indices(indices)
        self.len += len(vertices)
        self.numVertex = self.len//self.formatLen

    def setPos(self, offsets):
        x, y = offsets
        for i in range(self.index, self.index+self.len, self.formatLen):
            self.engine._vertices[i+8:i+10] = [x, y]

    def rotate(self, angles):
        roll, pitch, yaw = angles
        for i in range(self.index, self.index+self.len, self.formatLen):
            self.engine._vertices[i+5:i+8] = [roll, pitch, yaw]