#builtin
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

#custom
import init
import menu	
import controller as puzzle
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
	global Tutorial
	snapFlag = False
	proxList = []
	gloveLink = None
	snapTransitionTime = 0.3
	animateOutline = 1.25
	tasks = viztask.Scheduler
	canvas = viz.addGUICanvas()
	Tutorial = InterfaceTutorial(canvas)
	recordData = TutorialData()
		
class InterfaceTutorial():
	def __init__(self, canvas):
		
		sf = 0.5
		puzzle.glove.setEuler(0,0,0)
		puzzle.glove.setPosition(0,0,0)
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
		self.dogOutline.texture(None)

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
		self.keybindings.append(vizact.onkeydown('l', resetGlove, self.manager, self.gloveStart, self.dogCenter, self.outlineCenter))
		self.keybindings.append(vizact.onkeydown('p', self.debugger))
		
		#task schedule
		self.interface = viztask.schedule(self.interfaceTasks())
		self.gameMechanics = viztask.schedule(self.mechanics())
		
	def debugger(self):
		"""
		Activates debuggin' tools
		"""
		self.manager.setDebug(viz.TOGGLE)
		if self.dogCenter.getVisible() == viz.ON:
			self.dogCenter.visible(viz.OFF)
			self.outlineCenter.visible(viz.OFF)
			self.dogTargetMold.visible(viz.OFF)
			self.mainAxes.remove()
			self.outlineAxes.remove()
			self.dogAxes.remove()
		else:
			self.dogCenter.visible(viz.ON)
			self.outlineCenter.visible(viz.ON)
			self.dogTargetMold.visible(viz.ON)
			self.mainAxes = vizshape.addAxes()
			self.outlineAxes = vizshape.addAxes(parent = self.outlineCenter)
			self.dogAxes = vizshape.addAxes(parent = self.dogCenter)
			
	def interfaceTasks(self):
		"""
		Grab and Release task. viztask was used to make grab and release dependent on the occurence of one another.
		In order for a release there must have been a grab and vice versa.
		"""
		while True:
			yield viztask.waitKeyDown(' ')
			grab()
			yield viztask.waitKeyUp(' ')
			release(self)
			
	def end(self):
		"""
		CLEANUP TUTORIAL
		"""
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
		puzzle.glove.setParent(model.display.camcenter)
		puzzle.glove.setPosition([0,1,0])
		proxList = []
		gloveLink = None
		config.orientationVector = self.origOrienVec
		config.positionVector = self.origPosVec
		viztask.Task.kill(self.interface)
		viztask.Task.kill(self.gameMechanics)
		recordData.close()
		for bind in self.keybindings:
			bind.remove()
			
	def mechanics(self):
		"""tutorial mechanics: moves the dog outline around the environment and waits for the dog to be snapped to it
		before preforming the next action."""
		if self.iterations ==0:
			#setting conditions for position transformations along single axis
			puzzle.glove.setParent(viz.WORLD)
			config.orientationVector = [0,0,0]
			proxList.append(self.dogCenter)
	
		if self.iterations ==3:
			#setting conditions for position transformations along all axes
			proxList.remove(self.dogCenter)
	
		elif self.iterations==4:
			#setting conditinos for angular transformations
			proxList.append(self.dogCenter)
			config.orientationVector = self.origOrienVec
			config.positionVector = [0,0,0]
			puzzle.glove.setPosition(0,1,-1)
			puzzle.glove.color(0,0,5)
	
		elif self.iterations==8:
			#setting conditions for positional and angular transformations
			puzzle.glove.color(self.startColor)
			puzzle.glove.setParent(model.display.camcenter)
			proxList.remove(self.dogCenter)
			config.orientationVector = self.origOrienVec
			config.positionVector = self.origPosVec
	
		if self.iterations<=0:
			# X AXIS POS TRANSFORMATION
			config.positionVector = [.0001,0,0]
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along x-axis')
			randomPos = [random.randrange(-1,2,2), 0,0]
			self.movePos = vizact.move(randomPos[0],randomPos[1], randomPos[2], time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
		
		elif self.iterations>0 and self.iterations<=1:
			#Y AXIS POS TRANS
			config.positionVector = [0,.0001,0]
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along y-axis')
			randomPos = [0, random.randrange(-1,2,2),0]
			self.movePos = vizact.move(randomPos[0],randomPos[1], randomPos[2], time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
	
		elif self.iterations>1 and self.iterations<=2:
			#Z AXIS POS TRANS
			config.positionVector = [0,0,.0001]
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along z-axis')
			randomPos = [0,0,random.randrange(-1,2,2)]
			self.movePos = vizact.move(randomPos[0],randomPos[1], randomPos[2], time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
	
		elif self.iterations>2 and self.iterations<=3:
			#ALL AXES POS TRANS
			config.positionVector = self.origPosVec
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along all axis')
			randomPos = [0,1,-1]
			self.movePos = vizact.moveTo(randomPos, time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
		
		elif self.iterations>3 and self.iterations<=4:
			#X AXIS ANG TRANS
			config.orientationVector = [.01,0,0]
			puzzle.glove.setEuler(0,0,0)
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about x-axis')
			thisEuler = [0,0,0]
			thisEuler[1] = random.randint(-100,100)
			self.moveAng = vizact.spinTo(euler = thisEuler, time = animateOutline, mode = viz.REL_GLOBAL)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.moveAng)
	
		elif self.iterations>4 and self.iterations<=5:
			#Y AXIS ANG TRANS
			config.orientationVector = [0,.01,0]
			puzzle.glove.setEuler(0,0,0)
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about y-axis')
			thisEuler = [0,0,0]
			thisEuler[0] = random.randint(-100,100)
			self.moveAng = vizact.spinTo(euler = thisEuler, time = animateOutline, mode = viz.REL_GLOBAL)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.moveAng)
	
		elif self.iterations>5 and self.iterations<=6:
			#Z AXIS ANG TRANS
			config.orientationVector = [0,0,.01]
			puzzle.glove.setEuler(0,0,0)
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about z-axis')
			thisEuler = [0,0,0]
			thisEuler[2] = random.randint(-100,100)
			self.moveAng = vizact.spinTo(euler = thisEuler, time = animateOutline, mode = viz.REL_GLOBAL)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.moveAng)
		
		elif self.iterations>6 and self.iterations<=7:
			#ALL AXES ANG TRANS
			config.orientationVector = self.origOrienVec
			puzzle.glove.setEuler(0,0,0)
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about all axis')
			randomEuler = [random.randint(-100,100),random.randint(-100,100),random.randint(-100,100)]
			self.moveAng = vizact.spinTo(euler = randomEuler, time = animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.moveAng)
	
		elif self.iterations>7 and self.iterations<=12:
			#ALL AXES POS AND ANG TRANS
			recordData.event(event = 'ROUND ' + str(self.iterations), result = 'change pos and euler')
			randomPos = [random.randrange(-1,1,1),random.randrange(0,2,1),random.randrange(-1,1,1)]
			randomEuler = [random.randint(-90,90),random.randint(-90,90),random.randint(-90,90)]
			self.movePos = vizact.moveTo(randomPos, time = animateOutline)
			self.moveAng = vizact.spinTo(euler = randomEuler, time = animateOutline)
			transition = vizact.parallel(self.movePos, self.moveAng)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, transition)

		else:
			#END
			config.orientationVector = self.origOrienVec
			config.positionVector = self.origPosVec
			recordData.event(event = 'FINISHED', result = 'FINISHED')
		
		self.iterations = self.iterations+1

