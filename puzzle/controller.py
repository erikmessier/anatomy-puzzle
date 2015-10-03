"""
Controller components of the Puzzle game
"""

# Vizard modules
import viz
import vizact, viztask, vizproximity
import vizmat
import vizshape

# Python built-in modules
import random
import math
import json, csv
import time, datetime

# Custom modules
import init
import menu
import config
import model

class PuzzleController():
	"""
	Puzzle game controller base class.
	Not intended to be used directly, derive children that feature
	the game mode functionality you want.
	"""
	def __init__(self):
		self._groups = None
		self._meshes = None
		self._boneInfo = None
		self._proximityList = None
		self._inRange = None
		self._gloveLink = None
		self._grabFlag = None
		self._keyBindings = None
		self._closestBoneIdx = None
		self._prevBoneIdx = None
		self._lastGrabbed = None
		
		# Will move this out of main and where it belongs
		viewcube = puzzle.controller.viewCube()
		vizact.onkeydown('65460', viewcube.toggleModes) # Numpad '4' key
		
	def loadMeshes(meshes = [], animate = False, randomize = True):
		"""Load all of the files from the dataset into puzzle.mesh instances"""
		for i, fileName in enumerate(meshes):
			# This is the actual mesh we will see
			b = Mesh(fileName)
			if (not randomize or i == 0):
				#Hardcoded keystone
				b.setPosition([0.0,1.0,0.0])
				b.setEuler([0.0,90.0,180.0]) # [0,0,180] flip upright [0,90,180] flip upright and vertical
				if (i == 0):
					b.group.grounded = True
			else:		
				# b.setPosition([(random.random()-0.5)*3, 1.0, (random.random()-0.5)*3]) # random sheet, not a donut
				angle = random.random() * 2 * math.pi
				radius = random.random() + 1.5
				
				targetPosition = [math.sin(angle) * radius, 1.0, math.cos(angle) * radius]
				targetEuler = [(random.random()-0.5)*40,(random.random()-0.5)*40 + 90.0, (random.random()-0.5)*40 + 180.0]
				
				if (animate):
					move = vizact.moveTo(targetPosition, time = 2)
					spin = vizact.spinTo(euler = targetEuler, time = 2)
					transition = vizact.parallel(spin, move)
					b.addAction(transition)
				else:					
					b.setPosition(targetPosition)
					b.setEuler(targetEuler)
			
			model.appendMesh(b)
