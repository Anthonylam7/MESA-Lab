from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout

from kivy.properties import ListProperty
from kivy.lang import Builder

Builder.load_string(
    '''
    #: import Window kivy.core.window.Window
<Panel>:
    size_hint: None, None
    size: Window.width/5, Window.height/5
    canvas:
        Color:
            rgba: [1]*4
        Rectangle:
            pos: self.pos
            size: self.size

<Shade_Demo>:
    size_hint: None, None
    size: Window.size
    '''
)



class Panel(Widget):
    '''
        Class to represent a single panel of a solar array
        Instances maintain information about the path to the next class
    '''
    path = ListProperty()
    def __init__(self, next_panel = None, **kwargs):
        super(Panel, self).__init__(**kwargs)
        self.next = next_panel
        self.path = [*self.center] + [*self.next.center] if next_panel else []

class Shade_Demo(FloatLayout):
    def __init__(self, grid_dimensions, **kwargs):
        if isinstance(grid_dimensions, (list, tuple)) and len(grid_dimensions) == 2:
            self.dimension = grid_dimensions
        else:
            raise TypeError('Grid dimension is a list or tuple of length 2.')
        super(Shade_Demo, self).__init__(**kwargs)
        self._panel_list = []
        self.display()


    def display(self):

        for row in range(self.dimension[1]):
            temp = None
            for col in range(self.dimension[0]):
                width = self.width * 0.9 / (self.dimension[0])
                height = self.height * 0.9 / (self.dimension[1])
                x_padding = (self.width - self.width / (self.dimension[0]) * self.dimension[0])/2
                y_padding = (self.height - self.height / (self.dimension[1]) * self.dimension[1])/2
                x_pos = self.x + self.width*col/(self.dimension[0]) + x_padding
                y_pos = self.y + self.height*row/(self.dimension[1]) + y_padding

                p = Panel(
                    pos=(x_pos, y_pos),
                    size=(width,height)
                )
                self.add_widget(p)
                if temp:
                    temp.next = p
                else:
                    self._panel_list.append(p)
                temp = p




class DemoApp(App):
    def build(self):
        return Shade_Demo(grid_dimensions=(3,3))

if __name__ == '__main__':
    DemoApp().run()