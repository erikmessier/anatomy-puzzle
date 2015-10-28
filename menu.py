"""
menu.py

This is where all of the menu handling will go
"""
import viz
import vizact
import sys
import abc
import vizmenu
import vizinfo
import vizshape
import vizproximity
import vizdlg
import viztip

#custom modules
import config

#def init():
#	"""Create global menu instance"""
#	global main
#	global mode
#	global layer
#	global ingame
#	global canvas
#
#	canvas = viz.addGUICanvas()
##	canvas.setRenderWorldOverlay([2000,2000],60,1)
#	
#	main = MainMenu(canvas)
#	mode = ModeMenu(canvas)
#	layer = LayerMenu(canvas)
#	ingame = InGameMenu(canvas)
#	
#	# Compatibility for all display types
#	canvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
#	canvas.setCursorSize([25,25])
#	canvas.setCursorPosition([0,0])
	
class MenuController(object):
	def __init__(self):
		self.canvas = viz.addGUICanvas()
		canvas = self.canvas
		
		# Compatibility for all display types
		canvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
		canvas.setCursorSize([25,25])
		canvas.setCursorPosition([0,0])
		
		self.main	= MainMenu(canvas)
		self.mode	= ModeMenu(canvas)
		self.layer	= LayerMenu(canvas)
		self.ingame	= InGameMenu(canvas)

class GameMenu(vizinfo.InfoPanel):
	def __init__(self):
		pass
		
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
		self.name = 'main'
		
		# add play button, play button action, and scroll over animation
		self.play = self.addItem(viz.addButtonLabel('Play'), fontSize = 50)
		vizact.onbuttondown(self.play, self.playButton)
		
		# add options button row
		self.help = self.addItem(viz.addButtonLabel('Help'), fontSize = 50)
		vizact.onbuttondown(self.help, self.helpButton)
		
		# add help button row
		self.exit = self.addItem(viz.addButtonLabel('Exit'), fontSize = 50)
		vizact.onbuttondown(self.exit, self.exitButton)
		
		#rendering
		bb = self.getBoundingBox()
		self.canvas.setRenderWorldOverlay([bb.width*1.8, bb.height*1.8], fov = bb.height*.1, distance = 3)
		
		#change scale depending on display mode
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])

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
		self.setPanelVisible(viz.OFF, animate = False)
		game.setPanelVisible(viz.ON, animate = True)
		self.active = False
		game.active = True
		
	def exitButton(self):
		viz.quit()
		print 'Visual Anatomy Trainer has closed'
	
	def helpButton(self):
		print 'Help Button was Pressed'

