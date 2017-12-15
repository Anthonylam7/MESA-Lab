from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty


from src.lib.screenContext import BaseScreen



class VehicleBreakdown(BaseScreen):
    pass


class InfoBox(BoxLayout):
    """
    Helper widget for displaying content in a title, info format
    """
    title = StringProperty("")
    content = StringProperty("")
    def __init__(self, title="", content="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.title = title
        self.content = content



if __name__ == "__main__":
    from kivy.app import App
    from kivy.lang.builder import Builder
    Builder.load_string(
    """
    
<InfoBox>:
    Label:
        text: root.title
        size_hint_y: 0.3
        canvas:
            Color:
                rgba: (0.3, 0.3, 0.3, 0.5)
            Rectangle:
                pos: self.pos
                size: self.size
    Label:
        text: root.content
        canvas:
            Color:
                rgba: (0.4, 0.4, 0.4, 0.5)
            Rectangle:
                pos: self.pos
                size: self.size
    """
    )

    class InfoApp(App):
        def build(self):
            return InfoBox(title="This is a test", content="Hope it works")

    InfoApp().run()
