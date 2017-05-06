from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.garden.graph import Graph, MeshLinePlot

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.graphics import Color,Canvas,Line, Ellipse
from kivy.core.window import Window
from kivy.properties import NumericProperty

from math import sin, cos

Builder.load_string(
    '''
    #: import Window kivy.core.window.Window
<Earth>:
    size_hint: None,None
    size: Window.width/20, Window.width/20
    canvas:
        PushMatrix
        Rotate:
            origin: self.pos
            angle: self.angle
            axis: 0,0,1
        Color:
            rgba: 1,1,1,1
        Rectangle:
            pos: self.x - self.width*25.9/16, self.y - self.width*6.2/8
            size: self.width*3, self.width*1.7
            source: 'image/earth.png'
        Color:
            rgba: 1,0,0,1
        Rectangle:
            pos: self.x + self.width/2, self.y
            size: self.width/8, self.width/8
        PopMatrix

<Sun>:
    size_hint: None,None
    size: Window.width/3.5, Window.height/3.5
    pos: Window.width*1.5, Window.width*1.5
    canvas:
        Color:
            rgba: 1,1,1,1
        PushMatrix
        Rotate:
            origin: self.pos
            axis: 0,0,1
            angle: self.angle
        Ellipse:
            pos: self.x - self.width/2, self.y - self.width/2
            size: self.width,self.width
            source: 'image/sun.png'
        PopMatrix
        Line:
            ellipse:(self.x - Window.width/2,self.y - Window.width/4, Window.width, Window.width/2)
            width: 1
            dash_length: 10
            dash_offset: 10
        Color:
            rgba: 1,0,0,1
        Ellipse:
            pos: self.pos
            size: 5,5

<Space>:
    size_hint: None,None
    size: Window.width*3, Window.height*3
    canvas:
        Color:
            rgba: 1,1,1,1
    Image:
        size_hint: None,None
        allow_stretch: True
        keep_ratio: False
        size: root.size
        pos: root.pos
        source: 'image/space.jpg'

<Container>:
    size_hint: None,None
    size: Window.width*0.5, Window.height
    scroll_x: 0.5
    scroll_y: 0.75
    effect_cls: 'ScrollEffect'
    do_scroll: False,False

<Plot>:
    size_hint: None, None
    size: Window.width*0.5, Window.height*0.5
    pos: Window.width*0.5, Window.height*0.5

<Season>
    size_hint: None,None
    size: Window.size
    '''
)
class Earth(Widget):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Earth, self).__init__(**kwargs)
        Clock.schedule_interval(self.revolve, 1/60)
        self.orbit_path = self.orbit_gen((Window.width*1.5, Window.width*1.5), Window.width, Window.width/2)
        Clock.schedule_interval(self.orbit, 1/60)
        self.bind(size=self._update)

    def revolve(self, *args):
        self.angle+=8
        if self.angle%360 == 0:
            self.angle = 0

    def orbit(self, *args):
        self.pos = self.orbit_path.__next__()

    def orbit_gen(self, center, apogee, perigee):
        angle = 0
        while True:
            angle+=0.009
            yield center[0] + apogee/2*sin(angle), center[1] + perigee/2*cos(angle)

    def _update(self, *args):
        self.orbit_path = self.orbit_gen((Window.width * 1.5, Window.width * 1.5), Window.width, Window.width / 2)


class Sun(Widget):
    angle = NumericProperty(0)
    def __init__(self, **kwargs):
        super(Sun,self).__init__(**kwargs)
        Clock.schedule_interval(self.revolve, 1/60)

    def revolve(self, *args):
        self.angle += 0.3
        if self.angle%360 == 0:
            self.angle = 0

    def add_orbit(self, apogee, perigee):
        with self.canvas:
            Color(0,0,1,1)
            Line(ellipse=(self.x - apogee/2, self.y - perigee/2, apogee, perigee), width=1, dash_offset = 10, dash_length = 10)



class Space(FloatLayout):
    pass

class Container(ScrollView):
    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
        self.scroll = self._scroll_gen()
        Clock.schedule_interval(self._auto_scroll, 1/60)
        self.bind(size=self.update)

    def _auto_scroll(self, *args):
        self.scroll_x, self.scroll_y = self.scroll.__next__()

    def _scroll_gen(self):
        angle = 0
        while True:
            angle += 0.009
            yield 0.5 + 0.12*sin(angle),0.75

    def update(self, *args):
        self.scroll = self._scroll_gen()

class Plot(Graph):
    def __init__(self, **kwargs):
        super(Plot, self).__init__(**kwargs)
        self.xlabel = 'Voltage (mV)'
        self.ylabel = 'Current (Amps)'
        self.x_ticks_minor = 5
        self.x_ticks_major = 25
        self.y_ticks_major = 10
        self.y_grid_label = True
        self.x_grid_label = True
        self.padding = 5
        self.x_grid = True
        self.y_grid = True
        self.xmin = -0
        self.xmax = 200
        self.ymin = -4
        self.ymax = 4
        self.size_hint = None, None


        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = [(i,(80 - .4 * (2.718281 ** (i / 10000. / 0.00259)))/30) for i in range(200)]
        self.baseplot =  MeshLinePlot(color=[0, 1, 1, 1])
        self.baseplot.points = [(i,(80 - .4 * (2.718281 ** (i / 10000. / 0.00259)))/30) for i in range(200)]

        self.add_plot(self.plot)
        self.add_plot(self.baseplot)
        self.var = 1
        Clock.schedule_interval( self.update, 1 / 60)

    def update(self, *args):
        self.var += 0.018
        scale = 1 + 0.2*cos(self.var + 1.44 )
        self.plot.points = [(i,(80 - .4 * (2.718281 ** (i*scale / 10000. / 0.00259)))/30) for i in range(200)]

class Season(FloatLayout):
    def __init__(self, **kwargs):
        super(Season, self).__init__(**kwargs)
        self.container = Container()
        self.space = Space()
        self.sun = Sun()
        self.earth = Earth()
        self.plot = Plot()
        self.setup()


    def setup(self):
        self.space.add_widget(self.sun)
        self.space.add_widget(self.earth)
        self.container.add_widget(self.space)
        self.add_widget(self.container)
        self.add_widget(self.plot)

class DemoApp(App):
    def build(self):
        return Season()


if __name__ == '__main__':
    DemoApp().run()