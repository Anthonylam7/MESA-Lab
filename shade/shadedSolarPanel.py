from kivy.app import App
from math import sin
from kivy.garden.graph import Graph, MeshLinePlot




class shadedSolarPanel(App):
	def build(self):
		graph = Graph(xlabel='V', ylabel='I', x_ticks_minor=5,
			x_ticks_major=25, y_ticks_major=10,
			y_grid_label=True, x_grid_label=True, padding=5,
			x_grid=True, y_grid=True, xmin=-0, xmax=1, ymin=0, ymax=200)
		plot = MeshLinePlot(color=[1, 0, 0, 1])
		plot.points = [(x/140., 80 - 5**(x/10000./0.00259)) for x in range(0, 7000)]
		graph.add_plot(plot)
		return graph
		
		
if __name__ == '__main__':
	shadedSolarPanel().run()