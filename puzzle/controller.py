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
import view

# The controller...
controlInst = None

class PuzzleController(object):
	"""
	Puzzle game controller base class.
	Not intended to be used directly, derive children that feature
	the game mode functionality you want.
	"""
	def __init__(self):
		#self._groups = None
		self._meshes		= []
		self._meshesById	= {}
		self._keystones		= []
		self._proximityList	= []
		self._keyBindings	= []
		self._inRange		= []
		
		self._boneInfo		= None
		self._closestBoneIdx = None
		self._prevBoneIdx	= None
		self._lastGrabbed	= None
		self._gloveLink		= None

		self._grabFlag		= False
		self._snapAttempts	= 0
		self._imploded		= False

		self.viewcube = view.viewCube()
		
	def load(self, dataset = 'right arm'):
		"""
		Load datasets and initialize everything necessary to commence
		the puzzle game.
		"""
		
		# Dataset
		model.ds = model.DatasetInterface()

		# Proximity management
		model.proxManager = vizproximity.Manager()
		target = vizproximity.Target(model.pointer)
		model.proxManager.addTarget(target)

		model.proxManager.onEnter(None, self.EnterProximity)
		model.proxManager.onExit(None, self.ExitProximity)
	
		#Setup Key Bindings
		self.bindKeys()
		
		# start the clock
		time.clock()

		self.score = PuzzleScore()
		
#		viztask.schedule(soundTask(glove))

		self._meshesToLoad = model.ds.getOntologySet(dataset)
		self.loadMeshes(self._meshesToLoad)

		# Set Keystone
		for m in [self._meshes[i] for i in range(0,1)]:
			m.setPosition([0.0,1.5,0.0])
			m.setEuler([0.0,90.0,180.0])
			m.group.grounded = True
			self._keystones.append(m)
		#snapGroup(smallBoneGroups)
		
	def loadMeshes(self, meshes = [], animate = False, randomize = True):
		"""Load all of the files from the dataset into puzzle.mesh instances"""
		for i, fileName in enumerate(meshes):
			# This is the actual mesh we will see
			b = model.Mesh(fileName)
			if (not randomize):
				#Hardcoded keystone
				b.setPosition([0.0,1.5,0.0])
				b.setEuler([0.0,90.0,180.0]) # [0,0,180] flip upright [0,90,180] flip upright and vertical
			else:		
				# b.setPosition([(random.random()-0.5)*3, 1.0, (random.random()-0.5)*3]) # random sheet, not a donut
				angle	= random.random() * 2 * math.pi
				radius	= random.random() + 1.5
				
				targetPosition	= [math.sin(angle) * radius, 1.0, math.cos(angle) * radius]
				targetEuler		= [0.0,90.0,180.0]
				#targetEuler	= [(random.random()-0.5)*40,(random.random()-0.5)*40 + 90.0, (random.random()-0.5)*40 + 180.0]
				
				if (animate):
					move = vizact.moveTo(targetPosition, time = 2)
					spin = vizact.spinTo(euler = targetEuler, time = 2)
					transition = vizact.parallel(spin, move)
					b.addAction(transition)
				else:					
					b.setPosition(targetPosition)
					b.setEuler(targetEuler)
			
			self._meshes.append(b)
			self._meshesById[b.id] = b

	def unloadBones(self):
		"""Unload all of the bone objects to reset the puzzle game"""
		for m in self._meshes:
	#		m.textRemove()
			m.remove(children = True)
		
	def transparency(self, source, level, includeSource = False):
		"""Set the transparency of all the bones"""
		meshes = self._meshes
		if includeSource:
			for b in meshes:
				b.setAlpha(level)
		else:
			for b in [b for b in meshes if b != source]:
				b.setAlpha(level)			

	def moveCheckers(self, sourceChild):
		"""
		Move all of the checker objects on each bone into position, in order to
		see if they should be snapped.
		"""
		source = self._meshesById[sourceChild.id] # Just in case we pass in a node3D
		
		for bone in [b for b in self._meshes if b != source]:
			bone.checker.setPosition(source.centerPoint, viz.ABS_PARENT)

	def snapCheck(self):
		"""
		Snap checks for any nearby bones, and mates a src bone to a dst bone
		if they are in fact correctly placed.
		"""
		if not self._lastGrabbed:
			print 'nothing to snap'
			return
		
		SNAP_THRESHOLD = 0.5;
		DISTANCE_THRESHOLD = 1.5;
		ANGLE_THRESHOLD = 45;
		source = self._meshesById[self._lastGrabbed.id]
		self.moveCheckers(self._lastGrabbed)
			
		# Search through all of the checkers, and snap to the first one meeting our snap
		# criteria
		enabled = [m for m in self._meshes if m.getEnabled()]
		for bone in [b for b in enabled if b not in source.group.members]:
			targetSnap = bone.checker.getPosition(viz.ABS_GLOBAL)
			targetPosition = bone.getPosition(viz.ABS_GLOBAL)
			targetQuat = bone.getQuat(viz.ABS_GLOBAL)
			
			currentPosition = source.getPosition(viz.ABS_GLOBAL)
			currentQuat = source.getQuat(viz.ABS_GLOBAL)		
			
			snapDistance = vizmat.Distance(targetSnap, currentPosition)
			proximityDistance = vizmat.Distance(targetPosition, currentPosition)
			angleDifference = vizmat.QuatDiff(bone.getQuat(), source.getQuat())
			
			if (snapDistance <= SNAP_THRESHOLD) and (proximityDistance <= DISTANCE_THRESHOLD) \
					and (angleDifference < ANGLE_THRESHOLD):
				print 'Snap! ', source, ' to ', bone
				self.score.event(event = 'release', source = source.name, destination = bone.name, snap = True)
				viz.playSound(".\\dataset\\snap.wav")
				self.snap(source, bone)				
				if len(self._meshes) == len(source.group.members):
					print "Assembly completed!"
					end()
					menu.ingame.endButton()
				break
		else:
			print 'did not meet snap criteria'
			self._snapAttempts += 1
			self.score.event(event = 'release', source = source.name)

	def snap(self, sourceMesh, targetMesh):
		self.moveCheckers(sourceMesh)
		sourceMesh.moveTo(targetMesh.checker.getMatrix(viz.ABS_GLOBAL))
		targetMesh.group.merge(sourceMesh)
		if sourceMesh.group.grounded:
			self._keystones.append(sourceMesh)

	def snapGroup(self, boneNames):
		"""
		Specify a list of bones that should be snapped together
		"""
		print boneNames
		if (len(boneNames) > 0):
			meshes = []
			[[meshes.append(self._meshesById[m]) for m in group] for group in boneNames]
			[m.snap(meshes[0], animate = False) for m in meshes[1:]]

	def grab(self):
		"""Grab in-range objects with the pointer"""
		grabList = [b for b in self._proximityList if not b.group.grounded] # Needed for disabling grab of grounded bones
		if len(grabList) > 0 and not self._grabFlag:
			target = self.getClosestBone(model.pointer,grabList)
			target.setGroupParent()
			self._gloveLink = viz.grab(model.pointer, target, viz.ABS_GLOBAL)
	#		score.event(event = 'grab', source = target.name)
			self.transparency(target, 0.7)
			self._meshesById[target.id].mesh.color(0,1,0.5)
			self._meshesById[target.id].tooltip.visible(viz.ON)
