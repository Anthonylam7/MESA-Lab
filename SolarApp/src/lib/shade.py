from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, BooleanProperty

from src.lib.screenContext import BaseScreen
from src.lib.utilities import AttributeSlider, HelpButton
from src.lib.helpScreens import ShadeHelpScreen

import logging

logging.basicConfig(level=logging.DEBUG)

class Cell(Widget):
    """
    Class abstraction of a solar panel cell to be use with a solar panel container
    to demonstrate how solar panels consist of cells in series and parallel

    Each cell outputs a specific amount of voltage and only interacts with shade.
    """

    def __init__(self, voltage, **kwargs):
        super().__init__(**kwargs)
        self.voltage = voltage
        self.defaultVoltage = voltage
        self._isObstructed = False
        logging.debug("Cell initialized with voltage set to {}.".format(self.getVoltage()))

    def getVoltage(self):
        return self.voltage

    def setVoltage(self, voltage):
        self.voltage = voltage

    def resetVoltage(self):
        self.voltage = self.defaultVoltage


class SolarPanel(FloatLayout):
    """
    Class abstracting a solar panel built from solar cells in series and parallel
    An instance is in charge of reporting the total voltage output by its cell
    Note: For learning purposes cells are arrange in grid of series and parallel connections
          but realistically parallel configurations usually occur at the module level not at the cell level
    """

    def __init__(self, dim=(3, 3), **kwargs):
        super().__init__(**kwargs)
        self.dim = dim
        self.cells = []
        logging.debug("Panel initializing...")
        logging.debug("Adding cells...")
        self.populate()
        self.bind(size=self.resize)
        logging.debug("Panel initialized.")

    def populate(self):
        for row in range(self.dim[1]):
            r = []
            for col in range(self.dim[0]):
                cell = Cell(.33)
                r.append(cell)
                self.add_widget(cell)
            self.cells.append(r)
        self.resize()

    def resize(self, *args):
        padX, padY = (10, 10)
        x, y = self.pos
        w, h = self.size
        sw, sh = w / self.dim[0] - padX, h / self.dim[1] - padY
        for row, cells in enumerate(self.cells):
            for col, cell in enumerate(cells):
                cell.pos = (x + padX/2 + col * (sw + padX), y + padY/2 + row * (sh + padY))
                cell.size = (sw, sh)

    def computeVoltage(self):
        # Assuming a bypass diode for each cell and voltage mismatch is treated as an average
        voltsPerSeries = []
        for cells in self.cells:
            seriesVolt = 0
            unobstructed = True
            new_max = 0
            for cell in cells:
                if cell._isObstructed:
                    unobstructed = False
                    new_max = cell.getVoltage()
                if unobstructed:
                    seriesVolt += cell.getVoltage()
                else:
                    seriesVolt += new_max
            voltsPerSeries.append(seriesVolt)
        return sum(voltsPerSeries) / len(voltsPerSeries)

    def getVoltage(self):
        return self.computeVoltage()


class Shade(Widget):
    """
    Abstraction of a draggable shadow with the following properties:
        intensity: Darkeness level between 0 and 1.
        _isDragged: Boolean
        watch: list of cell instances to influence
        WIP
    """
    scale = NumericProperty(0.5)
    intensity = NumericProperty(0.5)
    recalculate = BooleanProperty(False)

    def __init__(self, max_size, **kwargs):
        super().__init__(**kwargs)
        self._isDragged = False
        self._dragOffset = (0,0)
        self.max_size = max_size
        self.bind(scale=self.resize, intensity=self.obstruct)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._isDragged = True
            self._dragOffset = touch.pos
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._isDragged:
            x = self.x + touch.x - self._dragOffset[0]
            y = self.y + touch.y - self._dragOffset[1]
            self.pos = (x, y)
            self._dragOffset = touch.pos
            self.obstruct()
        else:
            return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self._isDragged = False
        return super().on_touch_up(touch)

    def watch(self, cells):
        # Attach a list of cells to watch for
        targets = []
        for series in cells:
            for cell in series:
                targets.append(cell)
        self._watch = targets

    def obstruct(self, *args):
        # Method to modify voltage output of watched cells
        if self._watch:
            self.recalculate = True
            for cell in self._watch:
                if self.collide_widget(cell) and not cell._isObstructed:
                    cell.setVoltage(0.33 * (1 - self.intensity))
                    cell._isObstructed = True
                elif self.collide_widget(cell) and cell._isObstructed:
                    cell.setVoltage(0.33 * (1 - self.intensity))
                elif cell._isObstructed and not self.collide_widget(cell):
                    cell.resetVoltage()
                    cell._isObstructed = False

    def setIntensity(self, val):
        self.intensity = val

    def setMaxSize(self, maxSize):
        self.max_size = maxSize

    def resize(self, *args):
        w, h = self.max_size
        if 0.0 <= self.scale <= 1.0:
            scale = 0.9 * (self.scale) + 0.1
            self.size = (w * scale, h * scale)
            self.obstruct()
        else:
            raise ValueError("Function expects a float between 0.0 and 1.0.")



class ShadeDemo(BaseScreen):
    """
    Display class to showcase demo
    """
    output = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.panel = SolarPanel((4, 4))
        self.shade = Shade(max_size=(300, 300))
        self.shade.setIntensity(0.5)
        self.shade.watch(self.panel.cells)
        self.sizeSlider = AttributeSlider(self.shade, "scale",
                                          size_hint=(0.3, 0.1),
                                          pos_hint={
                                              'x': 0.66,
                                              'y': 0.6
                                          })
        self.intensitySlider = AttributeSlider(self.shade, "intensity",
                                          size_hint=(0.3, 0.1),
                                          pos_hint={
                                              'x': 0.66,
                                              'y': 0.45
                                          })
        self.help = HelpButton("More on Shade", ShadeHelpScreen(),text="Help",
                               size_hint=(0.1, 0.1)
                               )


        self.add_widget(self.panel)
        self.add_widget(self.shade)
        self.add_widget(self.sizeSlider)
        self.add_widget(self.intensitySlider)
        self.add_widget(self.help)

        self.bind(size=self.resize)
        self.shade.bind(recalculate=self.updateOutput)

    def resize(self, *args):
        self.panel.size = (self.width * 0.5, self.height * 0.45)
        self.panel.pos = (self.width * 0.1, self.height * 0.3)
        self.panel.resize()
        self.shade.setMaxSize((self.width / 2, self.height / 2))

    def updateOutput(self, *args):
        self.output = self.panel.getVoltage()
        self.shade.recalculate = False


if __name__ == "__main__":
    from kivy.app import App

    class ShadeApp(App):
        def build(self):
            return ShadeDemo()

    ShadeApp().run()