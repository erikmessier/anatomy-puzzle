# Builtin
import csv
import time, datetime
import random

# Vizard
import viz
import vizact
import vizinfo, vizdlg
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
import config
import model
import menu
		
class InterfaceTutorial(object):
	"""
	This game mode is intended to instruct novice users in the use of the SpaceMouse
	interface hardware. The mechanics of this tutorial are heavily inspired by the
	'teapot trainer' tutorial that ships with the SpaceMouse device.
	"""
	def __init__(self, dataset):
		
		
		
		
		self.snapFlag = False
		self.proxList = []
		self.gloveLink = None
		self.snapTransitionTime = 0.3
		self.animateOutline = 1.25
		self.tasks = viztask.Scheduler
		self.recordData = TutorialData()
		
		
		sf = 0.5
#		model.pointer.setEuler(0,0,0)
		model.pointer.setPosition(0,0,0)
		self.gloveStart = model.pointer.getPosition()
		self.iterations = 0
		self.origPosVec = config.SMPositionScale
		self.origOrienVec = config.SMEulerScale
		
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
		self.dogStart = self.dog.getPosition()
		self.dog.setScale([sf,sf,sf])
		self.startColor = model.pointer.getColor()
		
		#creating dog outline
		self.dogOutline = viz.addChild('.\\dataset\\dog\\dog.obj')
		self.dogOutline.setScale([sf,sf,sf])
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
		self.gloveTarget = vizproximity.Target(model.pointer)
		self.manager.addTarget(self.gloveTarget)
		self.dogTargetMold = vizshape.addSphere(0.2,parent = self.dogOutline, pos = (self.dogStart))
		self.dogTargetMold.setPosition([0,1.2,0])
		self.dogTargetMold.visible(viz.OFF)
		self.dogTarget = vizproximity.Target(self.dogTargetMold)
		self.manager.addTarget(self.dogTarget)
		
		#manager proximity events
		self.manager.onEnter(self.dogGrabSensor, self.EnterProximity)
		self.manager.onExit(self.dogGrabSensor, self.ExitProximity)
		self.manager.onEnter(self.dogSnapSensor, self.snapCheckEnter)
		self.manager.onExit(self.dogSnapSensor, self.snapCheckExit)
		
		#reset command
		self.keybindings = []
		self.keybindings.append(vizact.onkeydown('l', self.resetGlove))
		self.keybindings.append(vizact.onkeydown('p', self.debugger))
		
		#task schedule
		self.interface = viztask.schedule(self.interfaceTasks())
		self.gameMechanics = viztask.schedule(self.mechanics())
	
	def load(self, dataset):
		'''Accept dataset, but do nothing with it'''
		pass

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
			self.grab()
			yield viztask.waitKeyUp(' ')
			self.release()
			
	def end(self):
		"""
		CLEANUP TUTORIAL
		"""
		print 'ending'
		viztask.Task.kill(self.interface)
		viztask.Task.kill(self.gameMechanics)
		self.manager.clearSensors()
		self.manager.clearTargets()
		self.manager.remove()
		self.dog.remove()
		self.dogOutline.remove()
		self.dogCenter.remove()
		self.outlineCenter.remove()
		self.dogTargetMold.remove()
		self.iterations = 0
		model.pointer.setParent(model.display.camcenter)
		model.pointer.setPosition([0,1,0])
		self.proxList = []
		self.gloveLink = None
		config.SMEulerScale = self.origOrienVec
		config.SMPositionScale = self.origPosVec
		self.recordData.close()
		for bind in self.keybindings:
			bind.remove()
			
	def mechanics(self):
		"""tutorial mechanics: moves the dog outline around the environment and waits for the dog to be snapped to it
		before preforming the next action."""
		if self.iterations ==0:
			#setting conditions for position transformations along single axis
#			model.pointer.setParent(viz.WORLD)
			config.SMEulerScale = [0,0,0]
			self.proxList.append(self.dogCenter)
	
#		elif self.iterations ==3:
#			#setting conditions for position transformations along all axes
#			self.proxList.remove(self.dogCenter)
	
#		elif self.iterations==4:
#			#setting conditinos for angular transformations
#			self.proxList.append(self.dogCenter)
#			config.SMEulerScale = self.origOrienVec
#			config.SMPositionScale = [0,0,0]
##			model.pointer.setPosition(0,1,-1)
##			model.pointer.color(0,0,5)
	
		elif self.iterations==3:
			#setting conditions for positional and angular transformations