#			self._meshesById[target.id].nameLine.visible(viz.ON)
			if target != self._lastGrabbed and self._lastGrabbed:
				self._meshesById[self._lastGrabbed.id].mesh.color([1.0,1.0,1.0])
				self._meshesById[self._lastGrabbed.id].tooltip.visible(viz.OFF)
#				self._meshesById[self._lastGrabbed.id].nameLine.visible(viz.OFF)
			self._lastGrabbed = target
	#	elif not self._grabFlag:
	#		score.event(event = 'grab')
		self._grabFlag = True

	def release(self):
		"""Release grabbed object from pointer"""
		if self._gloveLink:
			self.transparency(self._lastGrabbed, 1.0)
			self._gloveLink.remove()
			self._gloveLink = None
		else:
			self.score.event(event = 'release')
		self._grabFlag = False
		
	def getClosestBone(self, pointer, proxList):
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

	def EnterProximity(self, e):
		source = e.sensor.getSourceObject()
		obj = self._meshesById[source.id]
		if source != self._lastGrabbed:
			obj.mesh.color([1.0,1.0,0.5])
			obj.setNameAudioFlag(1)
		self._proximityList.append(source)
	
	def ExitProximity(self, e):
		source = e.sensor.getSourceObject()
		if source != self._lastGrabbed:
			self._meshesById[source.id].mesh.color([1.0,1.0,1.0])
			self._meshesById[source.id].setNameAudioFlag(0)
		self._proximityList.remove(source)
	#	removeBoneInfo(model.getMeshsource.id))
	
	def implode(self):
		"""
		move bones to solved positions
		"""
		target = self._keystones[0] #keystone
		for m in self._meshes[1:]:
			if m.getAction():
				return
			for bone in [b for b in self._meshes if b != m]:
				bone.checker.setPosition(m.centerPoint, viz.ABS_PARENT)
			m.storeMat()
			m.moveTo(target.checker.getMatrix(viz.ABS_GLOBAL), time = 0.6)
		self._imploded = True
		self._keyBindings[3].setEnabled(viz.OFF)  #disable snap key down event

	def explode(self):
		"""
		move bones to position before implode was called
		"""
		for m in self._meshes[1:]:
			if m.getAction():
				return
			m.moveTo(m.loadMat(), time = 0.6)
		self._imploded = False
		self._keyBindings[3].setEnabled(viz.ON) #enable snap key down event

	def solve(self):
		"""
		operator used to toggle between implode and explode
		"""
		if self._imploded == False:
			self.implode()
		else:
			self.explode()

	def end(self):
		"""Do everything that needs to be done to end the puzzle game"""
		print "Puzzle Quitting!"
	#	score.close()
		model.proxManager.clearSensors()
		model.proxManager.clearTargets()
		model.proxManager.remove()
		self.unloadBones()
		for bind in self._keyBindings:
			bind.remove()

	def bindKeys(self):
		self._keyBindings.append(vizact.onkeydown('o', model.proxManager.setDebug, viz.TOGGLE)) #debug shapes
		self._keyBindings.append(vizact.onkeydown(' ', self.grab)) #space select
		self._keyBindings.append(vizact.onkeydown('65421', self.grab)) #numpad enter select
		self._keyBindings.append(vizact.onkeydown(viz.KEY_ALT_R, self.snapCheck))
		self._keyBindings.append(vizact.onkeyup(' ', self.release))
		self._keyBindings.append(vizact.onkeyup('65421', self.release))
		self._keyBindings.append(vizact.onkeydown('65460', self.viewcube.toggleModes)) # Numpad '4' key
		self._keyBindings.append(vizact.onkeydown(viz.KEY_CONTROL_R, self.solve))
		