class GameMenu(vizinfo.InfoPanel):
	"""Game selection submenu"""
	def __init__(self,canvas):
		vizinfo.InfoPanel.__init__(self, '',title = 'Game Menu',fontSize = 100,align=viz.ALIGN_CENTER_CENTER,icon=False,parent= canvas)
		self.layers = config.layers
		self.modes = config.modes
		
		self.name = 'game'
		self.canvas = canvas
		self.active = False
		self.getPanel().fontSize(50)
		self.setPanelVisible(viz.OFF, animate = False)

		self.menuVisible = False	
		
		#####################
		'''LAYER TAB PANEL SETUP'''
		#####################
		
		#creating tab panel tp 
		tp = vizdlg.TabPanel(align = viz.ALIGN_LEFT_TOP, parent = canvas)
		
		#creating sub panels for tab panels(all layer data is stored in config.layers) storing sub panels in laypan
		layPan = {}
		
		for i, l in enumerate(self.layers):
			layPan[l] = vizdlg.GridPanel(parent = canvas)
		
		#creating dict of checkboxes for layers
		self.checkBox = {}
		
		for cb in [cb for l in self.layers.values() for cb in l]:
			self.checkBox[cb] = viz.addCheckbox(parent = canvas)
		
		#add layers and textboxes to panels
		for i in self.layers:
			for j in self.layers[i]:
				layPan[i].addRow([viz.addText(j), self.checkBox[j]])
			tp.addPanel(i, layPan[i], align = viz.ALIGN_LEFT_TOP)
		
		###############################################
		'''CREATING MODES PANEL'''
		###############################################
		
		#creating labels for modes
		self.modeLabels = {}
		
		for l in self.modes.keys():
			self.modeLabels[l] = viz.addText(l, parent = canvas)
		
		#creating radio buttons for modes
		self.modeGroup = viz.addGroup(parent = canvas)
		self.radioButtons = {}
		
		for rb in self.modes.keys():
			self.radioButtons[rb] = viz.addRadioButton(self.modeGroup, parent = canvas)
		
		#creating grid panel to add mode to
		modeGrid = vizdlg.GridPanel(parent = canvas)
		
		#adding modes and radio buttons to grid panel
		for i in self.modes.keys():
			modeGrid.addRow([self.modeLabels[i], self.radioButtons[i]])
		
		###################################
		'''CREATE START AND STOP BUTTONS'''
		###################################
		
		#creating grid panels to add start and back buttons to
		setGrid = vizdlg.GridPanel(parent = canvas)
		
		#create back and start buttons and add to grid panel
		backButton = viz.addButtonLabel('Back')
		startButton = viz.addButtonLabel('Start')
		setGrid.addRow([backButton, startButton])
		
		#add back and state button actions
		vizact.onbuttondown(backButton, self.back)
		vizact.onbuttondown(startButton, self.start)
		
		############################
		'''ADD ITEMS TO GAME MENU'''
		############################
		
		#directions
		self.addItem(viz.addText('Select Parts of the Skeletal System You Wish to Puzzle and Select a Mode:', parent = canvas), fontSize = 30, align = viz.ALIGN_LEFT_TOP)
		
		#add tab panel to info panel
		tp.setCellPadding(5)
		self.addItem(tp, align = viz.ALIGN_LEFT_TOP)
		
		#modes
		self.addItem(modeGrid, align = viz.ALIGN_LEFT_TOP)
	
		#start and back buttons
		self.addItem(setGrid, align = viz.ALIGN_RIGHT_TOP)
		
		#change scale depending on display mode
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])
		
	def start(self):
		self.mode = []
		self.loadLayers = []
		'''Which subsets were selected'''
		for i in self.checkBox.keys():
			if self.checkBox[i].get() == 1:
				self.loadLayers.append(i)
		for i in self.radioButtons.keys():
			if self.radioButtons[i].get() == 1:
				self.mode.append(i)
		if len(self.loadLayers) != 0:
			print str(self.mode[0]) + ' was selected'
			try:
				puzzle.controller.start(self.loadLayers)
			except KeyError:
				print "Dataset does not exist!"
			self.setPanelVisible(viz.OFF)
			self.canvas.setCursorVisible(viz.OFF)
			self.active = False
			ingame.active = True
		elif self.mode[0] == 'Movement Tutorial':
			puzzle.tutorial.init()
			self.setPanelVisible(viz.OFF)
			self.canvas.setCursorVisible(viz.OFF)
			self.active = False
			ingame.active = True
		else: 
			print str(self.mode[0]) + ' was selected'
			print 'No Layer Was Selected!'
	
	def setDataset(self, name):
		self.dataset = name

	def back(self):
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
		
		self.name = 'ingame'
		self.canvas = canvas
		self.active = False
		self.getPanel().fontSize(50)
		self.setPanelVisible(viz.OFF, animate = False)
		self.menuVisible = False
		
		
		self.restart = self.addItem(viz.addButtonLabel('Restart'))
		self.end = self.addItem(viz.addButtonLabel('End game'))
		
		#Callbacks
		vizact.onbuttondown(self.restart, self.restartButton)
		vizact.onbuttondown(self.end, self.endButton)
		
		#change scale depending on display mode
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])

	def restartButton(self):
		if game.mode[0] == 'Movement Tutorial':
			puzzle.tutorial.tutorial.end()
			puzzle.tutorial.init()
		else:
			puzzle.controller.end()
			puzzle.controller.load(game.loadLayers)
		self.toggle()
	
	def endButton(self):
		if game.mode[0] == 'Movement Tutorial':
			puzzle.tutorial.Tutorial.end()
			puzzle.tutorial.recordData.close()
		puzzle.controller.end()
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
	if(main.active == True):
		main.toggle()
	elif(game.active == True):
		game.toggle()
	else:
		ingame.toggle()
