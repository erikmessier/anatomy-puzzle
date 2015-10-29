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
import viztask

import collections
#custom modules
import config
import puzzle

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
		
		self.main = MainMenu(canvas, self)
		self.mode = ModeMenu(canvas, self)
		self.layer = LayerMenu(canvas, self)
		self.ingame = InGameMenu(canvas, self)
		
		#stating menu display path
		self.menuOrder = [self.main, self.mode, self.layer, self.ingame]
		
	def start(self):
		"""
		Start the game
		"""
		self.selected = Selection()
		ignoreLayer = False
		# Which subsets were selected
		self.selected.modeSelected(self.mode.radioButtons)
		self.selected.objectsSelected(self.layer.regions, self.layer.layers, self.layer.checkBox, self.layer.selectAllOf)
		if self.selected.mode == 'Movement Tutorial':
			puzzle.tutorial.init()
			self.setPanelVisible(viz.OFF)
			self.canvas.setCursorVisible(viz.OFF)
			self.layer.active = False
			self.ingame.active = True
		else:
			if self.selected.load:
				puzzle.controller.start(self.selected.mode, self.selected.load)
				self.setPanelVisible(viz.OFF)
				self.layer.canvas.setCursorVisible(viz.OFF)
				self.layer.active = False
				self.ingame.active = True
				
	def restart(self):
		if self.layer.mode[0] == 'Movement Tutorial':
			puzzle.tutorial.Tutorial.end()
			puzzle.tutorial.init()
		else:
			puzzle.controller.end()
			puzzle.controller.start(game.mode[0],game.loadLayers)
		self.ingame.toggle()
		
	def endGame(self):
		if self.layer.mode[0] == 'Movement Tutorial':
			puzzle.tutorial.Tutorial.end()
			puzzle.tutorial.recordData.close()
		else:
			puzzle.controller.end()
		self.changeMenu(self.ingame, self.main)
		
	def backMenu(self, curMenu):
		i = self.menuOrder.index(curMenu)
		self.changeMenu(curMenu,  self.menuOrder[i-1])
		
	def nextMenu(self, curMenu):
		i = self.menuOrder.index(curMenu)
		self.changeMenu(curMenu,  self.menuOrder[i+1])

	def changeMenu(self, leaveMenu, goToMenu):	
		leaveMenu.setPanelVisible(viz.OFF, animate = False)
		goToMenu.setPanelVisible(viz.ON, animate = True)
		leaveMenu.menuVisible = False
		goToMenu.menuVisible = True
		leaveMenu.active = False
		goToMenu.active = True
		
	def toggle(self):
		if(self.main.active == True):
			main.toggle()
		elif(self.mode.active == True):
			mode.toggle()
		elif(self.layer.active == True):
			layer.toggle()
		else:
			ingame.toggle()
		
	def exitGame(self):
		viz.quit()
		print 'Visual Anatomy Trainer has closed'
		
class MenuBase(vizinfo.InfoPanel):
	"""Base Menu Class"""
	def __init__(self, canvas, name, title, startVisible = False):
		"""initialize the menu"""
		vizinfo.InfoPanel.__init__(self, '', title = title, fontSize = 100, parent = canvas, align = viz.ALIGN_CENTER_CENTER, icon = False)
		
		#hide system mouse
		viz.mouse.setVisible(False)
		viz.mouse.setTrap(True)
		
		self.canvas = canvas
		
		#menu is visible
		if startVisible:
			self.menuVisible = True
			self.active = True
		else:
			self.active = False
			self.setPanelVisible(viz.OFF, animate = False)
			self.menuVisible = False

		#individual menu parameters
		self.name = name
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])
		
		
	def toggle(self):
		if self.menuVisible == True:
			self.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True

