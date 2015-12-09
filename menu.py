"""
All menus of the game are defined here in both appearance and function
"""

# Builtin module
import collections
import json
import Tkinter

# Vizard modules
import viz
import vizact
import vizproximity
import vizmenu
import vizinfo
import vizshape
import vizdlg
import viztask

# Custom modules
import config
import model
import anatomyTrainer

class MenuController(object):
	def __init__(self):

		self.canvas = viz.addGUICanvas(scene = viz.Scene2)
		canvas = self.canvas
		
		
		# Compatibility for all display types
		canvas.setCursorSize([25,25])
		canvas.setCursorPosition([0,0])
	
		#init keybindings
		self.keybindings = []
		self.keybindings.append(vizact.onkeydown(viz.KEY_RETURN, self.nextMenu))
		self.keybindings.append(vizact.onkeydown(viz.KEY_ESCAPE, self.exitGame))
		
		#init menus
		self.mainMenu		= MainMenu(canvas, self)
		self.modeMenu		= ModeMenu(canvas, self)
		self.layerMenu		= LayerMenu(canvas, self)
		self.loadingScreen 	= LoadingScreen()
		self.inGameMenu		= InGameMenu(canvas, self)
		
		#stating menu display path
		self.menuOrder = [self.mainMenu, self.modeMenu, self.layerMenu, self.inGameMenu]
		
		self.activeMenu = self.mainMenu
	
	######################################
	"""layerMenu and inGameMenu methods"""
	######################################
	
	def start(self):
		"""Start the game"""
		model.selected = Selection()
		ignoreLayer = False
		
		# Which subsets were selected
		model.selected.modeSelected(self.modeMenu.radioButtons)
		model.selected.objectsSelected(self.layerMenu)
		
		# Startup the game if there have been selections on layer menu
		if model.selected.mode != 'Movement Tutorial' and model.selected.load:
			yield self.changeMenu(self.layerMenu, self.inGameMenu)
			anatomyTrainer.startGame(config.MenuConfig.Modes[model.selected.mode], model.selected.load)
		elif model.selected.mode == 'Movement Tutorial':
			yield self.changeMenu(self.layerMenu, self.inGameMenu)
			anatomyTrainer.startGame(config.MenuConfig.Modes[model.selected.mode], model.selected.load)
		
	def restart(self):
		"""Restart the game"""
		anatomyTrainer.restartGame(config.MenuConfig.Modes[model.selected.mode], model.selected.load)
		self.activeMenu.toggle()
		
	def endGame(self):
		"""End the game"""
		anatomyTrainer.endGame()
		self.changeMenu(self.inGameMenu, self.mainMenu)
		
			
	def onAllSelection(self, obj, state):
		"""If entire layer was selected on layerMenu, then disable the individual checks for a specific layer, and viceversa"""
		for layer in self.layerMenu.selectAllOf.keys():
				cb = self.layerMenu.selectAllOf[layer]
				if obj == cb:
					if state == viz.DOWN:
						self.disableChecks(layer, self.layerMenu.checkBox)
						break
					if state == viz.UP:
						self.enableChecks(layer, self.layerMenu.checkBox)
						break
						
	def disableChecks(self, layer, checkBoxes):
		"""Disable checkboxes of specific layer on layerMenu"""
		for region in checkBoxes:
			if not filter(lambda x: x == layer, config.MenuConfig.RemoveCheckFromTab[region]):
				checkBoxes[region][layer].disable()
		
	def enableChecks(self, layer, checkBoxes):
		"""Enable checkboxes of a specific layer on layerMenu"""
		for region in checkBoxes:
			if not filter(lambda x: x == layer, config.MenuConfig.RemoveCheckFromTab[region]):
				checkBoxes[region][layer].enable()
				
	##########################			
	"""Shared Menu Methods"""
	##########################
	
	def backMenu(self):
		i = self.menuOrder.index(self.activeMenu)
		self.changeMenu(self.activeMenu,  self.menuOrder[i-1])
		
	def nextMenu(self):
		i = self.menuOrder.index(self.activeMenu)
		self.changeMenu(self.activeMenu,  self.menuOrder[i+1])

	def changeMenu(self, leaveMenu, goToMenu):
		leaveMenu.setPanelVisible(viz.OFF, animate = False)
		leaveMenu.menuVisible = False
		leaveMenu.active = False
		if goToMenu == self.inGameMenu:
			goToMenu.active = True
		else:
			goToMenu.setPanelVisible(viz.ON, animate = True)
			goToMenu.menuVisible = True
			goToMenu.active = True
		self.activeMenu = goToMenu
		self.updateCursorVisibility()
		self.updateKeybindings()
		
	def updateCursorVisibility(self):
		if self.activeMenu == self.loadingScreen:
			self.canvas.setCursorVisible(viz.OFF)
		elif self.activeMenu == self.inGameMenu and self.activeMenu.menuVisible == False:
			self.canvas.setCursorVisible(viz.OFF)
		else:
			self.canvas.setCursorVisible(viz.ON)
		
	def updateKeybindings(self):
		"""Menu keybinding state machine"""
		for keybinding in self.keybindings:
			keybinding.remove()
		if self.activeMenu == self.inGameMenu:
			self.keybindings.append(vizact.onkeydown(viz.KEY_ESCAPE, self.toggle))
		elif self.activeMenu == self.layerMenu:
			self.keybindings.append(vizact.onkeydown(viz.KEY_RETURN, lambda: viztask.schedule(self.start))) #use viztask to make loading screen appear before loading (necessary event when not multithreading)
			self.keybindings.append(vizact.onkeydown(viz.KEY_ESCAPE, self.backMenu))
		elif self.activeMenu == self.mainMenu:
			self.keybindings.append(vizact.onkeydown(viz.KEY_RETURN, self.nextMenu))
			self.keybindings.append(vizact.onkeydown(viz.KEY_ESCAPE, self.exitGame))
		elif self.activeMenu == self.modeMenu:
			self.keybindings.append(vizact.onkeydown(viz.KEY_RETURN, self.nextMenu))
			self.keybindings.append(vizact.onkeydown(viz.KEY_ESCAPE, self.backMenu))
			
	def toggle(self):
		self.activeMenu.toggle()
		
	def exitGame(self):
		viz.quit()
		print 'Visual Anatomy Trainer has closed'
		
	################################	
	"""Loading Screen Methods"""
	################################
	
	def calcPercentLoaded(self, meshesToLoad, meshesLoaded):
		self.loadingScreen.percentLoaded = (float(meshesLoaded)/float(meshesToLoad))
		
	def finishedLoading(self):
		self.loadingScreen.percentLoaded = 0
		
	def updateLoad(self, meshesLoaded, meshesToLoad):
		self.calcPercentLoaded(meshesToLoad, meshesLoaded)
		self.loadingScreen.progress.set(self.loadingScreen.percentLoaded)
			