class FreePlayMode(PuzzleController):
	def __init__(self):
		super(FreePlayMode, self).__init__()

class TestMode(PuzzleController):
	def __init__(self):
		super(TestMode, self).__init__()
		
		self._meshesDisabled	= []
		self._keystoneAdjacent	= {}
	
	def load(self, dataset = 'right arm'):
		"""
		Load datasets and initialize everything necessary to commence
		the puzzle game. Customized for test mode.
		"""
		
		# Dataset
		model.ds = model.DatasetInterface()
		
		self._quizPanel = view.TestSnapPanel()
		self._quizPanel.toggle()

		# Proximity management
		model.proxManager = vizproximity.Manager()
		target = vizproximity.Target(model.pointer)
		model.proxManager.addTarget(target)

		model.proxManager.onEnter(None, self.EnterProximity)
		model.proxManager.onExit(None, self.ExitProximity)
	
		#Setup Key Bindings
		self.bindKeys()
		
		# start the clock
		time.clock()

		self.score = PuzzleScore()
		
#		viztask.schedule(soundTask(glove))
		self._meshesToLoad = model.ds.getOntologySet(dataset)
		self.loadMeshes(self._meshesToLoad)

		# Hide all of the meshes
		for m in self._meshes:
			m.disable()
		
		# Randomly select keystone(s)
		rand = random.sample(self._meshes, 3)
		print rand
		self._keystones += rand
		rand[0].enable()
		rand[0].setPosition([0.0,1.5,0.0])
		rand[0].setEuler([0.0,90.0,180.0])
		rand[0].group.grounded = True
		for m in rand[1:]:
			m.enable()
			self.snap(m, rand[0], add = False)
			print 'snapping ', m.name
		
		# Randomly enable some adjacent meshes
		disabled = [m for m in self._meshes if not m.getEnabled()]
		keystone = random.sample(self._keystones, 1)[0]
		self._keystoneAdjacent.update({keystone:[]})
		for m in self.getAdjacent(keystone, disabled)[:4]:
			print m
			m.enable(animate = False)
			self._keystoneAdjacent[keystone].append(m)
		#snapGroup(smallBoneGroups)
		self.quizSource = keystone
		self.quizTarget = random.sample(self._keystoneAdjacent[self.quizSource],1)[0]
		self._quizPanel.setFields(self.quizSource.name, self.quizTarget.name)

	def getAdjacent(self, mesh, pool):
		"""
		Sort pool by distance from mesh
		"""
		self.moveCheckers(mesh)
		neighbors = []
		
		for m in pool:
			centerPos = m.getPosition(viz.ABS_GLOBAL)
			checkerPos = m.checker.getPosition(viz.ABS_GLOBAL)
			dist = vizmat.Distance(centerPos, checkerPos)	
			neighbors.append([m,dist])
		
		sorted(neighbors, key = lambda a: a[1])
		
		return [l[0] for l in neighbors]

	def snapCheck(self):
		"""
		Snap checks for any nearby bones, and mates a src bone to a dst bone
		if they are in fact correctly placed.
		"""
		if not self._lastGrabbed:
			print 'nothing to snap'
			return
		
		SNAP_THRESHOLD = 0.5;
		DISTANCE_THRESHOLD = 1.5;
		ANGLE_THRESHOLD = 45;
		source = self._meshesById[self._lastGrabbed.id]
		self.moveCheckers(self._lastGrabbed)
			
		# Search through all of the checkers, and snap to the first one meeting our snap
		# criteria
		enabled = [m for m in self._meshes if m.getEnabled()]
		for bone in [b for b in enabled if b not in source.group.members]:
			targetSnap = bone.checker.getPosition(viz.ABS_GLOBAL)
			targetPosition = bone.getPosition(viz.ABS_GLOBAL)
			targetQuat = bone.getQuat(viz.ABS_GLOBAL)
			
			currentPosition = source.getPosition(viz.ABS_GLOBAL)
			currentQuat = source.getQuat(viz.ABS_GLOBAL)		
			
			snapDistance = vizmat.Distance(targetSnap, currentPosition)
			proximityDistance = vizmat.Distance(targetPosition, currentPosition)
			angleDifference = vizmat.QuatDiff(bone.getQuat(), source.getQuat())
			
			if (snapDistance <= SNAP_THRESHOLD) and (proximityDistance <= DISTANCE_THRESHOLD) \
					and (angleDifference < ANGLE_THRESHOLD):
				print 'Snap! ', source, ' to ', bone
				self.score.event(event = 'release', source = source.name, destination = bone.name, snap = True)
				viz.playSound(".\\dataset\\snap.wav")
				self.snap(source, bone)				
				if len(self._meshes) == len(source.group.members):
					print "Assembly completed!"
					end()
					menu.ingame.endButton()
				break
		else:
			print 'did not meet snap criteria'
			self._snapAttempts += 1
			self.score.event(event = 'release', source = source.name)
			
	def snap(self, sourceMesh, targetMesh, add = True):
		"""
		Overridden snap that adds more bones
		"""
		self.moveCheckers(sourceMesh)
		sourceMesh.moveTo(targetMesh.checker.getMatrix(viz.ABS_GLOBAL))
		targetMesh.group.merge(sourceMesh)
		if sourceMesh.group.grounded:
			self._keystones.append(sourceMesh)
		if add:
			# Add more bones
			disabled = [m for m in self._meshes if not m.getEnabled()]
			keystone = random.sample(self._keystones, 1)[0]
			try:
				m = self.getAdjacent(keystone, disabled)[random.randint(0,3)]
			except ValueError:
				m = self.getAdjacent(keystone, disabled)[0]
			m.enable(animate = True)
			
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
	print "Puzzle Quitting!"
	global controlInst
	try:
		controlInst.end()
	except AttributeError:
		print 'Not initialized'
	del(controlInst)

