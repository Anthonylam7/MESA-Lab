from kivy.app import App
from math import sin
from kivy.garden.graph import Graph, MeshLinePlot

from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

from Shadetest import Movable, Panel, Array
from kivy.lang import Builder

Builder.load_file('shadetest.kv')




class IVGraph(Graph):
	def __init__(self,**kwargs):
		super(IVGraph,self).__init__(**kwargs)
		# Initializes bounds ands axis
		self.xlabel='V'
		self.ylabel='I'
		self.x_ticks_minor=5
		self.x_ticks_major=25
		self.y_ticks_major=10
		self.y_grid_label=True
		self.x_grid_label=True
		self.padding=5
		self.x_grid=True
		self.y_grid=True
		self.xmin=-0
		self.xmax=1
		self.ymin=0
		self.ymax=200
		self.size_hint = None, None
		
		# Inserts a basic I-V plot
		self.plot = MeshLinePlot(color=[1, 0, 0, 1])
		self.plot.points = [(x/200., 80 - .4*(2.718281**(x/10000./0.00259)-1)) for x in range(0, 7000)]
		self.add_plot(self.plot)
		
	def updatePlot(self, I=0, *args):
		
		self.plot.points = [ (x/200., 30*I - .4*(2.718281**(x/10000./0.00259)-1)) for x in range(0,7000) ]


class UpdateGraph(App):
	def build(self):
		f = FloatLayout()
		graph = IVGraph( size = (400,400), pos = (400,350) )
		a = Array(size = (400,200), pos = (10, 100))
		a.generateArray(8,4)
		a.shadeCallback = graph.updatePlot
		
		f.add_widget(graph)
		f.add_widget(a)
		f.add_widget(a.shade)
		return f
		




if __name__ == '__main__':
	UpdateGraph().run()