class MenuBase(vizinfo.InfoPanel):
	"""Base Menu Class"""
	def __init__(self, canvas, name = '', title = '', startVisible = False, fontSize = 100):
		"""initialize the menu"""
		vizinfo.InfoPanel.__init__(self, '', title = title, fontSize = fontSize, parent = canvas, align = viz.ALIGN_CENTER_CENTER, icon = False)
		
		self.canvas = canvas
		
		#hide system mouse
		viz.mouse.setVisible(False)
		viz.mouse.setTrap(True)
		
		
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
		"""Toggle menu and cursor visibility"""
		if self.menuVisible == True:
			self.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True

class MainMenu(MenuBase):
	"""Main menu shown at launch"""
	def __init__(self, canvas, controller):
		# Add Virtual Mouse
		canvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
		# Store controller instance
		self.controller = controller
	
		"""initialize the Main menu"""
		super(MainMenu, self).__init__(canvas, 'main', 'Main Menu', True)
		
		
		# add play button, play button action, and scroll over animation
		self.play = self.addItem(viz.addButtonLabel('Play'), fontSize = 50)
		vizact.onbuttondown(self.play, self.controller.nextMenu)
		
		# add options button row
		self.Help = self.addItem(viz.addButtonLabel('Help'), fontSize = 50)
		vizact.onbuttondown(self.Help, self.helpButton)
		
		# add help button row
		self.Exit = self.addItem(viz.addButtonLabel('Exit'), fontSize = 50)
		vizact.onbuttondown(self.Exit, self.controller.exitGame)
		
#		#rendering
#		bb = self.getBoundingBox()
#		self.canvas.setRenderWorldOverlay([bb.width*1.8, bb.height*1.8], fov = bb.height*.1, distance = 3)
		
		#change scale depending on display mode
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])
	
		
	def helpButton(self):
		print 'Help Button was Pressed'

