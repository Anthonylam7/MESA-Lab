from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle

from kivy.clock import Clock

from random import randint
from queue import PriorityQueue

class grid(FloatLayout):

    def __init__(self, grid_dimension = (10, 10),**kwargs):
        super(grid, self).__init__(**kwargs)
        self.h_count = grid_dimension[0]
        self.v_count = grid_dimension[1]
        self.box_width = Window.height / self.h_count
        self.box_height = Window.height / self.v_count
        self.grid_data = []

        self.cur_block = (0, 0)
        self.start_pos = (0, 0)
        self.goal_pos = (0, 0)
        self.holding_goal = False
        self.holding_start = False
        self.adding_obs = False

        self.initialize_grid()
        self.draw_grid()
        self.randomize_grid(800)

        Clock.schedule_interval( self.update_grid, 1/20 )


    def initialize_grid(self):
        for row in range(self.v_count):
            row = []
            for col in range(self.h_count):
                row.append(0)
            self.grid_data.append(row)


    def draw_grid(self):

        v_div = Window.height/self.v_count
        h_div = Window.height/self.h_count

        with self.canvas.before:
            self.canvas.before.clear()
            Color(1,1,1,0.5)

            for h_line in range(self.v_count + 1):
                Line(points=(0, h_line * v_div, Window.height, h_line * v_div))

            for v_line in range(self.h_count + 1):
                Line(points=(v_line * h_div, 0, v_line * h_div, Window.height))

    def draw_box(self, coordinates, color):
        x , y = coordinates[0] * self.box_width, coordinates[1] * self.box_height

        with self.canvas:
            if color == 1:
                Color(1,0,0,1)
            elif color == 2:
                Color(0, 1, 0, 1)
            elif color == 3:
                Color(0, 0, 1, 1)
            elif color == 4:
                Color(0,1,0,0.3)
            else:
                return

            Rectangle( size = (self.box_width, self.box_height), pos = (x, y) )


    def update_grid(self, *args):
        with self.canvas:
            self.canvas.clear()

        for j, rows in enumerate(self.grid_data):
            for i, cols in enumerate( rows ):
                if cols != 0:
                    self.draw_box( (i,j), color = cols )
                    if cols == 2:
                        self.start_pos = (i,j)
                    elif cols == 3:
                        self.goal_pos = (i,j)

    def randomize_grid(self, num_items):
        #set start ...
        x, y = randint(0, self.h_count - 1), randint(0, self.v_count - 1)
        self.grid_data[y][x] = 2

        # and end
        x, y = randint(0, self.h_count - 1), randint(0, self.v_count - 1)
        self.grid_data[y][x] = 3

        # set random obstacles
        count = 0
        while count < num_items:
            x, y = randint(0, self.h_count-1), randint(0, self.v_count-1)
            if self.grid_data[y][x] == 0:
                self.grid_data[y][x] = 1
                count += 1

    def on_touch_down(self, touch):
        if touch.x < Window.height and touch.y < Window.height:
            x, y = touch.x // self.box_width, touch.y // self.box_height
            x, y = int(x), int(y)
            self.cur_block = (x,y)
            target = self.grid_data[y][x]
            if target == 2:
                self.holding_start = True
            elif target == 3:
                self.holding_goal = True
            else:
                self.adding_obs = True

        return super(grid, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.x < Window.height and touch.y < Window.height:
            x, y = touch.x // self.box_width, touch.y // self.box_height
            x, y = int(x), int(y)
            update = False
            if self.grid_data[y][x] == 1:
                self.holding_goal = 0
                self.holding_start = 0
                return super(grid, self).on_touch_move(touch)

            if (x,y) != self.cur_block and (self.holding_start or self.holding_goal):
                self.grid_data[ self.cur_block[1] ][ self.cur_block[0]] = 0
                self.cur_block = (x,y)
                update = True

            if self.holding_start and update:
                self.grid_data[y][x] = 2
            elif self.holding_goal and update:
                self.grid_data[y][x] = 3
        return super(grid, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.x < Window.height and touch.y < Window.height:
            x,y = touch.x//self.box_width , touch.y//self.box_height
            x,y = int(x), int(y)
            if self.adding_obs:
                self.grid_data[y][x] = 0 if self.grid_data[y][x] else 1
                self.adding_obs = False
            else:
                if self.holding_goal:
                    self.grid_data[y][x] = 3
                    self.holding_goal = False
                elif self.holding_start:
                    self.grid_data[y][x] = 2
                    self.holding_start = False
        else:
            #self.draw_path()
            p = self.trace_path_helper()
            self.clear_path()
            self.p = Clock.schedule_interval( lambda dt: self.update_path(p), 0.3)

        return super(grid,self).on_touch_up(touch)

    def neighbors(self,point):
        x,y = point
        neighbor = []
        if x - 1 >= 0 and self.grid_data[y][x-1] != 1:
            neighbor.append((x-1,y))
        if x + 1 < self.h_count and self.grid_data[y][x+1] != 1:
            neighbor.append((x+1,y))
        if y - 1 >= 0 and self.grid_data[y-1][x] != 1:
            neighbor.append((x, y-1))
        if y + 1 < self.v_count and self.grid_data[y+1][x] != 1:
            neighbor.append((x, y+1))

        return neighbor

    def cost(self, a, b):
        x1, y1 = a
        x2, y2 = b
        return abs(x1 - x2) + abs(y1 - y2)

    def a_star_search(self, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()
            if current == goal:
                break

            for next in self.neighbors(current):
                new_cost = cost_so_far[current] + 10
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristics(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current


        return came_from, cost_so_far

    def heuristics(self, a,b):
        x1,y1 = a
        x2,y2 = b
        return abs(x1-x2) + abs(y1 - y2)

    def draw_path(self):
        came_from, cost_so_far = self.a_star_search(self.start_pos, self.goal_pos)
        cur = self.goal_pos


        while cur != self.start_pos:
            # get the position of parent
            try:
                x,y = came_from[cur]
                self.grid_data[y][x] = 4
                cur = (x,y)

            except Exception as e:
                print(cur in came_from)
                print('x:',cur[0],'y:',cur[1])
                return

        x,y = cur
        self.grid_data[y][x] = 2

    def trace_path_helper(self):
        came_from, cost_so_far = self.a_star_search(self.start_pos, self.goal_pos)
        cur = self.goal_pos
        while cur != self.start_pos:
            # get the position of parent
            try:
                x,y = came_from[cur]
                self.grid_data[y][x] = 4
                cur = (x,y)
                yield

            except Exception as e:
                print(cur in came_from)
                print('x:',cur[0],'y:',cur[1])
                return

        x,y = cur
        self.grid_data[y][x] = 2

    def update_path(self, path_gen, *args):
        try:
            path_gen.__next__()
        except StopIteration:
            Clock.unschedule(self.p)

    def clear_path(self):
        for row in range(self.v_count):
            for col in range(self.h_count):
                if self.grid_data[row][col] == 4:
                    self.grid_data[row][col] = 0




class MainApp(App):
    def build(self):

        return grid( (50,50))
    '''
    def build_config(self, config):
        config.set_default({'test':{
            'key1':'val1',
            'key2':'val2'

        }})
    '''

if __name__ == '__main__':
    MainApp().run()