def resetGlove(manager, gloveStart, dogCenter, outlineCenter):
	#move glove to starting position
	puzzle.glove.setPosition(gloveStart)

def EnterProximity(e, gloveTarget, gloveObject):
	"""
	If the target entering the proximity is the gloveTarget, and the gloveTarget is active
	then add the source of the proximity sensor to proxList
	"""
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
	"""
	If the target leaving the proximity sensor is the gloveTarget, then remove the source of 
	the proximity sensor from proxList
	"""
	"""@args vizproximity.ProximityEvent()"""
	global proxList
	source = e.sensor.getSourceObject()
	target = e.target.getSourceObject()
	if target == glove:
		puzzle.glove.color(startColor)
		proxList.remove(source)

def grab():
	"""
	If the glove is not already linked to something, and the glove is within proximity of an object, link the 
	object to the glove
	"""
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
	"""
	Unlink the glove and the object, and if the object is close enough to its target, and is within angular range, then
	the object is snapped to its target.
	"""
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
	"""
	Moves dog to the pos and euler of its target (dogTarget)
	"""
	movePos = vizact.moveTo(dogTarget.getPosition(), time = snapTransitionTime)
	moveAng = vizact.spinTo(euler = dogTarget.getEuler(), time = snapTransitionTime)
	transition = vizact.parallel(movePos, moveAng)
	dog.addAction(transition)
	viztask.schedule(Tutorial.mechanics())

def snapCheckEnter(e, dogTarget):
	"""
	If the snap proximity sensor has its desired target within range, then snapFlag is True.
	snapFlag is used in release to determine whether snap will be called or not.
	"""
	"""@args vizproximity.ProximityEvent()"""
	global snapFlag
	targets = e.manager.getActiveTargets()
	for t in targets:
		if t == dogTarget:
			snapFlag = True

def snapCheckExit(e, dogTarget):
	"""
	If the dogTarget has left the proximity sensor then snapFlag is False
	"""
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
		try:
			self.scoreFile = open('.\\log\\tutorial\\' + self.startTime.strftime('%m%d%Y_%H%M%S') + '.csv', 'wb')
		except IOError:
			print "No directory?"
			raise
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