class ModeMenu(MenuBase):
	"""Game mode selection menu"""
	def __init__(self, canvas, controller):
		super(ModeMenu, self).__init__(canvas, 'mode', 'Mode Selection')
		
		# Store controller instance
		self.controller = controller
		
		#Store modes from config to populate modemenu with
		self.modes = config.MenuConfig.Modes
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
		self.backward = vizact.onbuttondown(backButton, self.controller.backMenu)
		self.forward = vizact.onbuttondown(startButton, self.controller.nextMenu)
		
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
		self.regions = config.OntologicalGroups.regions #collections.OrderedDict type
		self.layers = config.OntologicalGroups.layers #collections.OrderedDict type
		self.modes = config.MenuConfig.Modes
		self.getPanel().fontSize(50)
		
		#####################
		'''LAYER TAB PANEL SETUP'''
		#####################
		
		#creating tab panel tp 
		byRegionPanel = vizdlg.TabPanel(align = viz.ALIGN_LEFT_TOP, parent = canvas)
		
		#creating sub panels for tab panels(all layer data is stored in config.layers) storing sub panels in laypan
		layPan = {}
		
		for i, l in enumerate(self.regions.iteritems()):
			layPan[l[0]] = vizdlg.GridPanel(parent = canvas, fontSize = 50)
		
		#creating dict of checkboxes for layers
		self.checkBox = {}
		
		for key in self.regions.iterkeys():
			self.checkBox[key] = {}
			for cb in self.layers.iterkeys():
				self.checkBox[key][cb] = viz.addCheckbox(parent = canvas)
				
		#remove checkboxes from non-functioning region-layer selections
		for key in config.MenuConfig.RemoveCheckFromTab.iterkeys():
			for cb in config.MenuConfig.RemoveCheckFromTab[key]:
				self.checkBox[key][cb].disable()
		
		#populate panels with layers and checkboxes
		for i in self.regions.iterkeys():
			for j in self.layers.iterkeys():
				layPan[i].addRow([viz.addText(j), self.checkBox[i][j]])
			byRegionPanel.addPanel(i, layPan[i], align = viz.ALIGN_LEFT_TOP)
		
		#############################################
		"""CREATE TOTAL LAYER SELECTION CHECKBOXES"""
		#############################################
		
		#creating grib panel to put checkboxes on
		selectAllPanel = vizdlg.GridPanel(parent = canvas, fontSize = 50)
		
		#creating checkboxes
		self.selectAllOf = {}
		
		for i in self.layers.iterkeys():
			self.selectAllOf[i] = viz.addCheckbox(parent = canvas)
		
		#adding checkboxes to panel
		for i in self.layers:
			selectAllPanel.addRow([viz.addText('Load All ' + i, fontSize = 50), self.selectAllOf[i]])
		
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
		vizact.onbuttondown(backButton, self.controller.backMenu)
		vizact.onbuttondown(startButton, lambda: viztask.schedule(self.controller.start))
		
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

		#############################
		"""BUTTON CALLBACK"""
		#############################
		
		viz.callback(viz.BUTTON_EVENT, controller.onAllSelection)
		
class LoadingScreen(vizinfo.InfoPanel):
	"""Loading Screen"""
	def __init__(self, name = 'loading', title = '', fontSize = 175):
		"""initialize the menu"""
		self.canvas = viz.addGUICanvas(scene = viz.Scene2)
		vizinfo.InfoPanel.__init__(self, '', title = title, fontSize = fontSize, parent = self.canvas, align = viz.ALIGN_CENTER_CENTER, icon = False)
		
		
		#hide system mouse
		viz.mouse.setVisible(False)
		viz.mouse.setTrap(True)

		#adding progress bar
		self.name = name
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])
		
		self.percentLoaded = 0
		
		self.progress = viz.addProgressBar('Loading...')
		self.getPanel().fontSize(100)
		self.addItem(self.progress, align = viz.ALIGN_CENTER_CENTER)
		
class InGameMenu(MenuBase):
	"""In-game menu to be shown when games are running"""
	def __init__(self,canvas,controller):
		super(InGameMenu, self).__init__(canvas, 'ingame', 'In Game Menu')
		# Store controller instance
		self.controller = controller
		
		#menu buttons
		self.restart = self.addItem(viz.addButtonLabel('Restart'), fontSize = 50)
		self.end = self.addItem(viz.addButtonLabel('End game'), fontSize = 50)
		
		#Callbacks
		vizact.onbuttondown(self.restart, self.controller.restart)
		vizact.onbuttondown(self.end, self.controller.endGame)
		
		#change scale depending on display mode
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])
		
class Selection():
	"""Selection methods to determine GUI inputs, and storage format for GUI inputs"""
	def __init__(self):
		self.load		= []
		self.mode		= []
		self.regions	= []
		self.layers		= []
		
	def modeSelected(self, modeRadiosDict):
		"""Determines the selected game mode from the GUI"""
		for i in modeRadiosDict.keys():
			if modeRadiosDict[i].get() == 1:
				self.mode = i
				break
	
	def objectsSelected(self, inputMenu):
		"""Determines which selections were made on the tabs, and entire layer selections made"""
		for i in inputMenu.regions.iterkeys():
			for j in inputMenu.layers.iterkeys():
				if inputMenu.checkBox[i][j].get() == 1:		
					ontologySearch = (set.intersection, inputMenu.layers[j], inputMenu.regions[i])
					self.load.append(ontologySearch)
					
		for i in inputMenu.selectAllOf.keys():
			if inputMenu.selectAllOf[i].get() == 1:
				layer_region = (set.union, inputMenu.layers[i])
				self.load.append(layer_region)