class MainMenu(MenuBase):
	"""Main game menu"""
	def __init__(self, canvas, controller):
		# Store controller instance
		self.controller = controller
	
		"""initialize the Main menu"""
		super(MainMenu, self).__init__(canvas, 'main', 'Main Menu', True)
		
		
		# add play button, play button action, and scroll over animation
		self.play = self.addItem(viz.addButtonLabel('Play'), fontSize = 50)
		vizact.onbuttondown(self.play, self.controller.nextMenu, self)
		
		# add options button row
		self.Help = self.addItem(viz.addButtonLabel('Help'), fontSize = 50)
		vizact.onbuttondown(self.Help, self.helpButton)
		
		# add help button row
		self.Exit = self.addItem(viz.addButtonLabel('Exit'), fontSize = 50)
		vizact.onbuttondown(self.Exit, controller.exitGame)
		
		#rendering
		bb = self.getBoundingBox()
		self.canvas.setRenderWorldOverlay([bb.width*1.8, bb.height*1.8], fov = bb.height*.1, distance = 3)
		
		#change scale depending on display mode
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])
	
		
	def helpButton(self):
		print 'Help Button was Pressed'

class ModeMenu(MenuBase):
	"""Mode selection menu"""
	def __init__(self, canvas, controller):
		super(ModeMenu, self).__init__(canvas, 'mode', 'Mode Selection')
		
		# Store controller instance
		self.controller = controller
		
		#Store modes from config to populate modemenu with
		self.modes = config.menuLayerSelection.Modes
		self.getPanel().fontSize(50)
		
		##########################
		"""creating modes panel"""
		##########################
		
		#creating labels for modes
		self.modeLabels = {}
		
		for l in self.modes.iterkeys():
			self.modeLabels[l] = viz.addText(l, parent = canvas)
		
		#creating radio buttons for modes
		self.modeGroup = viz.addGroup(parent = canvas)
		self.radioButtons = {}
		
		for rb in self.modes.iterkeys():
			self.radioButtons[rb] = viz.addRadioButton(self.modeGroup, parent = canvas)
		
		self.radioButtons['Free Play'].set(1)
		
		#creating grid panel to add mode to
		modeGrid = vizdlg.GridPanel(parent = canvas)
		
		#adding modes and radio buttons to grid panel
		for i in self.modes.iterkeys():
			modeGrid.addRow([self.modeLabels[i], self.radioButtons[i]])
		
		##############################
		"""next and back buttons"""
		##############################
		
		#creating grid panels to add next and back buttons to
		setGrid = vizdlg.GridPanel(parent = canvas)
		
		#create back and next buttons and add to grid panel
		backButton = viz.addButtonLabel('Back')
		startButton = viz.addButtonLabel('Next')
		setGrid.addRow([backButton, startButton])
		
		#add back and state button actions
		vizact.onbuttondown(backButton, controller.backMenu, self)
		vizact.onbuttondown(startButton, self.controller.nextMenu, self)
		
		###############################
		"""add items to ModeMenu"""
		###############################
		self.addItem(modeGrid)
		self.addItem(setGrid)