#			model.pointer.color(self.startColor)
#			model.pointer.setParent(model.display.camcenter)
			try: 
				self.proxList.remove(self.dogCenter)
			except ValueError:
				print 'dogCenter is not in proximity'
			config.SMEulerScale = self.origOrienVec
			config.SMPositionScale = self.origPosVec
	
		if self.iterations<=0:
			# X AXIS POS TRANSFORMATION
			config.SMPositionScale = [.0001,0,0]
			self.recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along x-axis')
			randomPos = [4*(random.random()-0.5), 0,0]
			self.movePos = vizact.move(randomPos[0],randomPos[1], randomPos[2], time = self.animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
		
		elif self.iterations>0 and self.iterations<=1:
			#Y AXIS POS TRANS
			config.SMPositionScale = [0,.0001,0]
			self.recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along y-axis')
			randomPos = [0, 2*(random.random()-0.5),0]
			self.movePos = vizact.move(randomPos[0],randomPos[1], randomPos[2], time = self.animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
	
		elif self.iterations>1 and self.iterations<=2:
			#Z AXIS POS TRANS
			config.SMPositionScale = [0,0,.0001]
			self.recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along z-axis')
			randomPos = [0,0,4*(random.random()-0.5)]
			self.movePos = vizact.move(randomPos[0],randomPos[1], randomPos[2], time = self.animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
	
		elif self.iterations>2 and self.iterations<=3:
			#ALL AXES POS TRANS
			config.SMPositionScale = self.origPosVec
			self.recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along all axis')
			randomPos = [0,1,-1]
			self.movePos = vizact.moveTo(randomPos, time = self.animateOutline)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, self.movePos)
#		
#		elif self.iterations>3 and self.iterations<=4:
#			#X AXIS ANG TRANS
#			config.SMEulerScale = [.01,0,0]
#			model.pointer.setEuler(0,0,0)
#			self.recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about x-axis')
#			thisEuler = [0,0,0]
#			thisEuler[1] = random.randint(-100,100)
#			self.moveAng = vizact.spinTo(euler = thisEuler, time = self.animateOutline, mode = viz.REL_GLOBAL)
#			yield viztask.waitTime(1)
#			yield viztask.addAction(self.outlineCenter, self.moveAng)
#	
#		elif self.iterations>4 and self.iterations<=5:
#			#Y AXIS ANG TRANS
#			config.SMEulerScale = [0,.01,0]
#			model.pointer.setEuler(0,0,0)
#			self.recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about y-axis')
#			thisEuler = [0,0,0]
#			thisEuler[0] = random.randint(-100,100)
#			self.moveAng = vizact.spinTo(euler = thisEuler, time = self.animateOutline, mode = viz.REL_GLOBAL)
#			yield viztask.waitTime(1)
#			yield viztask.addAction(self.outlineCenter, self.moveAng)
#	
#		elif self.iterations>5 and self.iterations<=6:
#			#Z AXIS ANG TRANS
#			config.SMEulerScale = [0,0,.01]
#			model.pointer.setEuler(0,0,0)
#			self.recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about z-axis')
#			thisEuler = [0,0,0]
#			thisEuler[2] = random.randint(-100,100)
#			self.moveAng = vizact.spinTo(euler = thisEuler, time = self.animateOutline, mode = viz.REL_GLOBAL)
#			yield viztask.waitTime(1)
#			yield viztask.addAction(self.outlineCenter, self.moveAng)
#		
#		elif self.iterations>6 and self.iterations<=7:
#			#ALL AXES ANG TRANS
#			config.SMEulerScale = self.origOrienVec
#			model.pointer.setEuler(0,0,0)
#			self.recordData.event(event = 'ROUND ' + str(self.iterations), result = 'euler about all axis')
#			randomEuler = [random.randint(-100,100),random.randint(-100,100),random.randint(-100,100)]
#			self.moveAng = vizact.spinTo(euler = randomEuler, time = self.animateOutline)
#			yield viztask.waitTime(1)
#			yield viztask.addAction(self.outlineCenter, self.moveAng)
	
		elif self.iterations>3 and self.iterations<=9:
			#ALL AXES POS AND ANG TRANS
			self.recordData.event(event = 'ROUND ' + str(self.iterations), result = 'move along all axis')
			randomPos = [4*(random.random()-0.5),2*(random.random()-0.5),4*(random.random()-0.5)]
#			randomEuler = [random.randint(-90,90),random.randint(-90,90),random.randint(-90,90)]
			self.movePos = vizact.moveTo(randomPos, time = self.animateOutline)
#			self.moveAng = vizact.spinTo(euler = randomEuler, time = self.animateOutline)
			transition = vizact.parallel(self.movePos)
			yield viztask.waitTime(1)
			yield viztask.addAction(self.outlineCenter, transition)

		else:
			#END
			model.menu.toggle()
			config.SMEulerScale = self.origOrienVec
			config.SMPositionScale = self.origPosVec
			self.recordData.event(event = 'FINISHED', result = 'FINISHED')
		
		self.iterations = self.iterations+1

	def resetGlove(self):
		#move glove to starting position
		model.pointer.setPosition(self.gloveStart)

	def EnterProximity(self, e):
		"""
		If the target entering the proximity is the gloveTarget, and the gloveTarget is active
		then add the source of the proximity sensor to self.proxList
		
		"""
		"""@args vizproximity.ProximityEvent()"""
		source = e.sensor.getSourceObject()
		target = e.target.getSourceObject()
		targets = e.manager.getActiveTargets()
		print self.iterations
		if target == model.pointer:
			for t in targets:
				if t == self.gloveTarget:
					model.pointer.color(4,1,1)
					self.proxList.append(source)

	def ExitProximity(self, e):
		"""
		If the target leaving the proximity sensor is the gloveTarget, then remove the source of 
		the proximity sensor from self.proxList
		"""
		"""@args vizproximity.ProximityEvent()"""
		
		source = e.sensor.getSourceObject()
		target = e.target.getSourceObject()
		if target == model.pointer:
			model.pointer.color(1,1,1)
			
			self.proxList.remove(source)

	def grab(self):
		"""
		If the glove is not already linked to something, and the glove is within proximity of an object, link the 
		object to the glove
		"""
		if self.outlineCenter.getAction() or self.dogCenter.getAction():
			self.recordData.event(event = 'grab', result = 'Did Not Pick Up')
			return
		if not self.gloveLink and len(self.proxList)>0:
			target = self.proxList[0]
			self.gloveLink = viz.grab(model.pointer, target, viz.ABS_GLOBAL)
			self.recordData.event(event = 'grab', result = 'Picked Up')
		else:
			self.recordData.event(event = 'grab', result = 'Did Not Pick Up')

	def release(self):
		"""
		Unlink the glove and the object, and if the object is close enough to its target, and is within angular range, then
		the object is snapped to its target.
		"""
		eulerThres = 45
		eulerDiff = vizmat.QuatDiff(self.outlineCenter.getQuat(), self.dogCenter.getQuat())
		if self.snapFlag == True and eulerDiff <= eulerThres and self.gloveLink:
			self.recordData.event(event = 'release', result = 'Snapped!')
			self.snap()
		else:
			self.recordData.event()
		if self.gloveLink:
			try:
				self.gloveLink.remove()
			except NameError:
				self.gloveLink.removeItems(viz.grab(model.pointer, target, viz.ABS_GLOBAL))

	def snap(self):
		"""
		Moves dog to the pos and euler of its target (dogTarget)
		"""
		movePos = vizact.moveTo(self.outlineCenter.getPosition(), time = self.snapTransitionTime)
		moveAng = vizact.spinTo(euler = self.outlineCenter.getEuler(), time = self.snapTransitionTime)
		transition = vizact.parallel(movePos, moveAng)
		self.dogCenter.addAction(transition)
		viz.playSound(".\\dataset\\snap.wav")
		viztask.schedule(self.mechanics())

	def snapCheckEnter(self, e):
		"""
		If the snap proximity sensor has its desired target within range, then snapFlag is True.
		snapFlag is used in release to determine whether snap will be called or not.
		"""
		
		targets = e.manager.getActiveTargets()
		for t in targets:
			if t == self.dogTarget:
				self.snapFlag = True

	def snapCheckExit(self, e):
		"""
		If the dogTarget has left the proximity sensor then snapFlag is False
		"""
		target = e.target.getSourceObject()
		if target == self.dogTargetMold:
			self.snapFlag = False

class TutorialData():
	"""
	Collects data from tutorial
	"""
	def __init__(self):
		"""
		Init data recording structure
		"""
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
		currentEvent = dict(zip(self.header,[time.clock(), event, result]))
		self.events.append(currentEvent)
		self.csv.writerow([self.events[-1][column] for column in self.header])
		
	def close(self):
		self.scoreFile.close()
