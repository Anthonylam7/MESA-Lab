from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.floatlayout import FloatLayout


from kivy.vector import Vector
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from math import sin, cos
from VectorObject import VectorObject
from kivy.clock import Clock




'''
    This slide demonstrates the dependence of power collection on incident light

    A slider is set to control the position of a sun widget.
    Whenever the position of the sun is changed the sample power flux is calculated
    and displayed on a progress bar.

    When the sun is set to move the background rotates to change the time of day

    Two vectors are drawn on the plane bisecting the plane of the panel to indicate
    1. the normal vector and 2. the incident flux vector

    A button is located at the bottom right that opens a pop explain how flux works.
'''


Builder.load_string(
    '''
    #: import Window kivy.core.window.Window
<Angle_Sun>:
    size_hint: None,None
    size: Window.width/2.2, Window.width/2.2

    pos: Window.width * 0.8, Window.height*0.7
    canvas:
        Color:
            rgba: [0.8]*3 + [1]
        Rectangle:
            size: self.size
            pos: self.x - self.width/2, self.y - self.width/2
            source: 'image/realsun.png'

<PanelArray>:
    size_hint: None, None
    size: Window.width/2.2, Window.height/2.2
    canvas:
        Color:
            rgba: [1 - 0.7*self.color]*3 + [1]
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'image/solararray.png'

        Color:
            rgba: [1, 0, 0, 1]
        Rectangle:
            pos: self.center_panel
            size: 5,5


<Angle_Dep>:
    size_hint: None, None
    size: Window.size
    canvas:
        Color:
            rgba: [ 35/256 + self.color, 206/256, 235/256 - self.color/3, 1  ]
        Rectangle:
            size: self.size
            pos: self.pos

        Color:
            rgba: [1 - self.color*0.7]*3 + [1]
        Rectangle:
            size: self.width, self.height
            pos: self.pos
            source: 'image/grass_bgr.png'
    canvas.after:
        Color:
            rgba: [1, 0, 0, 0.8]
        Line:
            points: self.center_panel + self.panel_normal
            width: 2

        Color:
            rgba: [1, 0.5, 0.5, 0.8]
        Line:
            points: self.center_panel + self.sun_pointer
            width: 2

        Color:
            rgba: [1]*4
        Line:
            ellipse: self.center_panel[0] - 50, self.center_panel[1]-50, 100, 100, 90 + self.angles[0], 85 -self.angles[1]
            width: 1.3

<Sun_Slider>:
    pos_hint: {'x':0.53, 'y':0.05}
    size_hint: None, None
    size: Window.width/3, Window.height/15
    canvas.before:
        Color:
            rgba: [0.5]*3 + [0.8]
        Rectangle:
            size: self.width, self.height * 1.3
            pos: self.pos
    Label:
        text: 'Change Angle'
        pos: root.x, root.y + root.height/2
        size: root.size
        font_size: root.height/2

<PowerBar>:
    pos_hint: {'x': 0.53, 'y': 0.15}
    size_hint: None, None
    size: Window.width / 2.28, Window.height/12
    value: self.power_rate
    canvas.before:
        Color:
            rgba: [0.5]*3 + [0.8]
        Rectangle:
            size: self.width, self.height * 0.9
            pos: self.x, self.y + self.height * 0.2
    Label:
        text: 'Charge Rate'
        size: root.size
        pos: root.x, root.y + root.height * 0.4
        bold: False
        font_size: root.height/2

<Angle_Button>:
    pos_hint: {'x':0.88, 'y':0.05}
    size_hint: None, None
    size: Window.height/8, Window.height/11.8
    canvas:
        Color:
            rgba: [0.3 if self.is_pressed else 0.5]*3 + [0.8 ]
        Rectangle:
            size: self.size
            pos: self.pos

    Label:
        size: root.size
        pos: root.pos
        text: 'More'
        font_size: root.height/2

<Flux_Popup>:
    size: Window.size

    canvas:
        Color:
            rgba: [0,0,0,1]
        Rectangle:
            size: self.size
            pos: self.pos
    canvas.after:
        Color:
            rgba: [1]*4
        Line:
            points: self.points
            close: True
        Color:
            rgba: [1, 0, 0, 1]
        Line:
            points: self.normal
        Line:
            points: self.norm_arrow
            width: 1.5

    canvas:
        Color:
            rgba: [0.7, 0.8, 0.3, 1]
        Line:
            points: self.ray
            width: 2
        Line:
            points: self.ray_arrow
            width: 2

    Label:
        text: 'Flux: ' + '{}'.format(int(100*root.total_flux)) + ' %'
        size_hint: None, None
        size: root.width * 0.3, root.height * 0.3
        pos_hint: {'x':0.03, 'y': 0.75}
        font_size: self.height/4
    '''
)
class PowerBar(ProgressBar):
    power_rate = NumericProperty(0)
    def __init__(self, **kwargs):
        super(PowerBar, self).__init__(**kwargs)

    def update_power(self):
        angle_dif = self.parent.angles[1] + self.parent.angles[0]
        self.power_rate = 80 * cos(angle_dif/180*3.14) +20 if -90<angle_dif<=90 else 40*(1-self.parent.color)




