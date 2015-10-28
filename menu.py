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
		
		self.main	= MainMenu(canvas)
		self.mode	= ModeMenu(canvas)
		self.layer	= LayerMenu(canvas)
		self.ingame	= InGameMenu(canvas)
class MenuBase(vizinfo.InfoPanel):
	"""Base Menu Class"""
	def __init__(self, canvas, name, title):
		"""initialize the menu"""
		vizinfo.InfoPanel.__init__(self, '', title = title, fontSize = 100, parent = canvas, align = viz.ALIGN_CENTER_CENTER, icon = False)
		
		#hide system mouse
		viz.mouse.setVisible(False)
		viz.mouse.setTrap(True)
		
		#menu is visible
		self.menuVisible = True
		self.canvas = canvas
		self.active = True
		
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
	def __init__(self, canvas):
		"""initialize the Main menu"""
		super(MainMenu, self).__init__(canvas, 'main', 'Main Menu')
		
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
		
	def playButton(self):
		self.setPanelVisible(viz.OFF, animate = False)
		mode.setPanelVisible(viz.ON, animate = True)
		self.active = False
		mode.active = True
		
	def exitButton(self):
		viz.quit()
		print 'Visual Anatomy Trainer has closed'
	
	def helpButton(self):
		print 'Help Button was Pressed'

class ModeMenu(MenuBase):
	"""Mode selection menu"""
	def __init__(self, canvas):
		super(ModeMenu, self).__init__(canvas, 'mode', 'Mode Selection')
		self.modes = config.menuLayerSelection.Modes
		self.active = False
		self.getPanel().fontSize(50)
		self.setPanelVisible(viz.OFF, animate = False)
		
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
		vizact.onbuttondown(backButton, self.back)
		vizact.onbuttondown(startButton, self.next)
		
		###############################
		"""add items to ModeMenu"""
		###############################
		self.addItem(modeGrid)
		self.addItem(setGrid)
		
	def next(self):
		self.setPanelVisible(viz.OFF, animate = False)
		layer.setPanelVisible(viz.ON, animate = True)
		self.active = False
		layer.active = True
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

class LayerMenu(vizinfo.InfoPanel):
	"""Layer selection menu"""
	def __init__(self,canvas):
		vizinfo.InfoPanel.__init__(self, '',title = 'Layer Selection',fontSize = 75,align=viz.ALIGN_CENTER_CENTER,icon=False,parent= canvas)
		self.regions = config.menuLayerSelection.Regions #collections.OrderedDict type
		self.layers = config.menuLayerSelection.Layers #collections.OrderedDict type
		self.modes = config.menuLayerSelection.Modes
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
		vizact.onbuttondown(backButton, self.back)
		vizact.onbuttondown(startButton, self.start)
		
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
		
	def start(self):
		"""
		Start the game
		"""
		self.selected = Selection()
		ignoreLayer = False
		# Which subsets were selected
		self.selected.modeSelected(mode.radioButtons)
		self.selected.objectsSelected(self.regions, self.layers, self.checkBox, self.selectAllOf)
		if self.selected.mode == 'Movement Tutorial':
			puzzle.tutorial.init()
			self.setPanelVisible(viz.OFF)
			self.canvas.setCursorVisible(viz.OFF)
			self.active = False
			ingame.active = True
		else:
			if self.selected.load:
				puzzle.controller.start(self.selected.mode, self.selected.load)
				self.setPanelVisible(viz.OFF)
				self.canvas.setCursorVisible(viz.OFF)
				self.active = False
				ingame.active = True
	
	def setDataset(self, name):
		self.dataset = name
	def back(self):
		self.setPanelVisible(viz.OFF, animate = False)
		mode.setPanelVisible(viz.ON, animate = True)
		self.active = False
		mode.active = True
		
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
	"""
	In-game menu to be shown when games are running
	"""
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
		if layer.mode[0] == 'Movement Tutorial':
			puzzle.tutorial.Tutorial.end()
			puzzle.tutorial.init()
		else:
			puzzle.controller.end()
			puzzle.controller.start(game.mode[0],game.loadLayers)
		self.toggle()
	
	def endButton(self):
		if layer.mode[0] == 'Movement Tutorial':
			puzzle.tutorial.Tutorial.end()
			puzzle.tutorial.recordData.close()
		else:
			puzzle.controller.end()
		self.setPanelVisible(False)
		self.menuVisible = False
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
	elif(mode.active == True):
		mode.toggle()
	elif(layer.active == True):
		layer.toggle()
	else:
		ingame.toggle()
	
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
				
				
viz.go()
a = MenuController()