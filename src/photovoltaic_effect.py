from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.garden.graph import Graph, MeshStemPlot
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.animation import Animation

Builder.load_string(
'''
#: import Window kivy.core.window.Window
<PhotoVoltaic>:


<Current_Graph>:
    size_hint: None,None
    canvas.before:
        Color:
            rgba: 1,1,1,0.1
        BorderImage:
            border: 10,10,10,10
            size: self.size
            pos: self.pos

<Panel>:
    size: Window.height/2.2, Window.height/2.2
    canvas.before:
        Rectangle:
            size:self.size
            pos: self.pos
            source: 'image/panel.png'
        Color:
            rgba: 1,0,0,1
        Bezier:
            points: [self.right-self.width*0.25, self.top-self.height*0.6,self.right+self.width,self.top-self.height*0.6,self.right+self.width*1.05,self.top+self.height*0.19]
            segments: 200
        Color:
            rgba: 0,0,1,1
        Bezier:
            points: [self.right-self.width*0.25, self.top-self.height*0.61,self.right+self.width,self.top-self.height*0.61,self.right+self.width*1.06,self.top+self.height*0.19]
            segments: 200

<Lamp>:
    size: Window.height/2.2, Window.height/2.2
    canvas:
        PushMatrix
        Rotate:
            axis: 0,0,1
            origin: self.center
            angle: -15
        Color:
            rgba: [1,1,1,self.is_on]
        Rectangle:
            size: self.width*3, self.height*2
            pos: self.x - self.width*0.6 , self.y - self.height*1.2
            tex_coords: (0,1,0,0,1,1,1,0)
            source: 'image/light.png'
        Rotate:
            axis: 0,0,1
            origin: self.center
            angle: 10
        Rectangle:
            size: self.width*3, self.height*2
            pos: self.x - self.width*0.6 , self.y - self.height*1.2

            source: 'image/light.png'
        PopMatrix
    Image:
        pos: root.pos
        size: root.size
        source: 'image/lamp.png'

<Current>:
    size: Window.width/8.5, Window.height/8.5
    canvas:
        Color:
            rgba: 0,1,0.7,0.5
        Rectangle:
            pos:self.pos
            size:self.size
            source: 'image/sun_drop2.png'
    # Image:
    #     color: 1, 0.4, 0.4,1
    #     pos: self.pos
    #     size: self.size
    #     source: 'image/sun_drop2.png'

'''
)


'''
    This module displays a panel next to a lamp
    When the lamp is on, current flows through the panel and is display on a graph
'''

class Current(Widget):
    pass

class EndingAnim(Animation):
    def on_complete(self, widget):
        widget.parent.list_of_cur.remove(widget)
        widget.parent.remove_widget(widget)


class Panel(Widget):
    def __init__(self, **kwargs):
        super(Panel, self).__init__(**kwargs)
        self.is_charging = False
        self.list_of_cur = []


    def spawn(self, *args):
        self.current = Current(
            pos_hint = (None,None),
            pos= (self.right-self.width*0.2, self.top-self.height*0.8)
        )
        self.list_of_cur.append(self.current)
        self.anim = Animation(
            x=self.right+self.width*0.2,
            y=self.top-self.height*0.73
        ) + Animation(
            x=self.right+self.width*0.6,
            y=self.top - self.height * 0.55
        ) + Animation(
            x=self.right+self.width*0.7,
            y=self.top - self.height * 0.45
        ) + Animation(
            x=self.right+self.width*0.77,
            y=self.top - self.height * 0.35
        ) + Animation(
            x=self.right+self.width*0.81,
            y=self.top - self.height * 0.25
        ) + Animation(
            x=self.right+self.width*0.83,
            y=self.top - self.height * 0.19
        ) + EndingAnim(
            x=self.right+self.width*0.85,
            y=self.top - self.height * 0.05
        )
        self.add_widget(self.current)
        self.anim.start(self.current)


class Lamp(Widget):
    is_on = BooleanProperty(False)
    def on_touch_up(self, touch):
        if self.collide_point(touch.x,touch.y):
            self.is_on = not self.is_on

    pass

class Current_Graph(Graph):
    '''
    Class to display the current reading as incoming energy collide with the plot
    data_buff is used to calculate the running average
    data is the data to be displayed on the graph
    '''
    def __init__(self, **kwargs):
        super(Current_Graph, self).__init__(**kwargs)
        self.xlabel = 'Time'
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
        self.ymin = -0
        self.ymax = 10
        self.size_hint = None, None

        self.data_buff = []
        self.data = [[i,0] for i in range(200)]

        self.plot = MeshStemPlot(color=[1, 0, 0, 1])
        self.plot.points = self.data
        self.add_plot(self.plot)
        Clock.schedule_interval( self.update, 1 / 60)


    def update(self, *args):
        # update discards the oldest data and appends the newest
        #
        temp = self.data.pop(0)[1]
        self.data_buff.append(temp)
        for data in self.data:
            temp = data[0]
            data[0] -= 1
        self.data.append( [temp, 0] )
        self.plot.points = self.data

        if len(self.data_buff)%60 == 0:
            #print( sum(self.data_buff)/len(self.data_buff) )
            self.data_buff.clear()

    def collide_widget(self, obj):
        if self.x<obj.x<self.x+self.width and self.y < obj.top < self.y + self.height:
            if isinstance(obj, Current):
                self.data.append( [len(self.data), 4] )


class PhotoVoltaic(FloatLayout):
    def __init__(self, **kwargs):
        super(PhotoVoltaic, self).__init__(**kwargs)
        self.graph = Current_Graph(
            pos_hint={
                'x': 0.5,
                'y': 0.48
            },
            size=(Window.width/2.2, Window.height/2.2)
        )

        self.lamp = Lamp(
            size_hint=(None,None),
            pos_hint={
                'x': 0.05,
                'y': 0.3
            },
            size=(Window.width/2.2,Window.height/2.2)
        )

        self.panel = Panel(
            size_hint=(None,None),
            pos_hint={
                'x': 0.2,
                'y': -0.05
            }
        )
        self.add_widget(self.graph)
        self.add_widget(self.panel)
        self.add_widget(self.lamp)
        self.bind(size=self._update_size)
        Clock.schedule_interval(self._update,1/2)

    def _update_size(self, *args):
        self.size = Window.size
        self.graph.size = (Window.width/2.2, Window.height/2.2)

    def _update(self, *args):
        if self.lamp.is_on:
            self.panel.spawn()
            if self.panel.list_of_cur:
                for cur in self.panel.list_of_cur:
                    self.graph.collide_widget(cur)

class DemoApp(App):
    def build(self):
        return PhotoVoltaic()


if __name__ == '__main__':
    DemoApp().run()