#			bones.append(b)
#			bonesByName[fileName] = b
#			bonesById[b.id] = b

	def unloadBones():
		"""Unload all of the bone objects to reset the puzzle game"""
		for m in model.getMeshes():
	#		m.textRemove()
			m.remove(children = True)
		
	def transparency(source, level, includeSource = False):
		"""Set the transparency of all the bones"""
		meshes = model.getMeshes()
		if includeSource:
			for b in meshes:
				b.setAlpha(level)
		else:
			for b in [b for b in meshes if b != source]:
				b.setAlpha(level)			

	def moveCheckers(sourceChild):
		"""
		Move all of the checker objects on each bone into position, in order to
		see if they should be snapped.
		"""
		source = model.getMesh(sourceChild.id)
		
		for bone in [b for b in model.getMeshes() if b != source]:
			bone.checker.setPosition(source.centerPoint, viz.ABS_PARENT)

	def snap():
		"""
		Snap checks for any nearby bones, and mates a src bone to a dst bone
		if they are in fact correctly placed.
		"""
		if not lastGrabbed:
			print 'nothing to snap'
			return
		SNAP_THRESHOLD = 0.5;
		DISTANCE_THRESHOLD = 1.5;
		ANGLE_THRESHOLD = 45;
		source = model.getMesh(lastGrabbed.id)
		moveCheckers(lastGrabbed)

		# Search through all of the checkers, and snap to the first one meeting our snap
		# criteria
		for bone in [b for b in bones if b not in source.group.members]:
			targetSnap = bone.checker.getPosition(viz.ABS_GLOBAL)
			targetPosition = bone.getPosition(viz.ABS_GLOBAL)
			targetQuat = bone.getQuat(viz.ABS_GLOBAL)
			
			currentPosition = source.getPosition(viz.ABS_GLOBAL)
			currentQuat = source.getQuat(viz.ABS_GLOBAL)		
			
			snapDistance = vizmat.Distance(targetSnap, currentPosition)
			proximityDistance = vizmat.Distance(targetPosition, currentPosition)
			angleDifference = vizmat.QuatDiff(bone.getQuat(), source.getQuat())
			
			if (snapDistance <= SNAP_THRESHOLD) and (proximityDistance <= DISTANCE_THRESHOLD) and (angleDifference < ANGLE_THRESHOLD):
				print 'Snap! ', source, ' to ', bone
				score.event(event = 'release', source = source.name, destination = bone.name, snap = True)
				viz.playSound(".\\dataset\\snap.wav")
				source.snap(bone)
				if len(bones) == len(source.group.members):
					print "Assembly completed!"
					end()
					menu.ingame.endButton()
				break
		else:
			print 'did not meet snap criteria'
			score.event(event = 'release', source = source.name)

	def snapGroup(boneNames):
		"""Specify a list of bones that should be snapped together"""
		print boneNames
		if (len(boneNames) > 0):
			meshes = []
			[[meshes.append(model.getMesh(m)) for m in group] for group in boneNames]
			[m.snap(meshes[0], animate = False) for m in meshes[1:]]

	def grab():
		"""Grab in-range objects with the pointer"""
		grabList = [b for b in proximityList if not b.group.grounded] # Needed for disabling grab of grounded bones
		
		if len(grabList) > 0 and not grabFlag:
			target = getClosestBone(glove,grabList)
			# only play bone description sound once, so set it if it hasnt been
			if target.grabbedFlag == 0:
	#			playBoneDesc(grabList[0])
				target.setGrabbedFlag(True)
			target.setGroupParent()
			gloveLink = viz.grab(glove, target, viz.ABS_GLOBAL)
	#		score.event(event = 'grab', source = target.name)
			transparency(target, 0.7)
			lastGrabbed = target
			print lastGrabbed
	#	elif not grabFlag:
	#		score.event(event = 'grab')
		grabFlag = True

	def release():
		"""Release grabbed object from pointer"""
		if gloveLink:
	#		snap(lastGrabbed)
			transparency(lastGrabbed, 1.0)
			gloveLink.remove()
			gloveLink = None
		else:
			score.event(event = 'release')
		grabFlag = False
		
	def getClosestBone(pointer, proxList):
		"""
		looks through proximity list and searches for the closest bone to the glove and puts it at
		the beginning of the list
		"""
		if(len(proxList) >0):
			bonePos = proxList[0].getPosition(viz.ABS_GLOBAL)
			pointerPos = pointer.getPosition(viz.ABS_GLOBAL)
			shortestDist = vizmat.Distance(bonePos, pointerPos)	
			
			for i,x in enumerate(proxList):
				bonePos = proxList[i].getPosition(viz.ABS_GLOBAL)
				pointerPos = pointer.getPosition(viz.ABS_GLOBAL)
				tempDist = vizmat.Distance(bonePos,pointerPos)
				
				if(tempDist < shortestDist):
					shortestDist = tempDist
					tempBone = proxList[i]
					proxList[i] = proxList[0]
					proxList[0] = tempBone
		return proxList[0]
		
	def load(dataset = 'right arm'):
		"""
		Load datasets and initialize everything necessary to commence
		the puzzle game.
		"""
		
		if not RUNNING:
			init() # Flush everything
			
			RUNNING = True
			
			# Dataset
			self._ds = model.DatasetInterface()

			# Proximity management
			manager = vizproximity.Manager()
			target = vizproximity.Target(glove)
			manager.addTarget(target)

			manager.onEnter(None, EnterProximity)
			manager.onExit(None, ExitProximity)
		
			#Setup Key Bindings
			bindKeys()
			
			# start the clock
			time.clock()
			
			global score
			score = PuzzleScore()
			
	#		viztask.schedule(soundTask(glove))

			loadMeshes(ds.getOntologySet(dataset))
			#snapGroup(smallBoneGroups)

	def EnterProximity(e):
		global proximityList
		source = e.sensor.getSourceObject()
		model.getMesh(source.id).mesh.color([1.0,1.0,0.5])
		model.getMesh(source.id).setNameAudioFlag(1)
		proximityList.append(source)
		
	def ExitProximity(e):
		source = e.sensor.getSourceObject()
		model.getMesh(source.id).mesh.color([1.0,1.0,1.0])
		model.getMesh(source.id).setNameAudioFlag(0)
		proximityList.remove(source)
	#	removeBoneInfo(model.getMeshsource.id))

	def bindKeys():
		global keyBindings
		keyBindings.append(vizact.onkeydown('o', manager.setDebug, viz.TOGGLE)) #debug shapes
		keyBindings.append(vizact.onkeydown(' ', grab)) #space select
		keyBindings.append(vizact.onkeydown('65421', grab)) #numpad enter select
		keyBindings.append(vizact.onkeydown(viz.KEY_ALT_R, snap))
		keyBindings.append(vizact.onkeyup(' ', release))
		keyBindings.append(vizact.onkeyup('65421', release))
class FreePlayMode(PuzzleController):
	def __init__(self):
		super(FreePlayMode, self).__init__()

class TestMode(PuzzleController):
	def __init__(self):
		super(FreePlayMode, self).__init__()

			
