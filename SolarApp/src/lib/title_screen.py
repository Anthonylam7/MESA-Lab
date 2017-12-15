from src.lib.labels import BoldLabel, PlainLabel, TapToContinueLabel
from kivy.animation import Animation
from src.lib.screenContext import BaseScreen
from kivy.lang import Builder
from kivy.core.window import Window





class TitleScreen(BaseScreen):
    """
    Landing page to application
    Tap to enter main application
    Upon tapping, animates the characters M,E,S,A to form "MESA"
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._has_clicked = False
        self._m = PlainLabel(
            text="M",
            pos_hint={"x":0.1, "y":0.7}
        )
        self._maryland = PlainLabel(
            text="aryland",
            pos_hint={"x": 0.24, "y": 0.7}
        )
        self._e = PlainLabel(
            text="E",
            pos_hint={"x": 0.1, "y": 0.55}
        )
        self._educational = PlainLabel(
            text="ducational",
            pos_hint={"x": 0.2, "y": 0.55}
        )
        self._s = PlainLabel(
            text="S",
            pos_hint={"x": 0.1, "y": 0.4}
        )
        self._sustainable = PlainLabel(
            text="ustainable",
            pos_hint={"x": 0.2, "y": 0.4}
        )
        self._a = PlainLabel(
            text="A",
            pos_hint={"x": 0.1, "y": 0.25}
        )
        self._activities = PlainLabel(
            text="ctivities",
            pos_hint={"x": 0.21, "y": 0.25}
        )
        self._fear = BoldLabel(
            text="Fear the turtle",
            pos_hint={"x":0.25, "y":0.3}
        )

        self._continue = TapToContinueLabel(
            text="Tap to continue",
            pos_hint={"x":0.25, "y":0.1},
            color=(1,1,1,0)
        )
        self.add_widget(self._continue)
        self.add_widget(self._fear)
        self.cont_anim = (Animation(color=(1,1,1,1)) + Animation(color=(1,1,1,0)))
        self.cont_anim.repeat = True
        self.cont_anim.start(self._continue)
        self._labels = [self._m,
                        self._maryland,
                        self._e,
                        self._educational,
                        self._s,
                        self._sustainable,
                        self._a,
                        self._activities]
        self.add_labels()

    def add_labels(self):
        for l in self._labels:
            l.size = l.texture_size
            self.add_widget(l)

    def update(self, dt):
        # print(self._maryland.size)
        pass

    def on_touch_down(self, touch):
        if not self._has_clicked:
            fade_target = [self._maryland,
                           self._activities,
                           self._educational,
                           self._sustainable]
            anim = Animation(color=(1,1,1,0), duration=2)
            anim.on_complete = self.remove_and_next
            for w in fade_target:
                anim.start(w)
            self.cont_anim.stop(self._continue)
            self.remove_widget(self._continue)



    def remove_and_next(self,wid):
        self.remove_widget(wid)
        if not self._has_clicked:
            self.mesa_anim()
            self._has_clicked = True

    def mesa_anim(self):
        bold = [self._m, self._e, self._s, self._a]
        for i,w in enumerate(bold):
            # print(i)
            # anim = Animation(pos_hint={"x": 0.1, "y": 0.7})
            # anim2 = Animation(pos_hint={"x": 0.2+0.1*i, "y": 0.7})
            # anim.on_complete = lambda wid: anim2.start(wid)
            # anim.start(w)
            (Animation(pos_hint={"x": 0.1, "y": 0.5}, duration=2) +
            Animation(color=(1, 0, 0, 1)) +
             Animation(pos_hint={"x": 0.1+0.22*i, "y": 0.5}, duration=2, transition="out_back")).start(w)
        (Animation(duration=4)+Animation(color=(1, 0, 0, 1), transition="linear")).start(self._fear)


if __name__ == "__main__":
    from kivy.app import App
    from src.lib.screenContext import UpdateManager
    Builder.load_file("../layout/labels.kv")

    class Nuke(App):

        def build(self):
            u = UpdateManager()
            t = TitleScreen()
            u.add_widget(t)
            u.start(30)
            return u


    Nuke().run()