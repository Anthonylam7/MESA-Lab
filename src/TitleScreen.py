from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window


'''
    This module contains the layout for the title screen

'''




class Title(FloatLayout):
    def __init__(self, **kwargs):
        super(Title, self).__init__(**kwargs)
        self.size = Window.size
        self.title_label = Label(
            text = 'MESA Solar Energy \n   Educational App',
            pos_hint = {
                'x': 0.15,
                'y': 0.7
                },
            size_hint_y = None,
            size = (Window.width/2 , Window.height / 2 ),
            font_size = Window.height/8,
            text_size = (Window.width, Window.height  )
        )


        self.instruction = Label(
            text = 'Swipe right to access the menu',
            pos_hint = {
                'x': 0.24,
                'y': 0.5
                },
            size_hint_y = None,
            size = (Window.width/4, Window.height/4),
            font_size = Window.height/20,
            text_size = Window.size
        )

        self.add_widget(self.title_label)
        self.add_widget(self.instruction)
        self.bind(pos = self._set_size)
        self.bind(size = self._set_size)

    def _set_size(self, *args):
        self.size = Window.size
        self.title_label.size = (Window.width/2 , Window.height / 2 )
        self.title_label.text_size = Window.size
        self.title_label.font_size = Window.height/8
        self.instruction.size = (Window.width / 8, Window.height / 8 )
        self.instruction.text_size = Window.size
        self.instruction.font_size = Window.height / 20


class TitleDemo(App):
    def build(self):
        return Title()

if __name__ == '__main__':
    TitleDemo().run()