import viz
import vizact
import vizinfo
import vizdlg
import vizproximity
import vizshape
import vizmat

import csv
import time
import datetime

import init
import menu	
import puzzle
import config

def init():
	global proxList
	global snapFlag
	global gloveLink
	global recordData
	snapFlag = False
	proxList = []
	gloveLink = False
	global tutorial
	tutorial = InterfaceTutorial()
	recordData = TutorialData()

class InterfaceTutorial():
	def __init__(self):
		
		sf = 0.5
		self.gloveStart = puzzle.glove.getPosition()
		
		#creating tutorial objects
		self.dog = viz.addChild('.\\dataset\\dog\\dog.obj')
		self.dogOutline = viz.addChild('.\\dataset\\dog\\dog.obj')
		self.dogStart = self.dog.getPosition()
		self.dog.setScale([sf,sf,sf])
		self.dogOutline.setScale([sf,sf,sf])
		
		#creating dog outline
		self.dogOutline.alpha(0.8)
		self.dogOutline.color(0,5,0)

		#creating proximity manager
		self.manager = vizproximity.Manager()
		
		'''creating dog grab and snap sensors around sphere palced in the center of the dog'''
		self.dogCenter = vizshape.addSphere(0.1, pos = (self.dogStart))
		self.outlineCenter = vizshape.addSphere(0.1, pos = (self.dogStart))
		self.dogCenter.setPosition([0,-.35,0])
		self.outlineCenter.setPosition([0,-.35,0])
		self.centerStart = self.dogCenter.getPosition()
		viz.grab(self.dogCenter, self.dog)
		viz.grab(self.outlineCenter, self.dogOutline)
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
		self.dogTarget = vizshape.addSphere(0.2,parent = self.dogOutline, pos = (self.dogStart))
		self.dogTarget.setPosition([0,1.2,0])
		self.dogTarget.visible(viz.OFF)
		self.manager.addTarget(vizproximity.Target(self.dogTarget))
		
		#manager proximity events
		self.manager.onEnter(self.dogGrabSensor, EnterProximity, puzzle.glove)
		self.manager.onExit(self.dogGrabSensor, ExitProximity)
		self.manager.onEnter(self.dogSnapSensor, snapCheckEnter, self.dogCenter, self.outlineCenter, self.dogTarget)
		self.manager.onExit(self.dogSnapSensor, snapCheckExit)
		
		#grab, release, and reset commands
		self.keybindings = []
		self.keybindings.append(vizact.onkeydown(' ',grab))
		self.keybindings.append(vizact.onkeyup(' ', release, self))
		self.keybindings.append(vizact.onkeydown('l', reset, self.manager, self.gloveStart, self.dogCenter, self.outlineCenter))
	
	def end(self):
		self.manager.clearSensors()
		self.manager.clearTargets()
		self.manager.remove()
		self.dog.remove()
		self.dogOutline.remove()
		self.dogCenter.remove()
		self.outlineCenter.remove()
		for bind in self.keybindings:
			bind.remove()

def reset(manager, gloveStart, dogCenter, outlineCenter):
	manager.setDebug(viz.TOGGLE)
	puzzle.glove.setPosition(gloveStart)
	if dogCenter.getVisible() == False:
		dogCenter.visible(viz.ON)
		outlineCenter.visible(viz.ON)
	else:
		dogCenter.visible(viz.OFF)
		outlineCenter.visible(viz.OFF)
def EnterProximity(e, glove):
	"""@args vizproximity.ProximityEvent()"""
	global proxList
	target = e.target.getSourceObject()
	source = e.sensor.getSourceObject()
	if target == glove:
		proxList.append(source)
def ExitProximity(e):
	"""@args vizproximity.ProximityEvent()"""
	source = e.sensor.getSourceObject()
	try:
		proxList.remove(source)
	except ValueError:
		pass
def grab():
	global gloveLink
	global grabFlag
	global glove
	
	if len(proxList) > 0:
		target = proxList[0]
		gloveLink = viz.grab(puzzle.glove, target, viz.ABS_GLOBAL)
		recordData.event(event = 'grab', snape = 'Picked Up')
	else:
		recordData.event(event = 'grab', snape = 'Did Not Pick Up')
def release(self):
	global snapFlag
	global gloveLink
	eulerThres = 45
	eulerDiff = vizmat.QuatDiff(self.dogTarget.getQuat(), self.dogCenter.getQuat())
	try:
		if gloveLink:
			gloveLink.remove()
	except NameError:
		gloveLink.remove()
	
	if snapFlag == True and eulerDiff <= eulerThres:
		recordData.event(event = 'release', snape = True)
		snap(self.dogCenter, self.outlineCenter)
	else:
		recordData.event(event = 'release', snape = False)
def snap(dog, dogTarget):
	movePos = vizact.moveTo(dogTarget.getPosition(), speed = .5)
	moveAng = vizact.spinTo(euler = dogTarget.getEuler(), speed = 35)
	
	dog.addAction(movePos)
	dog.addAction(moveAng)
def snapCheckEnter(e, dog, dogOutline, dogTarget):
	"""@args vizproximity.ProximityEvent()"""
	global snapFlag
	sourceTarget = e.target.getSourceObject()
	
	if sourceTarget == dogTarget:
		snapFlag = True
def snapCheckExit(e):
	"""@args vizproximity.ProximityEvent()"""
	global snapFlag
	snapFlag = False

class TutorialData():
	'''collects data from tutorial'''
	def __init__(self):
		'''init data recording structure'''
		self.startTime = datetime.datetime.now()
		self.scoreFile = open('.\\tutorial log\\' + self.startTime.strftime('%m%d%Y_%H%M%S') + '.csv', 'wb')
		self.csv = csv.writer(self.scoreFile)
		
		self.header = ['timestamp','event','snap']
		self.events = []
		
		self.csv.writerow(self.header)

	def event(self, event = "release", snape = False):
		'''record event'''
		print 'EVENT!'
		currentEvent = dict(zip(self.header,[time.clock(), event, snape]))
		print currentEvent
		self.events.append(currentEvent)
		self.csv.writerow([self.events[-1][column] for column in self.header])
	def close(self):
		self.scoreFile.close()