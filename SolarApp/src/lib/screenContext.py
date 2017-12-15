from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock


class UpdateManager(FloatLayout):
    '''
    Class use to handle changing of screens and manage event starting and stopping.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)\

        self._event_callback = None
        self._loop = None
        self._screen = None

    def set_event(self, event):
        """
        :param event: function to be called each frame
        :return:
        """
        if not callable(event):
            raise TypeError("Event expects a callable object")
        self._event_callback = event

    def start(self, framerate=60):
        """
        Start event loop with a desired frame rate
        :param framerate: Non-negative number
        :return:
        """
        try:
            if framerate <= 0:
                raise ValueError("Frame rate should be a non-negative number")
            self._loop = Clock.schedule_interval(self._event_callback, 1/framerate)
        except TypeError as e:
            raise e

    def add_widget(self, widget, index=0):
        """
        Add a child widget and set event
        :param widget: widget with a callable update method
        :param index:
        :return:
        """
        if len(self.children) == 0:
            self.set_event(widget.update)
            super().add_widget(widget, index)
        else:
            raise Exception("UpdateManager expects only one child.")

    def remove_widget(self, widget):
        if len(self.children) == 1:
            try:
                self._loop.cancel()
                super().remove_widget(widget)
                self._loop = None
            except Exception as e:
                raise e
        else:
            raise Exception("No child to remove")


class BaseScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self, dt):
        raise Exception("Class has no defined update callback")