class modalityGUI():
	def __init__(self):
		self.PATH = '.\\dataset\\configurations\\'
		
		"""initialization variables: reading from previous created file to find what selections were 
		storing values in variables"""
		try:
			with open(self.PATH + 'configurations.json','rb') as f:
				try:
					self.prevInput = json.load(f)
				except ValueError:
					print 'no previous input file!'
		except IOError:
			print 'file has not yet been created'
			
		try:
			self.dispMode = self.prevInput['dispMode']
			self.pointerMode = self.prevInput['pointerMode']
		except:
			self.dispMode = None
			self.pointerMode = None
		self.camMode = None
		self.proceed = True
		
		#create the window
		self.root = Tkinter.Tk()
		self.root.resizable(0,0)
		self.root.protocol('WM_DELETE_WINDOW', self.__CancelCommand)
		
		#modify root window
		self.root.title('Modality Selection: ')
		
		#create main frame and directions frame
		mainFrame = Tkinter.Frame(self.root)
		mainFrame.pack(side = Tkinter.LEFT)
		
		#display modality label
		displayModeLabel = Tkinter.Label(mainFrame, text = 'Display Mode: ', bg = 'blue', fg = 'white')
		displayModeLabel.pack_configure(side = Tkinter.TOP)
		
		#display modality frame for radio buttons
		dispFrame = Tkinter.Frame(mainFrame)
		dispFrame.pack(side = Tkinter.TOP)
		
		#creating display modality radio buttons
		self.vDisp = Tkinter.StringVar()
		self.vDisp.set('dispMode')
				
		for label in config.DisplayMode.MODES.keys():
			val = config.DisplayMode.MODES[label]
			self.dispModeRadio = Tkinter.Radiobutton(dispFrame, text = label, variable = self.vDisp, value = val, command = self.dispSelected)
			self.dispModeRadio.pack_configure(side = Tkinter.LEFT)
		
		#pointer modality label
		pointModeLabel = Tkinter.Label(mainFrame, text = 'Pointer Mode: ', bg = 'blue', fg = 'white')
		pointModeLabel.pack_configure(side = Tkinter.TOP)
		
		#pointer modality frame for radio buttons
		pointFrame = Tkinter.Frame(mainFrame)
		pointFrame.pack(side = Tkinter.TOP)
		
		#creating pointer modality radio buttons
		self.vPoint = Tkinter.StringVar()
		self.vPoint.set('pointMode')
		
		for label in config.PointerMode.MODES.keys():
			val = config.PointerMode.MODES[label]
			self.pointModeRadio = Tkinter.Radiobutton(pointFrame, text = label, variable =  self.vPoint, value = val, command = self.pointSelected)
			self.pointModeRadio.pack_configure(side = Tkinter.LEFT)
	
		#setting display modality and pointer modality to most previously selected
		self.vDisp.set(self.dispMode)
		self.vPoint.set(self.pointerMode)
	
		#creating next and exit button frame
		exitFrame = Tkinter.Frame(mainFrame)
		exitFrame.pack(side = Tkinter.LEFT)
		
		nextFrame = Tkinter.Frame(mainFrame)
		nextFrame.pack(side = Tkinter.RIGHT)
		
		#creating next and exit buttons
		nextButton = Tkinter.Button(nextFrame, text = 'Next', fg = 'white', bg = 'green', command = lambda: self.next(None))
		exitButton = Tkinter.Button(exitFrame, text = 'Exit', fg = 'white', bg = 'red', command = lambda: self.exit(None))
		nextButton.pack_configure(side = Tkinter.RIGHT)
		exitButton.pack_configure(side = Tkinter.LEFT)
		
		#adding keybindings
		self.root.bind('<Return>', self.next)
		self.root.bind('<Escape>', self.exit)
		
		#start gui
		self.root.mainloop()
	
	def __CancelCommand(self):
		pass
		
	def dispSelected(self):
		radioValue = self.vDisp.get()
		self.dispMode = radioValue

	def pointSelected(self):
		radioValue = self.vPoint.get()
		self.pointerMode = radioValue
	
	def camSelected(self):
		pass

	def next(self, keyDown):
		with open(self.PATH + 'configurations.json','wb') as f:
			self.configurations = {'dispMode': self.dispMode, 'pointerMode': self.pointerMode, 'proceed': self.proceed}
			for _ in self.configurations.values():
				if _ == None:
					return
			json.dump(self.configurations, f, indent = 1)
		self.root.destroy()

	def exit(self, keyDown):
		self.proceed = False
		with open(self.PATH + 'configurations.json','wb') as f:
			self.configurations = {'dispMode': self.dispMode, 'pointerMode': self.pointerMode, 'proceed': self.proceed}
			json.dump(self.configurations, f, indent = 1)
		self.root.destroy()