class PuzzleScore():
	"""Handles scoring for the puzzle game"""
	def __init__(self):
		"""Init score datastructure, open up csv file"""
		self.startTime = datetime.datetime.now()
		self.scoreFile = open('.\\log\\' + self.startTime.strftime('%m%d%Y_%H%M%S') + '.csv', 'wb')
		self.csv = csv.writer(self.scoreFile)
		
		# Starting score
		self.score = 100
		
		self.header = ['timestamp','event','source','destination','snap']
		self.events = []
		
		self.csv.writerow(self.header)
		
		self.textbox = viz.addTextbox()
		self.textbox.setPosition(0.8,0.1)
		self.textbox.message('Score: ' + str(self.score))
	
	def event(self, event = "release", source = None, destination = None, snap = False):
		"""Record an event in the score history"""
		print 'Score event!'
		currentEvent = dict(zip(self.header,[time.clock(), event, source, destination, snap]))
		self.events.append(currentEvent)
		self.csv.writerow([self.events[-1][column] for column in self.header])
		
		self.update(self.events)
		
	def update(self, events):
		"""Iterative f calculation"""
		"""From Alex: So, start with 100 points, if you grab and release, it's minus 10,
		if you snap it's plus 10 if. You snap again, it's plus 20 and so on."""
		curEvent = events[-1]
		
		if (curEvent['event'] == 'release'):
			if curEvent['snap']:
				self.score += 10
			elif len(events) > 2:
				if events[-3]['source'] == curEvent['source']:
					pass
				elif curEvent['source'] != None:
					self.score -= 10
			elif curEvent['source'] != None:
				self.score -= 10
		
		self.textbox.message('Score: ' + str(self.score))
	
	def close(self):
		"""Close open file"""
		self.scoreFile.close()
		self.textbox.remove()

def end():
	"""Do everything that needs to be done to end the puzzle game"""
	global RUNNING
	if RUNNING:
		print "Puzzle Quitting!"
#		score.close()
		manager.clearSensors()
		manager.clearTargets()
		manager.remove()
		unloadBones()
		for bind in keyBindings:
			bind.remove()
		RUNNING = False

def start(dataset):
	"""
	Start running the puzzle game
	"""
	global controller

	controller = FreePlayMode()
	controller.load(dataset)

def csvToList(location):
	"""Read in a CSV file to a list of lists"""
	raw = []
	try:
		with open(location, 'rb') as csvfile:
			wowSuchCSV = csv.reader(csvfile, delimiter=',')
			for row in wowSuchCSV:
				raw.append(row)
	except IOError:
		print "ERROR: Unable to open CSV file at", location
	except:
		print "Unknown error opening CSV file at:", location
	return raw


def soundTask(pointer):
	"""
	Function to be placed in Vizard's task scheduler
		looks through proximity list and searches for the closest bone to the glove and puts it at
		the beginning of the list, allows the bone name and bone description to be played
	"""
	global proximityList
	while True:
		yield viztask.waitTime(0.25)
		if(len(proximityList) >0):
			bonePos = proximityList[0].getPosition(viz.ABS_GLOBAL)
			pointerPos = pointer.getPosition(viz.ABS_GLOBAL)
			shortestDist = vizmat.Distance(bonePos, pointerPos)
			
			for i,x in enumerate(proximityList):
				proximityList[i].incProxCounter()  #increase count for how long glove is near bone
				bonePos = proximityList[i].getPosition(viz.ABS_GLOBAL)
				pointerPos = pointer.getPosition(viz.ABS_GLOBAL)
				tempDist = vizmat.Distance(bonePos,pointerPos)
				#displayBoneInfo(proximityList[0])

				if(tempDist < shortestDist):
#					removeBoneInfo(proximityList[0])
					shortestDist = tempDist
					tempBone = proximityList[i]
					proximityList[i] = proximityList[0]
					proximityList[0] = tempBone
			#tempBone = proximityList[0]
			displayBoneInfo(proximityList[0])
			
			if proximityList[0].proxCounter > 2 and proximityList[0].getNameAudioFlag() == 1:
				#yield viztask.waitTime(3.0)
				vizact.ontimer2(0,0,playName,proximityList[0])
				proximityList[0].clearProxCounter()
				proximityList[0].setNameAudioFlag(0)
#			if tempBone.proxCounter > 2 and tempBone.getDescAudioFlag() == 1:
#				yield viztask.waitTime(1.5)
#				#playBoneDesc(proximityList[0])
#				vizact.ontimer2(0,0, playBoneDesc,tempBone)
#				tempBone.setDescAudioFlag(0)	

def playName(boneObj):
	"""Play audio with the same name as the bone"""
	try:
		viz.playSound(path + "audio_names\\" + boneObj.name + ".wav") # should be updated to path
	except ValueError:
		print ("the name of the audio name file was wrong")