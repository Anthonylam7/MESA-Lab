from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from kivy.clock import Clock
from kivy.properties import NumericProperty

class Movable(Scatter):
	pass

class Panel(Widget):
	def __init__ (self,**kwargs):
		super(Panel,self).__init__(**kwargs)
		self.status = True
		self.next = None
		self.position = None
		
class VoltageReading(Label):
	pass


class Array(Widget):
	voltReading = NumericProperty(24)
	
	def __init__(self,**kwargs):
		super(Array,self).__init__(**kwargs)
		self.headList = []
		
		self.shade = Movable()
		self.shadeCallback = None
	
	def generateArray( self, x = 1, y = 1):
		panelWidth = self.width / float(x)
		panelHeight = self.height / float(y)
		
		for i in range(1,y+1):
			for j in range(1,x+1):
				# add panel list here.
				# size = panelWidth, panelHeight
				# pos of panel = ( (j-1)*panelWidth + 10 , (i-1)*panelHeight )
				p = Panel( 
					size = (panelWidth,panelHeight), 
					pos = (self.x + (j-1)*(panelWidth *1.05) , self.y + (i-1)*(panelHeight * 1.05) ) 
					)
				p.position = (j,i)
				
				if  len(self.headList) < i :
					self.headList.append(p)
					self.add_widget(p)
					
				else :
					self.addPanel( i-1, p)
					self.add_widget(p)
					
		Clock.schedule_interval(self.totalVoltage, 1/4.)
		Clock.schedule_interval(self.shaded, 1/4.)
				
	def addPanel(self, headPos, Panel):
		current = self.headList[headPos]
		'''
		self.headList[headPos] = Panel
		Panel.next = current
		'''
		while current.next:
			current = current.next
		current.next = Panel
		
	def totalVoltage(self,*args):
		voltPerRow = []
		for head in self.headList:
			rowVolt = 0
			current = head
			while current:
				if current.status:
					rowVolt += 3.0
				else:				
					rowVolt += 0
					
					
				current = current.next
			voltPerRow.append(rowVolt)
			
		self.voltReading = sum(voltPerRow)/float(len(voltPerRow))

		
		
	def shaded(self,*args):
		for child in self.children:
			if child.collide_widget(self.shade):
				child.status = False
			else:
				child.status = True
	
	def on_voltReading(self, *args):
		if self.shadeCallback is None:
			print (args)
			return
		else:
			self.shadeCallback(self.voltReading/6.)
			
				
			




	


class ShadeTest(App):
	def build(self):
		f = FloatLayout()
		f.a = Array(size = (400,200), pos = (300, 300))
		f.a.generateArray(8,4)
		f.add_widget(f.a)
		f.add_widget(f.a.shade)
		return f
		
		
		
if __name__ == '__main__':
	ShadeTest().run()
