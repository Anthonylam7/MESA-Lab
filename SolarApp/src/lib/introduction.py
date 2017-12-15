from src.lib.screenContext import BaseScreen
from src.lib.labels import IntroLabel
from src.lib.constants import INTRO
from kivy.lang.builder import Builder




class Introduction(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._intro = IntroLabel(text=INTRO)
        self.add_widget(self._intro)