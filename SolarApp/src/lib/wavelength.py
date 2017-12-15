from kivy.graphics import Color, Line
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout

from src.lib.screenContext import BaseScreen

from math import sin

class WavelengthDemo(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.waves = []
        for i in range(3):
            w = Wave((1,0.2*(4-i),0.3*(1+i)), 0.05*(i+1), pos=(0, 200*i), height=self.height/3)
            self.waves.append(w)
            self.layout.add_widget(w)
        self.add_widget(self.layout)

    def on_size(self, ins, size):
        print(size)
        for i in range(3):
            w = self.waves[i]
            w.pos = (0, 200*i)
            w.height = self.height/3
            print(w.height)

    def update(self, dt):
        for wave in self.waves:
            wave.draw(dt)


class Wave(Widget):
    def __init__(self, color, wavelength, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.color = color
        self.time = 0
        self.wavelength = wavelength

    def draw(self, *args):
        with self.canvas:
            self.canvas.clear()
            pts = []
            for x in range(self.x, self.x+self.width):
                y = self.y + self.height/2*sin(x*self.wavelength-self.time/self.wavelength) + self.height/2
                pts.extend([x, y])

            Color(*self.color)
            Line(points=pts)
        self.time += args[0]

if __name__ == "__main__":
    from kivy.app import App
    from kivy.clock import Clock

    class WaveApp(App):
        def build(self):
            w = WavelengthDemo()
            Clock.schedule_interval(w.update, 1/30)
            return w

    WaveApp().run()