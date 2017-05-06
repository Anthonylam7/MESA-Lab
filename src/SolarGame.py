from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader

from kivy.properties import NumericProperty
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock

from random import randrange
from kivy.animation import Animation


class Game(FloatLayout):
    points = NumericProperty(0)
    combo_count = NumericProperty(0)
    life = NumericProperty(5)

    def __init__(self, **kwargs):

        super(Game, self).__init__(**kwargs)

        self.p = Player()
        self.s = Source()
        self.lifegauge = LifeGauge(
            pos = (Window.width*5/8, Window.height * 93/100)
        )
        self.l = Label(
            size_hint = (None, None),
            size = self.size,pos = (Window.width/50, Window.height * 7/8),
            text = 'Score: ' + str(self.points))
        self.l2 = Label(
            size_hint = (None, None),
            size = self.size,
            pos = (Window.width*7/8, Window.height * 7/8),
            text = 'Level: ' + str(self.combo_count + 1))

        self.popup = Popup(
            title = 'The Game',
            content = Label(text ='Hello, \nWelcome to the solar collection game.\nYour goal is to collect the suns energy.'
                                  '\nAvoid all trash particles!\n\nControl the collector by swiping left or right.'),
            size_hint = (None, None),
            size = (Window.width/2, Window.height/2),
            on_dismiss = self.start_game
            )
        self.add_widget(self.s)
        self.add_widget(self.p)
        self.add_widget(self.lifegauge)
        self.add_widget(self.l)
        self.add_widget(self.l2)
        self.size = Window.size
        self.sound = SoundLoader.load('sound/Blue Sky.mp3')
        self.sound.loop = True
        self.miss = SoundLoader.load('sound/miss.wav')
        with self.canvas.before:
            Color(0.5,0.5,0.5,1)
            Rectangle(source = 'image/sky.gif', size = self.size, pos = self.pos)
        self.sound.play()
        self.bind(points = self.update_score)
        self.bind(combo_count = self.s.level_up)
        self.bind(life = self.update_life )
        self.is_paused = False

        Clock.schedule_once((lambda *args: self.popup.open()), 1)
        self.stop_game()



    def stop_game(self, *args):
        if self.is_paused:
            pass
        else:
            self.is_paused = True
            print(self.is_paused)
            for wid in self.children:
                try:
                    Clock.unschedule( wid.event )
                except Exception as e:
                    #print(e)
                    pass

    def start_game(self, *args):
        if not self.is_paused:
            pass

        else:
            self.is_paused = False
            for wid in self.children:
                try:
                    wid.event()
                except Exception as e:
                    #print(e)
                    pass


    def update_score(self,*args):
        self.l.text  = 'score: ' + str(self.points)
        self.l2.text = 'Level: ' + str(self.combo_count + 1)

    def update_life(self, *args):
        self.lifegauge.life = self.life
        if self.life <= 0:
            button = Button(text= 'Restart?')
            button.bind(on_press = self.restart)
            self.stop_game()
            print(len(self.children))
            self.s.restart()
            self.p.restart()
            self.popup.title = 'Game Over'
            self.popup.content = button
            self.popup.open()
            self.popup.auto_dismiss = False

    def restart(self, *args):
        self.popup.dismiss()
        self.points = 0
        self.life = 5
        self.combo_count = 0
        self.stop_game()

        temp = []
        for wid in self.children:
            try:
                if isinstance(wid, (NullUnits,Units)):
                    temp.append(wid)
            except Exception as e:
                print(e)
                pass
        for wid in temp:
            wid.canvas.clear()
            wid.event.cancel()
            self.remove_widget(wid)
        self.start_game()



