from src.lib.screenContext import BaseScreen
from src.lib.utilities import ScrollableDescription
from src.lib.gl_constants import lamp_shader
from src.lib.constants import PHOTOELECTRIC
from kivy.uix.widget import Widget
from kivy.graphics import RenderContext
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.garden.graph import Graph, MeshLinePlot

class PhotoElectric(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lamp = Lamp()
        self._graph = VoltagePlot()
        self._desc = ScrollableDescription(
            desc=PHOTOELECTRIC,
            size_hint=(0.45, 0.9 ),
            pos_hint={'x':0.55, 'y':0}
        )
        self._desc.text.font_size = Window.height/20
        self.add_widget(self._lamp)
        self.add_widget(PEPanel())
        self.add_widget(self._graph)
        self.add_widget(self._desc)
        Clock.schedule_interval(self.update, 1/30)

    def update(self, dt):
        """Manages the update of child components"""
        if self._lamp._on:
            # When lights are on, activate plot update.
            self._graph.push_data(0.7)
        else:
            self._graph.push_data(0.0)


class Lamp(Widget):

    def __init__(self, **kwargs):
        self._light = Light(pos=self.pos)
        super().__init__(**kwargs)
        self._on = False


    def _update_light(self, *args):
        self._light.pos = self.pos

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self._on = not self._on
            if self._on:
                self._light.pos = (self.x + self.width*0.52, self.y + self.y/8)
                self._light.size = self.size
                self.add_widget(self._light)
            else:
                self.remove_widget(self._light)
        return super().on_touch_up(touch)

class Light(Widget):
    fs = StringProperty('')

    def __init__(self, **kwargs):

        self.canvas = RenderContext(use_parent_projection=True, use_parent_modelview=True)
        super().__init__(**kwargs)
        shader = self.canvas.shader
        shader.fs = lamp_shader
        Clock.schedule_interval(self.update, 1/60.)

    def on_fs(self, instance, value):
        # set the fragment shader to our source code
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed')

    def update(self, dt):
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = list(map(float, self.size))
        self.canvas["offsets"] = (self.x, self.y)
        # This is needed for the default vertex shader.
        self.canvas['projection_mat'] = Window.render_context['projection_mat']


class PEPanel(Widget):
    pass

class VoltagePlot(Graph):
    def __init__(self, **kwargs):
        self.data = MeshLinePlot(color=[1, 0, 0, 1])
        self.data.points = [(x, 0) for x in range(100)]
        self.xlabel = 'X'
        self.ylabel = 'Y'
        self.x_ticks_minor = 5
        self.x_ticks_major = 25
        self.y_ticks_major = 1
        self.y_grid_label = True
        self.x_grid_label = True
        self.padding = 5
        self.x_grid = True
        self.y_grid = True
        self.xmin = -0
        self.xmax = 100
        self.ymin = -1
        self.ymax = 1
        super().__init__(**kwargs)
        self.add_plot(self.data)

    def push_data(self, value):
        """
        appends a point to the end and shift all points to the left
        :param value:
        :return:
        """
        self.data.points.pop(0)
        for i, data in enumerate(self.data.points):
            self.data.points[i] = (data[0]-1, data[1])
        self.data.points.append((len(self.data.points), value))