import viz
import vizact
import vizinfo
import vizdlg
import vizproximity

import init
import menu	
import puzzle
import config

def init():
	global proxList
	proxList = []
	global tutorial
	tutorial = InterfaceTutorial()

class InterfaceTutorial():
	def __init__(self):
		
		sf = 0.5
		self.gloveStart = puzzle.glove.getPosition()
		
		#creating tutorial objects
		self.dog = viz.addChild('.\\dataset\\dog\\dog.obj')
		self.dogOutline = viz.addChild('.\\dataset\\dog\\dog.obj')
		self.dog.setScale([sf,sf,sf])
		self.dogOutline.setScale([sf,sf,sf])
		
		#creating dog outline
		self.dogOutline.alpha(.5)
		self.dogOutline.color(0,5,0)
#		self.dogOutline.visible(viz.OFF)

		#creating proximity manager and target
		self.manager = vizproximity.Manager()
		target = vizproximity.Target(puzzle.glove)
		self.manager.addTarget(target)
		
		#creating dog sensors
		self.dogSensor = vizproximity.Sensor(vizproximity.Sphere(1, center = [0,1,0]), source = self.dog)
		self.manager.addSensor(self.dogSensor)
		self.outlineSensor = vizproximity.Sensor(vizproximity.Sphere(1, center = [0,1,0]), source = self.dogOutline)
		self.manager.addSensor(self.outlineSensor)
		
		#manager proximity events
		self.manager.onEnter(None, EnterProximity, self.dog)
		self.manager.onExit(None, ExitProximity)
		
		#toggle debug mode 
		vizact.onkeydown('l', reset, self.manager, self.gloveStart)
		
		#selection commands
		self.keybindings = []
		self.keybindings.append(vizact.onkeydown(' ',grab))
		self.keybindings.append(vizact.onkeyup(' ', release))
	def end(self):
		self.manager.clearSensors()
		self.manager.clearTargets()
		self.manager.remove()
		self.dog.remove()
		self.dogOutline.remove()
		for bind in self.keybindings:
			bind.remove()
def reset(manager, gloveStart):
	manager.setDebug(viz.TOGGLE)
	puzzle.glove.setPosition(gloveStart)
def EnterProximity(e, sensorCheck):
	"""@args vizproximity.ProximityEvent()"""
	global proxList
	source = e.sensor.getSourceObject()
	if source == sensorCheck:
		proxList.append(source)
		print proxList
def ExitProximity(e):
	"""@args vizproximity.ProximityEvent()"""
	source = e.sensor.getSourceObject()
	try:
		proxList.remove(source)
		print proxList
	except ValueError:
		pass
def grab():
	global gloveLink
	global grabFlag
	global glove
	
	if len(proxList) > 0:
		target = proxList[0]
		gloveLink = viz.grab(puzzle.glove, target, viz.ABS_GLOBAL)
def release():
	global gloveLink
	
	if gloveLink:
		gloveLink.remove()
		gloveLink = None
def snap():
	pass
	