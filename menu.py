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

def init():
	"""Create global menu instance"""
canvas = viz.addGUICanvas()
canvas.setRenderWorldOverlay([2000,2000],60,1)
#main = MainMenu(canvas)
#game = GameMenu(canvas, config.layers)
#ingame = InGameMenu(canvas)
#vizact.onkeydown('l', ingame.toggle)
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
		self.help = self.addItem(viz.addButtonLabel('Help'), fontSize = 50)
		vizact.onbuttondown(self.help, self.helpButton)
		
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
		print 'Help Button was Pressed'

class GameMenu(vizinfo.InfoPanel):
	"""Game selection submenu"""
	def __init__(self,canvas, layers):
		vizinfo.InfoPanel.__init__(self, '',title = 'Game Menu',fontSize = 100,align=viz.ALIGN_CENTER_CENTER,icon=False,parent= canvas)
		self.layers = config.layers
		
		self.canvas = canvas
		self.active = False
		self.getPanel().fontSize(50)
		self.setPanelVisible(viz.OFF, animate = False)
		self.menuVisible = False	
	
		#creating tab panel tp 
		tp = vizdlg.TabPanel(align = viz.ALIGN_LEFT_TOP, parent = canvas)
		
		#creating dict space for checkboxes
		self.checkBox = {}
		
		for cb in [cb for l in self.layers.values() for cb in l]:
			self.checkBox[cb] = viz.addCheckbox()
		
		#creating sub panels for tab panels(all layer data is stored in config.layers) storing sub panels in laypan
		layPan = {}
		
		for i, l in enumerate(self.layers):
			layPan[l] = vizdlg.GridPanel(parent = canvas)

		#add items to sub panels of tab panels
		for i in self.layers:
			for j in self.layers[i]:
				layPan[i].addRow([viz.addText(j), self.checkBox[j]])
			tp.addPanel(i, layPan[i], align = viz.ALIGN_LEFT_TOP)
		
		#add directions above menu items
		self.addItem(viz.addText('Select the Following Parts of the Skeletal System That You Wish to Puzzle', parent = canvas), fontSize = 30)
		
		#add tab panel to info panel
		self.addItem(tp, align = viz.ALIGN_CENTER_TOP)
		tp.setCellPadding(10)

		#creating grid panel to add back and start buttons to
		setGrid = vizdlg.GridPanel(parent = canvas)
		
		#create back and start buttons
		backButton = viz.addButtonLabel('Back')
		startButton = viz.addButtonLabel('Start')
		setGrid.addRow([backButton, startButton])
		self.addItem(setGrid, align = viz.ALIGN_RIGHT_TOP)
		
		#add button event callback
		self.checkState = {}
		for cb in [cb for l in self.layers.values() for cb in l]:
			self.checkState[cb] = False
		viz.callback(viz.BUTTON_EVENT, self.checkBoxState)
		
		#add back and state button actions
		vizact.onbuttondown(backButton, self.back)
		vizact.onbuttondown(startButton, self.start)

	def start(self):
		self.loadLayers = []
		print 'Puzzle game has been started!'
		'''Which subsets were selected'''
		for i in self.checkState:
			if self.checkState[i] == True:
				self.loadLayers.append(i)
		if len(self.loadLayers) != 0:
			print self.loadLayers
			self.setPanelVisible(viz.OFF)
			self.canvas.setCursorVisible(viz.OFF)
			self.active = False
			ingame.active = True
		else: 
			print 'No Layer Was Selected!'
	
	def setDataset(self, name):
		self.dataset = name
		
	def checkBoxState(self, obj, state):
		"""on button event checks what type of button was selected and
		if the button is a checkbox then the state of the check boxes
		and associates selected checkboxes with their label"""
		for l in self.checkBox:
			if obj == self.checkBox[l]:
				if state == viz.DOWN:
					self.checkState[l] = True
				else:
					self.checkState[l] = False
	def back(self):
		print "Goi'n Back!"
		self.setPanelVisible(viz.OFF, animate = False)
		main.setPanelVisible(viz.ON, animate = True)
		self.active = False
		main.active = True
	def toggle(self):
		if(self.menuVisible == True):
			self.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True

class InGameMenu(vizinfo.InfoPanel):
	"""In-game menu to be shown when games are running"""
	def __init__(self,canvas):
		vizinfo.InfoPanel.__init__(self, '',title='In Game',fontSize = 100,align=viz.ALIGN_CENTER_CENTER,icon=False,parent=canvas)
		
		self.canvas = canvas
		self.active = False
		self.getPanel().fontSize(50)
		self.setPanelVisible(viz.OFF, animate = False)
		self.menuVisible = False
		
		
		self.restart = self.addItem(viz.addButtonLabel('Restart'))
		self.end = self.addItem(viz.addButtonLabel('End game'))
		
		#Callbacks
#		vizact.onbuttondown(self.options, self.optionsButton)
#		vizact.onbuttondown(self.restart, self.restartButton)
		vizact.onbuttondown(self.end, self.endButton)
		
		

#	def restartButton(self):
#		puzzle.end()
#		puzzle.load(game.loadLayers)
#		self.toggle()
	
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

#main = MainMenu(canvas)
#game = GameMenu(canvas, config.layers)
#ingame = InGameMenu(canvas)
#
#
#vizact.onkeydown('l', ingame.toggle)
main = MainMenu(canvas)
game = GameMenu(canvas, config.layers)
ingame = InGameMenu(canvas)
vizact.onkeydown('l', ingame.toggle)