def start(mode, dataset):
	"""
	Start running the puzzle game
	"""
	global controlInst
	
	if mode == 'Free Play':
		controlInst = FreePlayMode()
	elif mode == 'Quiz Mode':
		controlInst = TestMode()
	controlInst.load(dataset)

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
	return raw


def soundTask(pointer):
	"""
	Function to be placed in Vizard's task scheduler
		looks through proximity list and searches for the closest bone to the glove and puts it at
		the beginning of the list, allows the bone name and bone description to be played
	"""
#	while True:
#		yield viztask.waitTime(0.25)
#		if(len(proximityList) >0):
#			bonePos = proximityList[0].getPosition(viz.ABS_GLOBAL)
#			pointerPos = pointer.getPosition(viz.ABS_GLOBAL)
#			shortestDist = vizmat.Distance(bonePos, pointerPos)
#			
#			for i,x in enumerate(proximityList):
#				proximityList[i].incProxCounter()  #increase count for how long glove is near bone
#				bonePos = proximityList[i].getPosition(viz.ABS_GLOBAL)
#				pointerPos = pointer.getPosition(viz.ABS_GLOBAL)
#				tempDist = vizmat.Distance(bonePos,pointerPos)
#				#displayBoneInfo(proximityList[0])
#
#				if(tempDist < shortestDist):
##					removeBoneInfo(proximityList[0])
#					shortestDist = tempDist
#					tempBone = proximityList[i]
#					proximityList[i] = proximityList[0]
#					proximityList[0] = tempBone
#			#tempBone = proximityList[0]
#			displayBoneInfo(proximityList[0])
#			
#			if proximityList[0].proxCounter > 2 and proximityList[0].getNameAudioFlag() == 1:
#				#yield viztask.waitTime(3.0)
#				vizact.ontimer2(0,0,playName,proximityList[0])
#				proximityList[0].clearProxCounter()
#				proximityList[0].setNameAudioFlag(0)
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