class Flux_Popup(FloatLayout):

    points = ListProperty()
    normal = ListProperty()
    norm_arrow = ListProperty()
    ray = ListProperty()
    ray_arrow = ListProperty()
    ray_offset = 0
    total_flux = NumericProperty(0)
    start = None

    def __init__(self, **kwargs):
        super(Flux_Popup, self).__init__(**kwargs)
        self.points = [
            self.width * 0.75, self.height * 0.75,
            self.width * 0.25, self.height * 0.75,
            self.width * 0.25, self.height * 0.25,
            self.width * 0.75, self.height * 0.25
        ]
        self.vector_object = VectorObject(self.to_coordinates(), [*self.center, 0, 0])
        self.vector_norm = VectorObject(
            coordinates=[
                [self.width*0.5, self.height*0.5, 0, 0],
                [self.width*0.5, self.height*0.5, self.width*0.25, 0]
            ],
            center=[*self.center, 0, 0]
        )
        self.vector_norm_arrow = VectorObject(
            coordinates=[
                [self.width*0.47, self.height*0.5, self.width*0.2, 0],
                [self.width*0.5, self.height*0.5, self.width*0.25, 0],
                [self.width * 0.53, self.height * 0.5, self.width * 0.20, 0]
            ],
            center=[*self.center, 0, 0]
        )

        self.ray = [
            self.width*0.75 - self.ray_offset, self.height*0.5,
            self.width*0.65 - self.ray_offset, self.height*0.5
        ]

        self.ray_arrow = [
            self.width*0.68 - self.ray_offset, self.height*0.51,
            self.width * 0.65 - self.ray_offset, self.height * 0.5,
            self.width * 0.68 - self.ray_offset, self.height * 0.49
        ]
        Clock.schedule_interval(self.animate_ray, 1/60)
        Clock.schedule_interval(self.calculate_flux, 1/20)


    def animate_ray(self, *args):
        self.ray_offset += 10
        if  self.ray_offset > self.width * .15:
            self.ray_offset = - self.width*0.35

        self.ray = [
            self.width*0.75 - self.ray_offset, self.height*0.5,
            self.width*0.65 - self.ray_offset, self.height*0.5
        ]

        self.ray_arrow = [
            self.width*0.68 - self.ray_offset, self.height*0.51,
            self.width * 0.65 - self.ray_offset, self.height * 0.5,
            self.width * 0.68 - self.ray_offset, self.height * 0.49
        ]

    def calculate_flux(self, *args):
        start = self.vector_norm.to_list()[0]
        end = self.vector_norm.to_list()[1]
        self.total_flux = -(start[0] - end[0])/ ((start[0]-end[0])**2 + (start[1]-end[1])**2 + (start[2]-end[2])**2)**0.5
        self.total_flux = self.total_flux if self.total_flux>0 else 0

    def to_coordinates(self):
        coordinates = []
        for pair in zip(self.points[::2],self.points[1::2] ):
            coordinates.append(list(pair))
        return coordinates

    def on_touch_down(self, touch):
        self.start = touch.x, touch.y


    def on_touch_move(self, touch):

        dif_x = -(touch.x - self.start[0]) / self.width * 3.14 * 40
        dif_y = (touch.y - self.start[1]) / self.height * 3.14 * 40


        self.vector_object.transform('rotate', (1, 0, 0), dif_y)
        self.vector_object.transform('rotate', (0,1,0), dif_x)
        self.vector_norm.transform('rotate', (1, 0, 0), dif_y)
        self.vector_norm.transform('rotate', (0,1,0), dif_x)
        self.vector_norm_arrow.transform('rotate', (1, 0, 0), dif_y)
        self.vector_norm_arrow.transform('rotate', (0,1,0), dif_x)
        self.points = []
        self.normal = []
        self.norm_arrow = []
        for a, b, *c in self.vector_object.to_list():
            self.points.append(a)
            self.points.append(b)
        for a, b, *c in self.vector_norm.to_list():
            self.normal.append(a)
            self.normal.append(b)
        for a, b, *c in self.vector_norm_arrow.to_list():
            self.norm_arrow.append(a)
            self.norm_arrow.append(b)
        self.start = touch.x, touch.y


