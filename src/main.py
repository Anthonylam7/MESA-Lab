from menu_container import InterfaceConstruct
from TitleScreen import Title
from photovoltaic_effect import PhotoVoltaic
from pn_junc import PNJunction
from season import Season
from angle_dep import Angle_Dep
from SolarGame import Game
from kivy.app import App


class MESAapp(App):
    def build(self):
        screens = {
            'Title': Title,
            'Photoelectric Effect': PhotoVoltaic,
            'PN Junction': PNJunction,
            'Season': Season,
            'Game': Game,
            'Angles': Angle_Dep
        }
        names = ['Title', 'Photoelectric Effect', 'PN Junction', 'Season', 'Game', 'Angles']
        interface = InterfaceConstruct(screens=screens, screenNames= names)
        interface.set_main_panel(screens['Title']())
        return interface


if __name__ == '__main__':
    MESAapp().run()