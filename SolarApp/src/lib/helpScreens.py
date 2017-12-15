from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button

from src.lib.utilities import ScrollableDescription
from src.lib.constants import PHOTOELECTRIC, HARD_SHADE, SOFT_SHADE

class ShadeHelpScreen(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu = DropDown()
        self.menuButton = Button(text="Menu", pos_hint={"x":0.4, "y":0.9}, size_hint=(.2, .1))
        self.srcs = [
            "assets/images/hardShade.png",
            "assets/images/softShade.jpg"
        ]
        self.images = {}
        self.descriptions = {
            "hardShade.png": HARD_SHADE,
            "softShade.jpg": SOFT_SHADE
        }
        self.curImage = None
        self.content = ScrollableDescription(
            desc=PHOTOELECTRIC,
            size_hint=(1, 0.5)
        )
        self.content.text.font_size = 40

        self.add_widget(self.menuButton)
        self.add_widget(self.content)
        # self.add_widget(self.image)

        self.bind(size=self.resize)
        self.menuButton.bind(on_release=lambda x: self.menu.open(x))
        self.loadImages()
        self.loadMenu()



    def loadImages(self):
        for path in self.srcs:
            img = AsyncImage(
                source=path,
                size_hint=(0.4, 0.4),
                allow_stretch=True,
                pos_hint={"x":0.3, "y":0.5}
            )
            key = path.split("/")[-1]
            self.images[key] = img

    def loadMenu(self):
        self.menu.bind(on_select=lambda inst, data: self.setPage(data))
        for path in self.srcs:
            text = path.split("/")[-1]
            b = Button(text=text, size_hint_y=None, height=self.menuButton.height)
            b.bind(on_release=lambda instance: self.menu.select(instance.text))
            self.menu.add_widget(b)

    def resize(self, *args):
        for btn in self.menu.children:
            btn.height = self.menuButton.height

    def setPage(self, data):
        print(data)
        if self.curImage:
           self.remove_widget(self.curImage)
        self.curImage = self.images[data]
        self.add_widget(self.curImage)
        self.content.changeText(self.descriptions[data])



if __name__ == "__main__":
    from kivy.app import App

    class DemoApp(App):
        def build(self):
            return ShadeHelpScreen()

    DemoApp().run()