class Angle_Button(Widget):
    is_pressed = BooleanProperty(False)
    popup = Popup(
        title='Flux',
        content=Flux_Popup()
    )

    def on_touch_down(self, touch):
        super(Angle_Button, self).on_touch_down(touch)
        if self.collide_point(touch.x, touch.y):
            self.is_pressed = True
    def on_touch_up(self, touch):
        super(Angle_Button, self).on_touch_up(touch)
        self.is_pressed = False
        if self.collide_point(touch.x, touch.y):
            self.popup.open()

class Angle_Sun(Widget):
    angle = NumericProperty(0)
    def sun_center(self, *args):
        return self.pos
    def set_pos(self,pos):
        self.pos = pos
        print(self.pos)

class PanelArray(Widget):
    center_panel = ListProperty([0,0])
    color = NumericProperty(0)
    def __init__(self, **kwargs):
        super(PanelArray, self).__init__(**kwargs)
        self.bind(size=self.panel_center)
        self.panel_center()

    def panel_center(self, *args):
        '''
        :return: center of panel as tuple
        '''
        self.center_panel = self.x + self.width/1.95, self.y + self.height/1.55
        return self.x + self.width/1.95, self.y + self.height/1.55

class Sun_Slider(Slider):
    def __init__(self, sun, **kwargs):
        self.sun = sun
        super(Sun_Slider, self).__init__(**kwargs)
        self.bind(value=self.rotate_sun)
        self.bind(size=self.update_length)
        self.length = Vector(self.sun.pos).length()

    def rotate_sun(self, *args):
        angle = 30 + 120*self.get_norm_value()
        self.sun.pos  = (Vector(self.length,0).rotate(angle))

    def update_length(self, *args):
        angle = 120 * self.get_norm_value()
        self.length = Vector(self.sun.pos).rotate(-angle).length()


class Angle_Dep(FloatLayout):
    center_panel = ListProperty([0,0])
    panel_normal = ListProperty([0,0])
    sun_pos = ListProperty([0,0])
    sun_pointer = ListProperty([0,0])
    angles = ListProperty([0,0])
    angle_diff =NumericProperty(0)
    color = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Angle_Dep, self).__init__(**kwargs)
        self.sun = Angle_Sun()
        self.panels = PanelArray()
        self.slider = Sun_Slider(sun=self.sun)
        self.button = Angle_Button()
        self.progressbar = PowerBar()
        self.add_widget(self.sun)
        self.add_widget(self.panels)
        self.add_widget(self.slider)
        self.add_widget(self.button)
        self.add_widget(self.progressbar)
        self.center_panel = self.panels.panel_center()
        self.sun_pos = self.sun.sun_center()
        self.calc_angles()
        self.locate_sun()
        self.find_normal()
        self.bind(size=self._update)
        self.sun.bind(pos=self._update)
        Clock.schedule_interval(self._update, 1/20)

    def locate_sun(self):
        angle = self.angles[0]
        self.sun_pointer = Vector(self.panels.width/2, 0).rotate(-angle)+ Vector(self.center_panel)

    def find_normal(self):
        angle = self.angles[1]
        self.panel_normal = Vector(self.panels.width/2, 0).rotate(angle) + Vector(self.center_panel)

    def calc_angles(self):
        angle1 = Vector(1, 0).angle(Vector(self.sun.sun_center()) - Vector(self.center_panel))
        angle2 = Vector(self.center_panel).angle((1, 0))
        self.angles = angle1, angle2


    def _update(self, *args):
        self.center_panel = self.panels.panel_center()
        self.sun_pos = self.sun.sun_center()
        self.calc_angles()
        self.locate_sun()
        self.find_normal()
        self.color = self.panels.color = self.slider.get_norm_value()
        self.progressbar.update_power()


class DemoApp(App):
    def build(self):
        return Angle_Dep()


if __name__ == '__main__':
    DemoApp().run()