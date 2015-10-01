import viz
import vizact
import vizinfo
import vizdlg
import vizproximity
import viztask
import vizshape
import vizmat

import csv
import time
import datetime
import random


import init
import menu	
import puzzle
import config
import model

def init():
	global proxList
	global snapTransitionTime
	global animateOutline
	global tasks
	global snapFlag
	global gloveLink
	global recordData
	global tutorial
	snapFlag = False
	proxList = []
	gloveLink = None
	snapTransitionTime = 0.3
	animateOutline = 1.25
	tasks = viztask.Scheduler
	canvas = viz.addGUICanvas()
	tutorial = InterfaceTutorial(canvas)
	recordData = TutorialData()
	
	
class InterfaceTutorial():
	def __init__(self, canvas):
		
		sf = 0.5
		self.gloveStart = puzzle.glove.getPosition()
		self.iterations = 0
		self.canvas = canvas
		self.origPosVec = config.positionVector
		self.origOrienVec = config.orientationVector
		#creating directions panel
#		viz.mouse.setVisible(False)
#		directions = vizinfo.InfoPanel('', fontSize = 10, parent = canvas, align = viz.ALIGN_LEFT_TOP, title = 'Tutorial', icon = False)
#		if config.pointerMode ==0:
#			directions.addItem(viz.addText('Keyboard Controls:'))
#			directions.addLabelItem(viz.addText('W'))
#		
#		if config.pointerMode ==1:
#			directions.addItem(viz.addText('Spacemouse Controls:'))
#			directions.addItem(viz.addTexQuad(size = 300, parent = canvas, texture = viz.addTexture('.\\mouse key.png')))
		
		
		#creating tutorial objects
		self.dog = viz.addChild('.\\dataset\\dog\\dog.obj')
		self.dogOutline = viz.addChild('.\\dataset\\dog\\dog.obj')
		self.dogStart = self.dog.getPosition()
		self.dog.setScale([sf,sf,sf])
		self.dogOutline.setScale([sf,sf,sf])
		self.startColor = puzzle.glove.getColor()
		
		#creating dog outline
		self.dogOutline.alpha(0.8)
		self.dogOutline.color(0,5,0)

		#creating proximity manager
		self.manager = vizproximity.Manager()
		
		'''creating dog grab and snap sensors around sphere palced in the center of the dog'''
		self.dogCenter = vizshape.addSphere(0.1, pos = (self.dogStart))
		self.dogSnapSensor = vizproximity.Sensor(vizproximity.Sphere(0.35, center = [0,1,0]), source = self.dogCenter)
		self.outlineCenter = vizshape.addSphere(0.1, pos = (self.dogStart))
		self.dogCenter.setPosition([0,-.35,0])
		self.outlineCenter.setPosition([0,-.35,0])
		self.centerStart = self.dogCenter.getPosition()
		self.dogGrab = viz.grab(self.dogCenter, self.dog)
		self.outlineGrab = viz.grab(self.outlineCenter, self.dogOutline)
		self.dogCenter.color(5,0,0)
		self.outlineCenter.color(0,5,0)
		self.dogCenter.visible(viz.OFF)
		self.outlineCenter.visible(viz.OFF)
		
		self.dogSnapSensor = vizproximity.Sensor(vizproximity.Sphere(0.35, center = [0,1,0]), source = self.dogCenter)
		self.manager.addSensor(self.dogSnapSensor)
		self.dogGrabSensor = vizproximity.Sensor(vizproximity.Sphere(0.85, center = [0,1,0]), source = self.dogCenter)
		self.manager.addSensor(self.dogGrabSensor)
		
		'''creating glove target and a dog target. the dog target is a sphere placed at the center of the dog outline'''
		self.gloveTarget = vizproximity.Target(puzzle.glove)
		self.manager.addTarget(self.gloveTarget)
		self.dogTargetMold = vizshape.addSphere(0.2,parent = self.dogOutline, pos = (self.dogStart))
		self.dogTargetMold.setPosition([0,1.2,0])
		self.dogTargetMold.visible(viz.OFF)
		self.dogTarget = vizproximity.Target(self.dogTargetMold)
		self.manager.addTarget(self.dogTarget)
		
		#manager proximity events
		self.manager.onEnter(self.dogGrabSensor, EnterProximity, self.gloveTarget, puzzle.glove)
		self.manager.onExit(self.dogGrabSensor, ExitProximity, puzzle.glove, self.startColor)
		self.manager.onEnter(self.dogSnapSensor, snapCheckEnter, self.dogTarget)
		self.manager.onExit(self.dogSnapSensor, snapCheckExit, self.dogTargetMold)
		
		#reset command
		self.keybindings = []
		self.keybindings.append(vizact.onkeydown('l', reset, self.manager, self.gloveStart, self.dogCenter, self.outlineCenter))
		self.keybindings.append(vizact.onkeydown('p', self.debugger))
		
		#task schedule
		self.interface = viztask.schedule(self.interfaceTasks())
		self.gameMechanics = viztask.schedule(self.mechanics())
		
	def debugger(self):
		self.manager.setDebug(viz.TOGGLE)
		if self.dogCenter.getVisible() == viz.ON:
			self.dogCenter.visible(viz.OFF)
			self.outlineCenter.visible(viz.OFF)
			self.dogTargetMold.visible(viz.OFF)
		else:
			self.dogCenter.visible(viz.ON)
			self.outlineCenter.visible(viz.ON)
			self.dogTargetMold.visible(viz.ON)
	def interfaceTasks(self):
		while True:
			yield viztask.waitKeyDown(' ')
			grab()
			yield viztask.waitKeyUp(' ')
			release(self)
	def end(self):
		self.manager.clearSensors()
		self.manager.clearTargets()
		self.manager.remove()
		self.dog.remove()
		self.dogOutline.remove()
		self.dogCenter.remove()
		self.outlineCenter.remove()
		self.dogTargetMold.remove()
		self.iterations = 0
		puzzle.glove.color(self.startColor)
		proxList = []
		gloveLink = None
		config.orientationVector = self.origOrienVec
		config.positionVector = self.origPosVec
		viztask.Task.kill(self.interface)
		viztask.Task.kill(self.gameMechanics)
		for bind in self.keybindings:
			bind.remove()
	def mechanics(self):
		if self.iterations ==0:
			config.orientationVector = [0,0,0]
			config.positionVector = self.origPosVec
	
		elif self.iterations==4:
			puzzle.glove.setParent(viz.WORLD)
			proxList.append(self.dogCenter)
			config.orientationVector = self.origOrienVec
			config.positionVector = [0,0,0]
			puzzle.glove.color(0,0,5)
			puzzle.glove.setPosition(0,1,-1)
	
		elif self.iterations==8:
			puzzle.glove.color(self.startColor)
			puzzle.glove.setParent(model.display.camcenter)
			proxList.remove(self.dogCenter)
			config.orientationVector = self.origOrienVec
			config.positionVector = self.origPosVec
	
		if self.iterations<=0:
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along x-axis')
			randomPos = [random.randrange(-1,2,2), 0,0]
			self.movePos = vizact.move(randomPos[0],randomPos[1], randomPos[2], time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
		
		elif self.iterations>0 and self.iterations<=1:
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along y-axis')
			randomPos = [0, random.randrange(-1,2,2),0]
			self.movePos = vizact.move(randomPos[0],randomPos[1], randomPos[2], time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
	
		elif self.iterations>1 and self.iterations<=2:
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along z-axis')
			randomPos = [0,0,random.randrange(-1,2,2)]
			self.movePos = vizact.move(randomPos[0],randomPos[1], randomPos[2], time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
	
		elif self.iterations>2 and self.iterations<=3:
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along all axis')
			randomPos = [0,1,-1]
			self.movePos = vizact.moveTo(randomPos, time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
		
		elif self.iterations>3 and self.iterations<=4:
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about x-axis')
			randomEuler = [random.randint(-100,100),0,0]
			self.moveAng = vizact.spinTo(euler = randomEuler, time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.moveAng)
	
		elif self.iterations>4 and self.iterations<=5:
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about y-axis')
			randomEuler = [0,random.randint(-100,100),0]
			self.moveAng = vizact.spinTo(euler = randomEuler, time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.moveAng)
	
		elif self.iterations>5 and self.iterations<=6:
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about z-axis')
			randomEuler = [0,0,random.randint(-100,100)]
			self.moveAng = vizact.spinTo(euler = randomEuler, time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.moveAng)
		
		elif self.iterations>6 and self.iterations<=7:
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about all axis')
			randomEuler = [random.randint(-100,100),random.randint(-100,100),random.randint(-100,100)]
			self.moveAng = vizact.spinTo(euler = randomEuler, time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.moveAng)
	
		elif self.iterations>7 and self.iterations<=12:
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'change pos and euler')
			randomPos = [random.randrange(-1,1,1),random.randrange(0,2,1),random.randrange(-1,1,1)]
			randomEuler = [random.randint(-90,90),random.randint(-90,90),random.randint(-90,90)]
			self.movePos = vizact.moveTo(randomPos, time = animateOutline)
			self.moveAng = vizact.spinTo(euler = randomEuler, time = animateOutline)
			transition = vizact.parallel(self.movePos, self.moveAng)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, transition)

		else:
			config.orientationVector = self.origOrien
			config.positionVector = self.origPos
			recordData.event(event = 'FINISHED', result = 'FINISHED')
		
		self.iterations = self.iterations+1

def reset(manager, gloveStart, dogCenter, outlineCenter):
	puzzle.glove.setPosition(gloveStart)
def EnterProximity(e, gloveTarget, gloveObject):
	"""@args vizproximity.ProximityEvent()"""
	global proxList
	source = e.sensor.getSourceObject()
	target = e.target.getSourceObject()
	targets = e.manager.getActiveTargets()
	if target == gloveObject:
		for t in targets:
			if t == gloveTarget:
				gloveObject.color(0,0,5)
				proxList.append(source)
def ExitProximity(e, glove, startColor):
	"""@args vizproximity.ProximityEvent()"""
	global proxList
	source = e.sensor.getSourceObject()
	target = e.target.getSourceObject()
	if target == glove:
		puzzle.glove.color(startColor)
		proxList.remove(source)
def grab():
	global gloveLink
	global grabFlag
	global glove
	if not gloveLink and len(proxList)>0:
		target = proxList[0]
		gloveLink = viz.grab(puzzle.glove, target, viz.ABS_GLOBAL)
		recordData.event(event = 'grab', result = 'Picked Up')
	else:
		recordData.event(event = 'grab', result = 'Did Not Pick Up')
def release(self):
	eulerThres = 45
	eulerDiff = vizmat.QuatDiff(self.outlineCenter.getQuat(), self.dogCenter.getQuat())
	if snapFlag == True and eulerDiff <= eulerThres and gloveLink:
		recordData.event(event = 'release', result = 'Snapped!')
		snap(self.dogCenter, self.outlineCenter)
	else:
		recordData.event()
	if gloveLink:
		try:
			gloveLink.remove()
		except NameError:
			gloveLink.removeItems(viz.grab(puzzle.glove, target, viz.ABS_GLOBAL))
def snap(dog, dogTarget):
	movePos = vizact.moveTo(dogTarget.getPosition(), time = snapTransitionTime)
	moveAng = vizact.spinTo(euler = dogTarget.getEuler(), time = snapTransitionTime)
	transition = vizact.parallel(movePos, moveAng)
	dog.addAction(transition)
	viztask.schedule(tutorial.mechanics())
def snapCheckEnter(e, dogTarget):
	"""@args vizproximity.ProximityEvent()"""
	global snapFlag
	targets = e.manager.getActiveTargets()
	for t in targets:
		if t == dogTarget:
			snapFlag = True
def snapCheckExit(e, dogTarget):
	"""@args vizproximity.ProximityEvent()"""
	global snapFlag
	target = e.target.getSourceObject()
	if target == dogTarget:
		snapFlag = False
class TutorialData():
	'''collects data from tutorial'''
	def __init__(self):
		'''init data recording structure'''
		self.startTime = datetime.datetime.now()
		self.scoreFile = open('.\\tutorial log\\' + self.startTime.strftime('%m%d%Y_%H%M%S') + '.csv', 'wb')
		self.csv = csv.writer(self.scoreFile)
		self.header = ['timestamp','event','event result']
		self.events = []
		self.csv.writerow(self.header)
	def event(self, event = "release", result = 'Did Not Snap'):
		'''record event'''
#		print 'EVENT!'
		currentEvent = dict(zip(self.header,[time.clock(), event, result]))
		self.events.append(currentEvent)
		self.csv.writerow([self.events[-1][column] for column in self.header])
	def close(self):
		self.scoreFile.close()
