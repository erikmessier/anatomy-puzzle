"""
menu.py

This is where all of the menu handling will go
"""
import viz
viz.go()
import vizact
import sys
import abc
import vizmenu
import vizinfo
import vizshape
import vizproximity
import vizdlg
import config

#def init():
#	"""Create global menu instance"""
#
canvas = viz.addGUICanvas()
canvas.setRenderWorldOverlay([2000,2000],60,1)
# Compatibility for all display types
canvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
canvas.setCursorPosition([0,0])	

class MainMenu(vizinfo.InfoPanel):
	"""Main game menu"""
	def __init__(self, canvas):
		"""initialize the Main menu"""
		vizinfo.InfoPanel.__init__(self, '', fontSize = 100, parent = canvas, align = viz.ALIGN_CENTER_CENTER, \
			title = 'Main Menu', icon = False)
		
		# Since we are using the vizard pointer, hide system mouse
		viz.mouse.setVisible(False)
		viz.mouse.setTrap(True)
		self.menuVisible = True
		self.canvas = canvas
		self.active = True
		
		# add play button, play button action, and scroll over animation
		self.play = self.addItem(viz.addButtonLabel('Play'), fontSize = 50)
		vizact.onbuttondown(self.play, self.playButton)
		
		# add options button row
		self.options = self.addItem(viz.addButtonLabel('Options'), fontSize = 50)
		vizact.onbuttondown(self.options, self.helpButton)
		
		# add help button row
		self.exit = self.addItem(viz.addButtonLabel('Exit'), fontSize = 50)
		vizact.onbuttondown(self.exit, self.exitButton)

	def toggle(self):
		if(self.menuVisible == True):
			self.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True
		
			
	def playButton(self):
		print 'Play button was pressed'
		self.setPanelVisible(viz.OFF, animate = False)
		game.setPanelVisible(viz.ON, animate = True)
		self.active = False
		game.active = True
		
	def exitButton(self):
		print 'Exit button was pressed'
		print 'Exiting Visual Anatomy Trainer'
		viz.quit()
		print 'Visual Anatomy Trainer has closed'
	
	def helpButton(self):
		print 'Options button was pressed'

class GameMenu(vizinfo.InfoPanel):
	"""Game selection submenu"""
	def __init__(self,canvas, layers):
		vizinfo.InfoPanel.__init__(self, 'Choose Which Parts of the Skeletal System You Would Like To Puzzle',title= None,fontSize = 25,align=viz.ALIGN_CENTER_CENTER,icon=False,parent= canvas)
		self.layers = config.layers
		self.layerSuper = list(enumerate(self.layers))
		
		self.canvas = canvas
		self.active = False
		
		print "creating Game Menu"
		self.getPanel().fontSize(50)
		self.setPanelVisible(viz.OFF, animate = False)
		self.menuVisible = False	
		
		#creating grid panel to add menu selections to
		setGrid = vizdlg.GridPanel(parent = canvas)
		
		#creating tab panel tp 
		tp = vizdlg.TabPanel(align = viz.ALIGN_LEFT_TOP, parent = canvas)
		
		#adding sub panels to tab panel(all layer data is stored in config.layers)
		
		for i in range(len(self.layers)):
			tp.addPanel(self.layerSuper[i][i])
		
		
		#adding back button
		
		
	def start(self):
		print 'Puzzle game button was pressed'
		self.setPanelVisible(viz.OFF)
		self.canvas.setCursorVisible(viz.OFF)
		self.active = False
		ingame.active = True
		puzzle.load(self.dataset)
	
	def setDataset(self, name):
		self.dataset = name
		

	def toggle(self):
		if(self.menuVisible == True):
			self.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True
	def imageOfSet(self,layerName):
		datasetImage = '.\\img\\' + layerName + '.png'
		return datasetImage
		print imageOfSet('Skull')
		

class InGameMenu(vizinfo.InfoPanel):
	"""In-game menu to be shown when games are running"""
	def __init__(self,canvas):
		vizinfo.InfoPanel.__init__(self, '',title='In Game',fontSize = 100,align=viz.ALIGN_CENTER_CENTER,icon=False,parent=canvas)
		
		self.canvas = canvas
		self.active = False
		self.getPanel().fontSize(50)
		self.setPanelVisible(viz.OFF, animate = False)
		self.menuVisible = False
		
		self.options = self.addItem(viz.addButtonLabel('Options'))
		self.restart = self.addItem(viz.addButtonLabel('Restart'))
		self.end = self.addItem(viz.addButtonLabel('End game'))
		
		#Callbacks
#		vizact.onbuttondown(self.options, self.optionsButton)
		vizact.onbuttondown(self.restart, self.restartButton)
		vizact.onbuttondown(self.end, self.endButton)
		
		

	def restartButton(self):
		puzzle.end()
		puzzle.load(game.dataset)
		self.toggle()
	
	def endButton(self):
		puzzle.end()
		self.toggle()
		self.active = False
		main.active = True
		main.menuVisible = True
		main.setPanelVisible(True)
		main.canvas.setCursorVisible(True)

	def toggle(self):
		if(self.menuVisible == True):
			self.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True

def toggle(visibility = viz.TOGGLE):
	print "toggling menu"
	if(main.active == True):
		main.toggle()
	elif(game.active == True):
		game.toggle()
	else:
		ingame.toggle()

#canvas = viz.addGUICanvas()
#canvas.setRenderWorldOverlay([2000,2000],60,1)
## Compatibility for all display types
#canvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
#canvas.setCursorPosition([0,0])	

main = MainMenu(canvas)
game = GameMenu(canvas, config.layers)
#ingame = InGameMenu(canvas)