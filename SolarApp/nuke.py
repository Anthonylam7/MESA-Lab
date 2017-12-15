from kivy.app import App
from src.lib.screenContext import BaseScreen, UpdateManager
from src.lib.photoelectric import PhotoElectric, Lamp
from src.lib.gl_constants import lamp_shader
from src.lib.PNJunction import PNJunctionScreen
from src.lib.shade import ShadeDemo
from src.lib.angleDep import AngleDemo
from kivy.core.window import EventLoop

import logging



logging.basicConfig(level=logging.DEBUG)


class Nuke(App):
    def build(self):
        EventLoop.ensure_window()
        u = UpdateManager()
        i = PhotoElectric()
        u.add_widget(i)
        a = AngleDemo()
        return a

Nuke().run()