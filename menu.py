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
	canvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
	canvas.setCursorPosition([0,0])	
	
	main = MainMenu(canvas)
	game = GameMenu(canvas)
	ingame = InGameMenu(canvas)
		
	


class MainMenu(): # Y U NO INHERET vizinfo.InfoPanel (ง •̀_•́)ง
	"""Main game menu"""
	
	def __init__(self,canvas):
		"""initialize the Main menu"""
		#self.dispMode = dispMode;
		print "creating main menu"

		viz.mouse.setVisible(False)
		
		self.menuVisible = True
		self.canvas = canvas
		self.active = True
		
		#Creates a virtual mouse if you are in Oculus.
		#if dispMode == 2:
		
		#vizinfo.InfoPanel.__init__(self)
		self.menu = vizinfo.InfoPanel('',title='Main Menu',fontSize = 100,align=viz.ALIGN_CENTER_CENTER,icon=False,parent=self.canvas)
		self.menu.getPanel().fontSize(50)

		self.Play = self.menu.addItem(viz.addButtonLabel('Play'))
		self.Scores = self.menu.addItem(viz.addButtonLabel('Scores'))
		self.Options = self.menu.addItem(viz.addButtonLabel('Options'))
		self.Exit = self.menu.addItem(viz.addButtonLabel('Exit'))

		vizact.onbuttondown(self.Exit,self.exitFunc)
		vizact.onbuttondown(self.Play,self.playFunc)
		vizact.onbuttondown(self.Scores, self.scoresFunc)
		vizact.onbuttondown(self.Options, self.optionsFunc)

		bb = self.menu.getBoundingBox()
		self.canvas.setRenderWorldOverlay([bb.width, bb.height], fov=bb.height*.1, distance=3.0)
		
		

	def toggle(self):
		if(self.menuVisible == True):
			self.menu.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.menu.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True
		
			
	def playFunc(self):
		print 'Play button was pressed'
		self.menu.setPanelVisible(viz.OFF, animate = False)
		game.menu.setPanelVisible(viz.ON, animate = True)
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

class GameMenu():
	"""Game selection submenu"""
	def __init__(self,canvas):
		self.dataset = 'Skull'
	
		self.canvas = canvas
		self.active = False
		
		print "creating Game Menu"
		self.menu = vizinfo.InfoPanel('Select Dataset',title='Game Menu',fontSize = 50,align=viz.ALIGN_CENTER_CENTER,icon=False,parent= canvas)
		self.menu.getPanel().fontSize(50)
		self.menu.setPanelVisible(viz.OFF, animate = False)
		self.menuVisible = False;		
		
		#Add radio buttons
		self.skullRadio = self.menu.addLabelItem('Skull', viz.addRadioButton('dataset'))
		self.armRadio = self.menu.addLabelItem('Arm', viz.addRadioButton('dataset'))
		self.pelvisRadio = self.menu.addLabelItem('Pelvis', viz.addRadioButton('dataset'))

		#Add puzzle start button
		self.Puzzle = self.menu.addItem(viz.addButtonLabel('Start Puzzle Game'))

		#Set callbacks
		vizact.onbuttondown(self.skullRadio, self.setDataset, 'Skull')
		vizact.onbuttondown(self.armRadio, self.setDataset, 'Arm')
		vizact.onbuttondown(self.pelvisRadio, self.setDataset, 'Pelvis')
		vizact.onbuttondown(self.Puzzle, self.puzzleFunc)

	def puzzleFunc(self):
		print 'Puzzle game button was pressed'
		self.menu.setPanelVisible(viz.OFF)
		self.canvas.setCursorVisible(viz.OFF)
		self.active = False
		ingame.active = True
		puzzle.load(self.dataset)
	
	def setDataset(self, name):
		self.dataset = name
		

	def toggle(self):
		if(self.menuVisible == True):
			self.menu.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.menu.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True
		

class InGameMenu():
	"""In-game menu to be shown when games are running"""
	def __init__(self,canvas):
		
		self.canvas = canvas
		self.active = False
		self.menu = vizinfo.InfoPanel('',title='In Game',fontSize = 100,align=viz.ALIGN_CENTER_CENTER,icon=False,parent=self.canvas)
		self.menu.getPanel().fontSize(50)
		self.menu.setPanelVisible(viz.OFF, animate = False)
		self.menuVisible = False
		
		self.options = self.menu.addItem(viz.addButtonLabel('Options'))
		self.restart = self.menu.addItem(viz.addButtonLabel('Restart'))
		self.end = self.menu.addItem(viz.addButtonLabel('End game'))
		
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
		main.menu.setPanelVisible(True)
		main.canvas.setCursorVisible(True)

	def toggle(self):
		if(self.menuVisible == True):
			self.menu.setPanelVisible(False)
			self.canvas.setCursorVisible(False)
			self.menuVisible = False
		else:
			self.menu.setPanelVisible(True)
			self.canvas.setCursorVisible(True)
			self.menuVisible = True
#		
#class OverHeadMenu(viz.VizNode):
#	def __init__(self):
#		self.menuBoxes = []
#		self.ExtoMM = vizshape.addBox()
#		self.ExtoMM.setScale(2.0, 0.5, 0.5)
#		self.ExtoMM.billboard(viz.BILLBOARD_VIEW)
#		self.ExtoMM.setPosition([0.0,2.0, 3.0])
#		self.textEMM = viz.addText('Exit to Main Menu', self.ExtoMM)
#		self.textEMM.setParent(self.ExtoMM)
#		self.textEMM.setScale(0.1,0.3,0.3)
#		self.textEMM.alignment(viz.TEXT_CENTER_CENTER)
#		self.textEMM.color(viz.RED)
#		self.textEMM.setPosition(0,0,-0.505)
#		
#		self.menuBoxes.append(self.ExtoMM)
#		#sensor1 = vizproximity.addBoundingSphereSensor(self.ExtoMM,scale=2)
#		#manager.addSensor(sensor1)
#		
#		self.ExtoDesktop = vizshape.addBox()
#		self.ExtoDesktop.setParent(self.ExtoMM)
#		self.ExtoDesktop.setScale(1.0,1.0,1.0)
#		self.ExtoDesktop.billboard(viz.BILLBOARD_VIEW)
#		self.ExtoDesktop.setPosition([0.0,-1.25,0.0])
#		self.textED = viz.addText('Exit to Desktop', self.ExtoDesktop)
#		self.textED.setParent(self.ExtoDesktop)
#		self.textED.setScale(0.1,0.3,0.3)
#		self.textED.alignment(viz.TEXT_CENTER_CENTER)
#		self.textED.color(viz.RED)
#		self.textED.setPosition(0,0,-0.505)
#		
#		self.menuBoxes.append(self.ExtoDesktop)
#		#sensor2 = vizproximity.addBoundingSphereSensor(self.ExtoDesktop,scale=2)
#		#manager.addSensor(sensor2)
#		
#	def ExitToMainMenu(self):
#		for menu in self.menuBoxes:
#			menu.remove()
#		mainMenu = MainMenu()
#		
#	def ExittoDesktop(self):
#		viz.quit()

def setVisibility(visibility = viz.TOGGLE):
	if not puzzle.RUNNING:
		if(main.active == True):
			main.toggle()
		elif(game.active == True):
			game.toggle()
	else:
		ingame.toggle()

def toggle():
	setVisibility()