class LayerMenu(MenuBase):
	"""Layer selection menu"""
	def __init__(self,canvas,controller):
		super(LayerMenu, self).__init__(canvas, 'layer', 'Layer Selection')
		
		# Store controller instance
		self.controller = controller
		
		#Store region, layer, and mode data from config to populate menu
		self.regions = config.menuLayerSelection.Regions #collections.OrderedDict type
		self.layers = config.menuLayerSelection.Layers #collections.OrderedDict type
		self.modes = config.menuLayerSelection.Modes
		self.getPanel().fontSize(50)
		
		#####################
		'''LAYER TAB PANEL SETUP'''
		#####################
		
		#creating tab panel tp 
		byRegionPanel = vizdlg.TabPanel(align = viz.ALIGN_LEFT_TOP, parent = canvas)
		
		#creating sub panels for tab panels(all layer data is stored in config.layers) storing sub panels in laypan
		layPan = {}
		
		for i, l in enumerate(self.regions.iteritems()):
			layPan[l[0]] = vizdlg.GridPanel(parent = canvas, fontSize = 10)
		
		#creating dict of checkboxes for layers
		self.checkBox = {}
		
		for key in self.regions.iterkeys():
			self.checkBox[key] = {}
			for cb in self.layers.iterkeys():
				self.checkBox[key][cb] = viz.addCheckbox(parent = canvas)
		
		#populate panels with layers and checkboxes
		for i in self.regions.iterkeys():
			for j in self.layers.iterkeys():
				layPan[i].addRow([viz.addText(j), self.checkBox[i][j]])
			byRegionPanel.addPanel(i, layPan[i], align = viz.ALIGN_LEFT_TOP)
		
		#############################################
		"""CREATE TOTAL LAYER SELECTION CHECKBOXES"""
		#############################################
		
		#creating grib panel to put checkboxes on
		selectAllPanel = vizdlg.GridPanel(parent = canvas, fontSize = 10)
		
		#creating checkboxes
		self.selectAllOf = {}
		
		for i in self.layers.iterkeys():
			self.selectAllOf[i] = viz.addCheckbox(parent = canvas)
		
		#adding checkboxes to panel
		for i in self.layers:
			selectAllPanel.addRow([viz.addText('Load All ' + i, fontSize = 5), self.selectAllOf[i]])
		
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
		vizact.onbuttondown(backButton, self.controller.backMenu, self)
		vizact.onbuttondown(startButton, self.controller.start)
		
		############################
		'''ADD ITEMS TO GAME MENU'''
		############################
		
		#add tab panel to info panel
		byRegionPanel.setCellPadding(5)
		self.addItem(byRegionPanel, align = viz.ALIGN_LEFT_TOP)
		
		#add grid panel to info panel
		self.addItem(selectAllPanel, align = viz.ALIGN_LEFT_TOP)
	
		#start and back buttons
		self.addItem(setGrid, align = viz.ALIGN_RIGHT_TOP)
		
		#change scale depending on display mode
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])
		
		#rendering
		bb = self.getBoundingBox()
		self.canvas.setRenderWorldOverlay([bb.width*1.8, bb.height*1.8], fov = bb.height*.1, distance = 1)

class InGameMenu(MenuBase):
	"""
	In-game menu to be shown when games are running
	"""
	def __init__(self,canvas,controller):
		super(InGameMenu, self).__init__(canvas, 'ingame', 'In Game Menu')
		
		# Store controller instance
		self.controller = controller
		
		#menu buttons
		self.restart = self.addItem(viz.addButtonLabel('Restart'))
		self.end = self.addItem(viz.addButtonLabel('End game'))
		
		#Callbacks
		vizact.onbuttondown(self.restart, self.controller.restart)
		vizact.onbuttondown(self.end, self.controller.endGame)
		
		#change scale depending on display mode
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])
	
class Selection():
	"""Selection methods to determine GUI inputs, and storage format for GUI inputs"""
	def __init__(self):
		self.load = []
		self.mode = []
		self.unionFlag = False
	def modeSelected(self, modeRadiosDict):
		"""Determines the selected game mode from the GUI"""
		for i in modeRadiosDict.keys():
			if modeRadiosDict[i].get() == 1:
				self.mode = i
	def objectsSelected(self, regions, layers, specif_LayerChecks, all_LayerChecks):
		"""Determiens which selections were made on the tabs, and entire layer selections made"""
		for i in regions.iterkeys():
			for j in layers.iterkeys():
				if specif_LayerChecks[i][j].get() == 1:
					layer_region = (set.intersection, [layers[j]], regions[i])
					self.load.append(layer_region)
		for i in all_LayerChecks.keys():
			if all_LayerChecks[i].get() == 1:
				layer_region = (set.union, [layers[i]], 'All Regions')
				self.load.append(layer_region)
				self.unionFlag = True