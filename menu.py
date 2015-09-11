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

import puzzle

def init():
	"""Create global menu instance"""
	global main
	global game
	global ingame
	global canvas
	
	canvas = viz.addGUICanvas()
	canvas.setRenderWorldOverlay([2000,2000],60,1)
	# Compatibility for all display types
	canvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
	canvas.setCursorPosition([0,0])	
	
	main = MainMenu(canvas)
	game = GameMenu(canvas)
	ingame = InGameMenu(canvas)

class MainMenu(vizinfo.InfoPanel):
	"""Main game menu"""
	def __init__(self,canvas):
		"""initialize the Main menu"""
		vizinfo.InfoPanel.__init__(self, '', title='Main Menu', fontSize = 100, \
			align=viz.ALIGN_CENTER_CENTER, icon=False, parent=canvas)
		
		# Since we are using the vizard pointer, hide system mouse
		viz.mouse.setVisible(False)
		viz.mouse.setTrap(True)
		self.menuVisible = True
		self.canvas = canvas
		self.active = True
		
		self.getPanel().fontSize(50)

		self.Play = self.addItem(viz.addButtonLabel('Play'))
		self.Scores = self.addItem(viz.addButtonLabel('Scores'))
		self.Options = self.addItem(viz.addButtonLabel('Options'))
		self.Exit = self.addItem(viz.addButtonLabel('Exit'))

		vizact.onbuttondown(self.Exit,self.exitFunc)
		vizact.onbuttondown(self.Play,self.playFunc)
		vizact.onbuttondown(self.Scores, self.scoresFunc)
		vizact.onbuttondown(self.Options, self.optionsFunc)

		bb = self.getBoundingBox()
		self.canvas.setRenderWorldOverlay([bb.width, bb.height], fov=bb.height*.1, distance=3.0)
		
		

	def toggle(self):
		if(self.menuVisible == True):
			self.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True
		
			
	def playFunc(self):
		print 'Play button was pressed'
		self.setPanelVisible(viz.OFF, animate = False)
		game.setPanelVisible(viz.ON, animate = True)
		self.active = False
		game.active = True
		
	def exitFunc(self):
		print 'Exit button was pressed'
		print 'Exiting Visual Anatomy Trainer'
		viz.quit()
		print 'Visual Anatomy Trainer has closed'
		
	def scoresFunc(self):
		print 'Scores button was pressed'
	
	def optionsFunc(self):
		print 'Options button was pressed'

class GameMenu(vizinfo.InfoPanel):
	"""Game selection submenu"""
	def __init__(self,canvas):
		vizinfo.InfoPanel.__init__(self, 'Select Dataset',title='Game Menu',fontSize = 50,align=viz.ALIGN_CENTER_CENTER,icon=False,parent= canvas)
		self.dataset = 'Skull'
	
		self.canvas = canvas
		self.active = False
		
		print "creating Game Menu"
		self.getPanel().fontSize(50)
		self.setPanelVisible(viz.OFF, animate = False)
		self.menuVisible = False;		
		
		#Add radio buttons
		self.skullRadio = self.addLabelItem('Skull', viz.addRadioButton('dataset'))
		self.armRadio = self.addLabelItem('Arm', viz.addRadioButton('dataset'))
		self.pelvisRadio = self.addLabelItem('Pelvis', viz.addRadioButton('dataset'))

		#Add puzzle start button
		self.Puzzle = self.addItem(viz.addButtonLabel('Start Puzzle Game'))

		#Set callbacks
		vizact.onbuttondown(self.skullRadio, self.setDataset, 'Skull')
		vizact.onbuttondown(self.armRadio, self.setDataset, 'Arm')
		vizact.onbuttondown(self.pelvisRadio, self.setDataset, 'Pelvis')
		vizact.onbuttondown(self.Puzzle, self.puzzleFunc)

	def puzzleFunc(self):
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