class Source(Widget):
    trans = NumericProperty(1)
    def __init__(self, **kwargs):
        super(Source, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (Window.width/4, Window.width/4)
        self.pos = (Window.width/2 - self.width/2, Window.height * 0.8)
        self.duration = 0.5
        self.speed = 1
        self.period = 6

        with self.canvas.before:
            Color( 0.8, 0.8, 0.8, self.trans)
            Rectangle(source = 'image/sun_drop.png',size = self.size, pos = (self.x - self.width/2, self.y))

        Clock.schedule_interval(self.update, 1/60)
        self.event = Clock.schedule_interval(self.teleport, self.period)

    def update(self, *args):

        self.canvas.before.clear()

        with self.canvas.before:
            Color( 0.8, 0.8, 0.8, self.trans)
            Rectangle(source = 'image/sun_drop.png', size = self.size, pos = (self.x - self.width/2, self.y))

    def teleport(self, *args):
        a = Animation(trans=0, duration=self.duration) + Animation(x=randrange(0, Window.width) , duration= 0.1) + Animation(trans=1,duration=self.duration)
        a.start(self)
        a.bind(on_complete = self.spawn )

    def spawn(self,*args):
        roll = randrange(0, 100)
        if roll < 90:
            u = Units( pos = self.pos)
        else:
            u = NullUnits( pos = self.pos)
        u.vel = self.speed
        self.parent.add_widget(u)

    def level_up(self, *args):
        self.duration *= 0.9
        self.speed *= 1.03
        self.period *= 0.9
        Clock.unschedule(self.event)
        self.event = Clock.schedule_interval(self.teleport, self.period)

    def restart(self):
        self.pos = (Window.width/2 - self.width/2, Window.height * 0.8)
        self.duration = 0.5
        self.speed = 1
        self.period = 6


class Units(Widget):
    def __init__(self, **kwargs):
        super(Units, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (Window.width/30, Window.width/30)
        self.vel = 0

        with self.canvas:
            Color(1,1,1,1)
            Rectangle(source = 'image/sun_drop2.png', size = self.size, pos = (self.x - self.width/2, self.y))
        self.event = Clock.schedule_interval(self.update, 1/30)

    def update(self,*args):
        self.y = self.y - self.vel

        if self.y < 0:
            self.parent.miss.play()
            self.canvas.clear()
            self.event.cancel()
            self.parent.points -= (1000//(self.parent.combo_count + 1))
            self.parent.remove_widget(self)
        self.canvas.clear()
        with self.canvas:
            Color(1,1,1,1)
            Rectangle(source='image/sun_drop2.png', size=self.size, pos=(self.x - self.width / 2, self.y))



class NullUnits(Widget):
    def __init__(self, **kwargs):
        super(NullUnits, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (Window.width/30, Window.width/30)
        self.vel = 0

        with self.canvas:
            Color(1,1,1,1)
            Rectangle(source = 'image/sun_drop2.png', size = self.size, pos = (self.x - self.width/2, self.y))
        self.event = Clock.schedule_interval(self.update, 1/30)

    def update(self,*args):
        self.y = self.y - self.vel

        if self.y < 0:
            self.canvas.clear()
            self.event.cancel()
            self.parent.remove_widget(self)

        self.canvas.clear()
        with self.canvas:
            Color(1,1,1,1)
            Rectangle(source='image/trash.png', size=self.size, pos=(self.x - self.width / 2, self.y))




class Player(Widget):

    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.vel = (0,0)
        self.size = (Window.width/8, Window.width/8)
        self.pos = (Window.width/2 - self.width/2, 0)
        self.init_pos = None
        self.collect = SoundLoader.load('sound/collect.mp3')
        self.trash = SoundLoader.load('sound/trash.wav')
        self.combo = SoundLoader.load('sound/combo.wav')
        self.combo.pitch = 2
        self.consecutive = 0
        with self.canvas:
            Color(1,1,1,1)
            Rectangle(source = 'image/media.png', size = self.size, pos = self.pos )
        self.event = Clock.schedule_interval(self.update, 1/60)

    def on_touch_down(self, touch):
        self.init_pos = (touch.x, touch.y)
        return super(Player, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.init_pos:
            return super(Player,self).on_touch_move(touch)
        self.vel = ((touch.x - self.init_pos[0])/Window.width * 15, 0)
        self.canvas.after.clear()
        with self.canvas.after:
            Color(1,0,0,1)
            if self.vel[0] > 0:
                Rectangle( size = ( (touch.x - self.init_pos[0]), 10 ) , pos = ( self.init_pos[0],self.init_pos[1]))
            else:
                Rectangle( size = ( -(touch.x - self.init_pos[0]), 10) , pos = ( touch.x, self.init_pos[1]) )

        return super(Player,self).on_touch_move(touch)

    def on_touch_up(self, touch):
        self.canvas.after.clear()
        return super(Player,self).on_touch_down(touch)

    def update(self, *args):
        if self.x < 0:
            self.x = 1
            self.vel = (0,0)
        elif self.x > Window.width - self.width:
            self.x = Window.width - self.width - 1
            self.vel = (0,0)
        else:
            self.x = self.x + self.vel[0]
        self.canvas.clear()
        with self.canvas:
            Color(1,1,1,1)
            Rectangle(source = 'image/media.png', size = self.size, pos = self.pos )

        for children in self.parent.children:
            if isinstance(children, Units) and self.collide_widget(children):
                print('Collected.')
                self.consecutive = (self.consecutive + 1)%10
                if self.consecutive > 0:
                    self.collect.play()
                    self.parent.points += (100*(self.parent.combo_count + 1))
                else:
                    self.combo.play()
                    self.parent.combo_count += 1
                    self.parent.points += (100*(self.parent.combo_count + 1))
                children.canvas.clear()
                children.event.cancel()
                children.parent.remove_widget(children)

            elif isinstance(children, NullUnits) and self.collide_widget(children):
                self.parent.life -= 1
                self.trash.play()
                print(self.parent.life, ' left...')
                self.parent.points -= (1000*(self.parent.combo_count + 1))
                if self.parent.life <= 0:
                    print('Game over...')


                children.canvas.clear()
                children.event.cancel()
                children.parent.remove_widget(children)
    def restart(self):
        self.pos = (Window.width / 2 - self.width / 2, 0)
        self.consecutive = 0


class LifeGauge(Widget):
    def __init__(self, **kwargs):
        super(LifeGauge, self).__init__(**kwargs)
        self.image = 'image/life.png'
        self.life = 5
        self.max_life = 5
        self.size_hint = (None, None)
        self.size = (Window.width/5, Window.height/7)

        with self.canvas:
            for offset in range(self.life):
                Color(1,1,1,1)
                Rectangle(source = self.image,
                          pos=(self.x + offset * self.width/self.max_life, self.y),
                          size = (self.width/self.max_life, self.width/self.max_life)
                )
        self.event = Clock.schedule_interval( self.update, 1/20)


    def update(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            for offset in range(self.life):
                Rectangle(source = self.image,
                          pos=(self.x + offset * self.width/self.max_life, self.y),
                          size = (self.width/self.max_life, self.width/self.max_life)
                )





class GameApp(App):
    def build(self):
        return Game()







if __name__ == '__main__':
    GameApp().run()