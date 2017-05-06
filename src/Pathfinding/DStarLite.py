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

    Current the constructor only supports the creation of randomly generated grids base on a dimensions tuple parameter

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
        '''
        Displays the current data onto the kivy canvas
        :param args: used as place holder for args provided by Clock object
        :return:
        '''
        self.drawGrid()
        if self._obstacles:
            self.drawObstacles()
        if self._start and self._target:
            self.drawObjective()

    def drawGrid(self):
        '''
        Draws a grid based on the dimensions attribute and the bounding window

        Note:: At the time of writing this, there is a bug when maximizing the screen which causes the grid
                to not render properly
        :return:
        '''
        div_col, div_row = Window.width/self.numCols, Window.height/self.numRows
        with self.canvas.before as c:
            self.canvas.before.clear()
            Color(1,1,1,1)
            for cols in range(self.numCols+1):
                Line(points=[cols*div_col, 0, cols*div_col, self.height])
            for rows in range(self.numRows+1):
                Line(points=[0, rows*div_row, self.width, rows*div_row])

    def drawObstacles(self):
        '''
        Draws obstacles as boxes
        To DO:: use nonlocal on div_xx since this function is internally called by the update method
        :return:
        '''
        div_col, div_row = Window.width / self.numCols, Window.height / self.numRows
        with self.canvas:
            self.canvas.clear()
            Color(1, 0.5, 0.6, 1)
            for x,y in self._obstacles:
                Rectangle(pos=(x*div_col+0.5,y*div_row+0.5), size=(div_col-1,div_row-1))

    def drawObjective(self):
        '''
        Same as drawObstacles
        :return:
        '''
        div_col, div_row = Window.width / self.numCols, Window.height / self.numRows
        with self.canvas.after:
            #self.canvas.after.clear()
            for color, coordinates in [([0,1,0,1],self._start), ([0,0,1,1],self._target)]:
                Color(*color)
                Rectangle(pos=(coordinates[0]*div_col, coordinates[1]*div_row), size=(div_col,div_row))


    def setStart(self, coordinates):
        '''
        Setter for starting location
        :param coordinates: tuple
        :return:
        '''

        if 0 <= coordinates[0] <= self.numCols and 0 <= coordinates <= self.numRows:
            if coordinates not in self._obstacles:
                self._start = (coordinates)
            else:
                raise ValueError("Invalid start loc. Point is already an obstacle!")

        else:
            raise ValueError("Input coordinates are out of bounds!")

    def setDestination(self, coordinates):
        '''
        Setter for target location
        :param coordinates: tuple
        :return:
        '''
        if 0 <= coordinates[0] <= self.numCols and 0 <= coordinates <= self.numRows:
            if coordinates not in self._obstacles:
                self._target = (coordinates)
            else:
                raise ValueError("Invalid destination. Point is already an obstacle!")
        else:
            raise ValueError("Input coordinates are out of bounds!")

    def generateObstacles(self, numObstacles, *args):
        '''
        Randomly generate random obstacles on grid
        :param numObstacles: int indicating number of random obstacles
        :param args:
        :return:
        '''
        if self._obstacles == None:
            self._obstacles.extend([(randint(0,self.numCols),randint(0,self.numRows)) for i in range(numObstacles)])
        else:
            self._obstacles = [(randint(0,self.numCols),randint(0,self.numRows)) for i in range(numObstacles)]

    ''' ********************************* Below contain D* Lite operations ***************************************** '''

    def initialize(self):
        '''
        Initializes the grid according to D* Lite implementation:
            1. sets the g and rhs for every node to _INFINITY parameter.
            2. sets the rhs of goal to 0
            3. add goal to the open set

        :return:
        '''
        for col in range(self.numCols):
            for row in range(self.numRows):
                self._gVal[(col,row)] = self._INFINITY
                self._rhs[(col,row)] = self._INFINITY
        self._rhs[self._target] = 0
        self._open.put((self.calculateKeys(self._target), self._target))

    def cost(self, u, v):
        '''

        :param u: pos tuple of inital node
        :param v: pos tuple of destination node
        :return: 1 or 1.4
        '''
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
            raise

    def heuristic(self, u):
        '''
        Using L1 distance since movement is discrete

        Note:: L1 norm implies non unique paths
        :param u: pos tuple
        :return: L1 distance
        '''
        try:
            return abs(u[0]-self._target[0]) + abs(u[1]-self._target[1])
        except:
            print('invalid arg:', u, 'arg should be a tuple.')
            return -1

    def _getNeighbor(self, u):
        '''
        finds the adjacent neighbors to a node that are not obstacles
        :param u: pos tuple for node u
        :return:
        '''
        x,y = u
        possibleNeighbor = [(col, row) for col in range(x-1,x+2) for row in range(y-1, y+2) if (row!=x or col!=y)]
        possibleNeighbor = [(x,y) for x,y in possibleNeighbor if (0<=x<self.numCols and 0<=y<self.numRows)]
        return [x for x in possibleNeighbor if x not in self._obstacles]

    def _getPredecessor(self, u):
        '''
        Locate predecessors from predecessor LUT
        sets all neighbors of u to be predecessors if predecessors are not found
            also sets u to be the successors to those neighbors because the grid is bi-directional
        :param u:
        :return:
        '''
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
        '''
        sets the rhs u to the best possible rhs
        the result of this will be a potential gradient that can be used to determine the path

        if u is an inconsistent node it is added to the open set for processing
        :param u: pos tuple
        :return:
        '''
        if u != self._target:
            self._rhs[u] = min([self.cost(u,s) + self._gVal[s] for s in self._successor[u]])
        if self._gVal[u] != self._rhs[u]:
            self._open.put((self.calculateKeys(u),u))

    def computeShortestPath(self):
        '''
        main computation in D* Lite algorithm.
        Main loop is a BFS using priority to prune and determine the best expansion each iteration
            each loop a node is selected and check for consistency:
                if overconsistent then just set g = rhs and expand
                elif inconsistent recalculate and expand
        an extra conditional clause is added in the event that no possible path is found and the queue becomes empty
        :return:
        '''
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
        '''
        Important in the case where a obstacle is newly found which causes data to be inconsistent
        :param u: pos tuple
        :return:
        '''
        #print('calculaing keys', u)
        try:
            return min(self._gVal[u], self._rhs[u])
        except Exception as e:
            print(e, u, 'Keys')
            exit()

    def execute(self):
        '''
        Quick call to demonstrate algorithm using kivy canvas
        The movement loop has been relocated to a schedule event callback in order to visually animate the
        path traversal.
        :return:
        '''
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
