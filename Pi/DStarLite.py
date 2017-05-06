from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout

from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Canvas, Line
from random import randint
from queue import PriorityQueue
from kivy.clock import Clock

'''
    Model for performing pathfinding via D* lite.
    Two variants are implemented:
        1. Uses a grid where successors and predecessor relationships are implicitly neighboring cells.
        2. Uses a graph to map spatial and relational data to optimize number of iterations required to reach a solution
    This implementation uses the kivy framework to visually display the process.
'''




class Grid(FloatLayout):

    def __init__(self, dimensions, **kwargs):
        super(Grid, self).__init__(**kwargs)
        self._INFINITY = 100000
        self.numCols, self.numRows = dimensions
        self._obstacles = []
        self._backPointer = {}
        self_forwardPointer = {}
        self._gVal = {}
        self._rhs = {}
        self._start = None
        self._target = None
        self._path = []
        self._predecessor = {}
        self._successor = {}
        self._open = PriorityQueue()
        self._hasChanged = False
        self._locationChanged = ()
        self.drawGrid()
        self.generateObstacles(1500)
        self.setStart((0,0))
        self.setDestination((40,40))
        Window.bind(size=self.update)
        self.update()
        self.execute()


    def update(self, *args):
        self.drawGrid()
        if self._obstacles:
            self.drawObstacles()
        if self._start and self._target:
            self.drawObjective()

    def drawGrid(self):
        div_col, div_row = Window.width/self.numCols, Window.height/self.numRows
        with self.canvas.before as c:
            self.canvas.before.clear()
            Color(1,1,1,1)
            for cols in range(self.numCols+1):
                Line(points=[cols*div_col, 0, cols*div_col, self.height])
            for rows in range(self.numRows+1):
                Line(points=[0, rows*div_row, self.width, rows*div_row])

    def drawObstacles(self):
        div_col, div_row = Window.width / self.numCols, Window.height / self.numRows
        with self.canvas:
            self.canvas.clear()
            Color(1, 0.5, 0.6, 1)
            for x,y in self._obstacles:
                Rectangle(pos=(x*div_col+0.5,y*div_row+0.5), size=(div_col-1,div_row-1))

    def drawObjective(self):
        div_col, div_row = Window.width / self.numCols, Window.height / self.numRows
        with self.canvas.after:
            #self.canvas.after.clear()
            for color, coordinates in [([0,1,0,1],self._start), ([0,0,1,1],self._target)]:
                Color(*color)
                Rectangle(pos=(coordinates[0]*div_col, coordinates[1]*div_row), size=(div_col,div_row))


    def setStart(self, coordinates):
        # if coordinates in self._obstacles:
        #     return
        self._start = (coordinates)

    def setDestination(self, coordinates):
        # if coordinates in self._obstacles:
        #     return
        self._target = (coordinates)


    def generateObstacles(self, numObstacles, *args):
        if self._obstacles == None:
            self._obstacles.extend([(randint(0,self.numCols),randint(0,self.numRows)) for i in range(numObstacles)])
        else:
            self._obstacles = [(randint(0,self.numCols),randint(0,self.numRows)) for i in range(numObstacles)]

    ''' ********************************* Below contain D* Lite operations ***************************************** '''

    def initialize(self):
        for col in range(self.numCols):
            for row in range(self.numRows):
                self._gVal[(col,row)] = self._INFINITY
                self._rhs[(col,row)] = self._INFINITY
        self._rhs[self._target] = 0
        self._open.put((self.calculateKeys(self._target), self._target))

    def cost(self, u, v):
        try:
            x0,y0 = u
            x1, y1 = v
            dif_x = x0-x1
            dif_y = y0-y1
            if dif_x != 0 and dif_y != 0:
                return 1.4
            else:
                return 1

        except Exception as e:
            print(e)
            print('Inputs were: u = {}, and v = {}'.format(u,v))
            return -1

    def heuristic(self, u):
        try:
            return abs(u[0]-self._target[0]) + abs(u[1]-self._target[1])
        except:
            print('invalid arg:', u, 'arg should be a tuple.')
            return -1

    def _getNeighbor(self, u):
        x,y = u
        possibleNeighbor = [(col, row) for col in range(x-1,x+2) for row in range(y-1, y+2) if (row!=x or col!=y)]
        possibleNeighbor = [(x,y) for x,y in possibleNeighbor if (0<=x<self.numCols and 0<=y<self.numRows)]
        return [x for x in possibleNeighbor if x not in self._obstacles]

    def _getPredecessor(self, u):
        if u not in self._predecessor.keys():
            neighbors = self._getNeighbor(u)
            self._predecessor[u] = neighbors
            for s in neighbors:
                if s in self._successor.keys():
                    if u not in self._successor[s]:
                        self._successor[s].append(u)
                else:
                    self._successor[s] = [u]
            return neighbors

        else:
            return self._predecessor.get(u)


    def getPath(self):
        pass

    def updateVertex(self, u):
        if u != self._target:
            self._rhs[u] = min([self.cost(u,s) + self._gVal[s] for s in self._successor[u]])
        if self._gVal[u] != self._rhs[u]:
            self._open.put((self.calculateKeys(u),u))

    def computeShortestPath(self):
        startKey = self.calculateKeys(self._start)
        try:
            while self._open.queue[0][0] < startKey or self._rhs[self._start] != self._gVal[self._start]:
                u = self._open.get()[1]
                if self._gVal[u] > self._rhs[u]:    # If the gval is overconsistent...
                    self._gVal[u] = self._rhs[u]    # make consistent
                    for s in self._getPredecessor(u):
                        self.updateVertex(s)
                elif self._gVal[u] < self._rhs[u]:
                    self._gVal[u] = self._INFINITY
                    for s in self._getPredecessor(u)+[u]:
                        self.updateVertex(s)
                if self._open.empty():
                    break
        except Exception as e:
            print(e, self._open.queue[0], 'here', self._open.queue)
            exit(1)

    def calculateKeys(self, u):
        #print('calculaing keys', u)
        try:
            return min(self._gVal[u], self._rhs[u])
        except Exception as e:
            print(e, u, 'Keys')
            exit()

    def execute(self):
        self.initialize()
        self.computeShortestPath()
        if self._gVal[self._start] == self._INFINITY:
            raise Exception('There are no solutions')
        # while self._start != self._target:
        #     self._start = min([(self.cost(self._start,s)+self._gVal[s], s) for s in self._successor[self._start]], key=lambda x: x[0])[1]
        #     self.drawObjective()
        Clock.schedule_interval(self.move, 0.06)


    def move(self, *args):
        '''
            Move function works by looking at the current calculated potential gradience and traveling down the
            steepest path until goal.
            After every move, a cheack is made on the _hasChanged boolean attribute which is toggled by some other
            methods.
            In the case of changes, the node that has been changed will be stored in the _locationChanged attribute
            All reference on the changed node will be removed and it will be added to the list of obstacles
            Finally the path is repaired.

            Note:: This approach potentially works only for the addition of an object and not for the case that
                    the obstactle is moved/removed
        :param args:
        :return:
        '''
        if self._start != self._target:
            self._start = min([(self.cost(self._start,s)+self._gVal[s], s) for s in self._successor[self._start]], key=lambda x: x[0])[1]
            self.drawObjective()
            if self._hasChanged:
                changed_node = self._locationChanged
                # self._rhs[changed_node] = self._INFINITY
                # self.updateVertex(changed_node)
                for neighbor in self._getNeighbor(changed_node):
                    self._successor[neighbor].remove(changed_node)
                    self._predecessor[neighbor].remove(changed_node)
                    self.updateVertex(neighbor)
                self.computeShortestPath()




class PathingApp(App):
    def build(self):
        self.grid = Grid(dimensions=(50,50), size=Window.size)
        return self.grid


if __name__ == '__main__':
    PathingApp().run()
    #Grid(dimensions=(20, 20), size=Window.size)