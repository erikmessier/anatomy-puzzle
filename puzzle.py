"""
puzzle.py

This file provides all methods and objects necessary to 
run the anatomy puzzle game.
"""

# Vizard modules
import viz
import vizact
import vizmat
import vizshape
import vizproximity
import viztask

# Python built-in modules
import random
import json
import math
import csv
import time
import datetime

# Custom modules
import init
import menu
import config
import datasetHandler

### Constants
#Delay to bone name sound
boneNameDelay = 1
# Scale factor
SF = 1.0/200

glove = None

def init():
	"""Flush global variables"""
	global RUNNING
	global bones
	global bonesById
	global bonesByName
	global groups
	global boneInfo
	global proximityList
	global inRange
	global gloveLink
	global grabFlag
	global keyBindings
	global closestBoneIdx
	global prevBoneIdx
	global lastGrabbed
	
	RUNNING = False
	bones = []
	bonesById = {}
	bonesByName = {}
	groups = []
	boneInfo = {}
	proximityList = []
	keyBindings = []
		
	inRange = []
	lastGrabbed = 'initValueLastGrabbed'
	gloveLink = None
	grabFlag = False

def __init__(self):
	pass
	
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

def loadMeshes(meshes = [], animate = False, randomize = True):
	"""Load all of the bones from the dataset into puzzle.bone instances"""
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
		
		bones.append(b)
		bonesByName[fileName] = b
		bonesById[b.id] = b

	return bones

def unloadBones():
	"""Unload all of the bone objects to reset the puzzle game"""
	for b in bones:
#		b.textRemove()
		b.remove(children = True)
	
def transparency(source, level, includeSource = False):
	"""Set the transparency of all the bones"""
	if includeSource:
		for b in bones:
			b.setAlpha(level)
	else:
		for b in [b for b in bones if b != source]:
			b.setAlpha(level)			

def moveCheckers(sourceChild):
	"""
	Move all of the checker objects on each bone into position, in order to
	see if they should be snapped.
	"""
	source = bonesById[sourceChild.id]
	
	for bone in [b for b in bones if b != source]:
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
	source = getBone(lastGrabbed.id)
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

#class FreePlayMode(PuzzleController):
#	def __init__(self):
#		pass
#
#class TestMode(PuzzleController):
#	def __init__(self):
#		pass

class BoneGroup():
	"""
	BoneGroup object manages a group of bones that need to stay
	fused to each other. Besides keeping a list of bones, it also
	has methods necessary to allow ease of group management
	"""
	def __init__(self, members):
		self.members = []
		self.addMembers(members)

		#Grounding for environment setup
		self.grounded = False
	
	def setParent(self, parent):
		"""Set bone to parent of all other bones in the group"""
		curMat = parent.getMatrix(viz.ABS_GLOBAL)
		parent.setParent(viz.WORLD)
		parent.setMatrix(curMat, viz.ABS_GLOBAL)
		
		for m in [m for m in self.members if m != parent]:
			curMat = m.getMatrix(viz.ABS_GLOBAL)
			m.setParent(parent)
			m.setMatrix(curMat, viz.ABS_GLOBAL)
	
	def addMembers(self, members):
		"""Add a list of Bone objects to the members list"""
		self.members += members
		for m in members:
			m.group = self
	
	def merge(self, source):
		"""Merge group members into this group and delete"""
		self.members += source.group.members
		#del source.group
		for b in source.group.members:
			b.setGroup(self)

class Mesh(viz.VizNode):
	"""
	Bone object is a customized version of VizNode that is design to accomodate
	obj files from the BodyParts3D database.
	"""
	def __init__(self, fileName, SF = 1.0/200):
		"""Pull the BodyParts3D mesh into an instance and set everything up"""
		self.metaData = ds.getMetaData(file = fileName)
		self.centerPoint = self.metaData['centerPoint']
		print self.centerPoint
		self.centerPointScaled = [a*SF for a in self.centerPoint]
		self.centerPointScaledFlipped = [a*SF*-1 for a in self.centerPoint]
		print self.centerPointScaledFlipped
		
		self.name = self.metaData['name']

		self.nameFormatted = ''
		for i, w in enumerate(self.name.split()):
			if (i + 1) % 2 == 0 and i != 0: 
				self.nameFormatted += w + '\n'
			else:
				self.nameFormatted += w + ' ' 
		
		#give a bone an information property
#		self.info = ''
#		for j,bd in enumerate(boneDesc['info'].split()):
#			if(j+1) % 10 ==0 and j != 0:
#				self.info += bd + ' \n'
#			else: 
#				self.info += bd + ' '
		
		# We are using a 'center' viznode to make manipulation easy
		self.center = vizshape.addCube(0.1) # An arbitrary placeholder cube
		viz.VizNode.__init__(self, self.center.id)
		
		# This is the actual mesh we will see
		self.mesh = viz.addChild(config.DATASET_PATH + fileName + '.obj')
		self.mesh.setScale([SF,SF,SF])
		
		# This is the viznode that will be moved around to check distances for snapping
		self.checker = vizshape.addCube(10.0)
		
		# Tooltip
		self.tooltip = viz.addText(self.nameFormatted)
		self.tooltip.billboard(viz.BILLBOARD_VIEW)
		self.tooltip.setScale(0.001,0.001,0.001) #small scale for bounding box calc
		
		#Description

#		if display.displayMode == 2:
#			self.dialogue = viz.addText(self.info,pos = [0,3,0],parent=viz.WORLD)
#			self.dialogue.billboard(viz.BILLBOARD_VIEW)
#			self.dialogue.setBackdrop(viz.BACKDROP_CENTER_TOP)
#			self.dialogue.setScale(0.15,0.15,0.15)
#			self.dialogue.alignment(viz.ALIGN_CENTER_CENTER)
#			#self.dialogue.setPosition([0.03,0.85,0])
#			#self.dialogue.color(viz.BLACK)
#		else:
#			self.dialogue = viz.addText(self.info,parent=viz.SCREEN)
#			#self.dialogue.setBackdrop(viz.BACKDROP_CENTER_TOP)
#			self.dialogue.setScale(0.3,0.3,0.0)
#			self.dialogue.alignment(viz.ALIGN_LEFT_BOTTOM)
#			self.dialogue.setPosition([0.03,0.85,0])
#			#self.dialogue.color(viz.BLACK)
		
		# Setup heirarchy for proper movement behavior
		self.mesh.setParent(self)
		self.tooltip.setParent(self)
		self.checker.setParent(self.mesh)
		
		# Offset mesh to lie in center of center viznode
		self.mesh.setPosition(self.centerPointScaledFlipped, viz.ABS_PARENT)
		self.checker.setPosition(self.centerPoint)
	
		self.addSensor()
		
		# Tooltip formatting
		self.tooltip.setScale(0.1,0.1,0.1) #set to prefered scale
		self.tooltip.setPosition(0,0,.5)
		self.tooltip.alignment(viz.TEXT_CENTER_CENTER)
		
		# Turn off visibility of center and checker viznodes
#		self.disable([viz.RENDERING])
		self.color([0.3,0,0])
		self.checker.disable([viz.RENDERING,viz.INTERSECTION,viz.PHYSICS])
#		self.tooltip.disable([viz.RENDERING])
		#self.dialogueBox.disable([viz.RENDERING])
#		self.dialogue.disable([viz.RENDERING])
		
		self.scale = SF
#		self.phys = self.collideSphere()

		
		self.nameAudioFlag = 1    #defualt: 1, 1 allows name to be played, 0 does not allow name playback
		self.descAudioFlag = 1		#default: 1, 1 allows description to be played, 0 does not allow dec playback
		self.grabbedFlag = 0
		self.proxCounter = 0
		
		
		# Group handling
		self.group = BoneGroup([self])
		groups.append(self.group)
		
	
	def incProxCounter(self):
		"""used to determine how long the glove is close to a bone. 
			helps with debouncing for sound output
		"""
		self.proxCounter += 1
	
	def clearProxCounter(self):
		"""resets the counter for how long glove is close to bone"""
		self.proxCounter  = 0
	
	def addSensor(self):
		"""Add a sensor to a proximity manager"""
		sensor = vizproximity.addBoundingSphereSensor(self)
		manager.addSensor(sensor)
		
	def setGroupParent(self):
		"""
		When manipulating a group of bones, the grabbed bone must move all
		of the other group members
		"""
		self.group.setParent(self)

	def setGroup(self, group):
		"""Set bone group"""
		self.group = group
	
	def setAlpha(self, level):
		"""Set bone alpha level"""
		self.mesh.alpha(level)
	
	def snap(self, target, animate = True):
		"""Invoked by the puzzle.snap method to handle local business"""
		moveCheckers(self)
		targetPosition = target.checker.getPosition(viz.ABS_GLOBAL)
		targetEuler = target.checker.getEuler(viz.ABS_GLOBAL)		
		# WARNING the full setMatrix cannot be assigned because scale is different!
		if (animate):
			move = vizact.moveTo(targetPosition, time = 0.3)
			spin = vizact.spinTo(euler = targetEuler, time = 0.3)
			transition = vizact.parallel(spin, move)
			self.addAction(transition)
		else:
			self.setPosition(targetPosition, viz.ABS_GLOBAL)
			self.setEuler(targetEuler,viz.ABS_GLOBAL)

		target.group.merge(self)
		
	def grabSequence(self):
		"""
		jascha, if you want this somewhere else, we can change the location
		calling this method will activate the bones tooltip render
		"""
		self.tooltip.enable([viz.RENDERING])
		
		try: #play audio with the same name as the bone
			viz.playSound(".\\dataset\\Skull\\audio_names\\" + self.name + ".wav")
		except ValueError:
			print ("the name of the audio file was wrong")
		
	def releaseSequence(self):
		"""
		calling this method will disable rendering on the bones tooltip
		"""
		self.tooltip.disable([viz.RENDERING])
		
	def setNameAudioFlag(self, flag):
		"""
		True to allow bone name playback
		"""
		self.nameAudioFlag = flag
	
	def playDescription(self):
		"""
		Play the Bone description audio
		"""
		try:
			#print ("play " + boneObj.name + " description")
			viz.playSound(path + "audio_descriptions2\\" + self.name + ".wav")
		except ValueError:
			print ("the name of the audio description file was wrong")
	
	def getNameAudioFlag(self):
		"""
		return self.nameAudioFlag
		"""
		return self.nameAudioFlag
		
	def getGrabbedFlag(self):
		"""
		return self.grabbedFlag
		"""
		return self.grabbedFlag
		
	def setGrabbedFlag(self,flag):
		"""
		used for determining if a bone was grabbed or not
		True if bone was grabbed
		"""
		self.grabbedFlag = flag
	
	def displayBoneInfo(self):
		"""Displays the bone description and bone tool tip"""
		self.tooltip.enable([viz.RENDERING])
		self.dialogue.enable([viz.RENDERING])
		
	def removeBoneInfo(self):
		"""removes bone description and bone tool tip and clears the proximity counter used for debouncing"""
		self.tooltip.disable([viz.RENDERING])
#		self.dialogue.disable([viz.RENDERING])
		self.clearProxCounter()
			
	def getDescAudioFlag(self):
		""" return seld.descAudioFlag """
		return self.descAudioFlag
		
	def setDescAudioFlag(self,val):
		"""
		used to determine whether or not to play bone description audio
		0 = do not play dec audio
		1 = play desc audio
		"""
		self.descAudioFlag = val

class viewCube():
	"""
	the viewCube is an object that sits above the location
	where the skull is to be assembeled(the podium) and provides
	anatomical locational information (AP/ RL/ IS). There should
	also be a principle plane mode that shows midsagittal, frontal
	and transverse. the player should be able to toggle between these
	modes with a putton press.The parent of the viewcube is the podium
	"""
	def __init__(self):
		"""sets up viewcube and principle planes"""
		#Should appear ontop of podium
		
		self.modeCounter = 0 #Will be used to determine mode
		SF = 1 #Scale box
		
		#------------(AP/RL/SI) + cube mode setup-------------
		
		#add text objects set positions
		self.anterior = viz.addText('Anterior',pos = [0 ,SF*.5 ,SF*.5])
		self.posterior = viz.addText('Posterior',pos = [0, SF*.5 ,SF*-.5])
		self.left = viz.addText('Left', pos = [SF*-.5 ,SF*.5 ,0])
		self.right = viz.addText('Right', pos = [SF*.5 ,SF*.5 ,0])
		self.superior = viz.addText('Superior', pos = [0 ,SF*1.0 ,0])
		self.inferior = viz.addText('Inferior', pos = [0 ,SF*.01 ,0])
		
		#set orientation
		self.anterior.setEuler([180,0,0])
		self.posterior.setEuler([0,0,0])
		self.left.setEuler([90,0,0])
		self.right.setEuler([-90,0,0])
		self.superior.setEuler([0,90,0])
		self.inferior.setEuler([0,90,0])
		
		#set scale
		self.anterior.setScale([.1,.1,.1])
		self.posterior.setScale([.1,.1,.1])
		self.left.setScale([.1,.1,.1])
		self.right.setScale([.1,.1,.1])
		self.superior.setScale([.1,.1,.1])
		self.inferior.setScale([.1,.1,.1])
		
		#set each text object to be centered
		self.anterior.alignment(viz.ALIGN_CENTER_CENTER)
		self.posterior.alignment(viz.ALIGN_CENTER_CENTER)
		self.left.alignment(viz.ALIGN_CENTER_CENTER)
		self.right.alignment(viz.ALIGN_CENTER_CENTER)
		self.superior.alignment(viz.ALIGN_CENTER_CENTER)
		self.inferior.alignment(viz.ALIGN_CENTER_CENTER)
	
		#turn off rendering
		self.anterior.disable([viz.RENDERING])
		self.posterior.disable([viz.RENDERING])
		self.left.disable([viz.RENDERING])
		self.right.disable([viz.RENDERING])
		self.superior.disable([viz.RENDERING])
		self.inferior.disable([viz.RENDERING])

		#consider changing size, font, shading etc.
		
		#add cube
		RADIUS = .5 *SF
		self.cube = wireframeCube([RADIUS,RADIUS,RADIUS])
		self.cube.setPosition([0,RADIUS, 0] , viz.ABS_PARENT)
		
		#turn off visability
		self.cube.visible(viz.OFF) 
		
		#---------------principle plane setup------------------------
		self.frontalPlane    = vizshape.addPlane(size = [1*SF ,1*SF] , axis = vizshape.AXIS_Z ,cullFace = False)
		self.transversePlane = vizshape.addPlane(size = [1*SF ,1*SF] , axis = vizshape.AXIS_Y ,cullFace = False)
		self.sagittalPlane   = vizshape.addPlane(size = [1*SF ,1*SF] , axis = vizshape.AXIS_X , cullFace = False)
		
		#setPosition(up in y so that origin is at bottom)
		self.frontalPlane.setPosition([0,SF*.5,0])
		self.transversePlane.setPosition([0,SF*.5,0])
		self.sagittalPlane.setPosition([0,SF*.5,0])
	
		#set alpha
		self.frontalPlane.alpha(.5)
		self.transversePlane.alpha(.5)
		self.sagittalPlane.alpha(.5)
		
		#set color
		self.frontalPlane.color([1,1,.5])
		self.transversePlane.color([1,1,.5])
		self.sagittalPlane.color([1,1,.5])
		
		#add text labels to upper corners of planes
		self.frontalLabel  = viz.addText('Frontal Plane',pos = [.5*SF ,SF*.5 , .01*SF]) #.01 prevents overlap with plane
		self.transverseLabel  = viz.addText('Transverse Plane',pos = [-.5*SF , .01*SF ,SF*.5]) 
		self.sagittalLabel = viz.addText('Sagittal Plane',pos = [.01*SF ,SF*.5 ,SF*-.5])
		
		#scale text labels
		self.frontalLabel.setScale([.1,.1,.1])
		self.transverseLabel.setScale([.1,.1,.1])
		self.sagittalLabel.setScale([.1,.1,.1])
		
		#set planes to be parents of labels
		self.frontalLabel.setParent(self.frontalPlane)
		self.transverseLabel.setParent(self.transversePlane)
		self.sagittalLabel.setParent(self.sagittalPlane)

		#orient text labels
		self.frontalLabel.setEuler([180,0,0])
		self.transverseLabel.setEuler([0,90,0])
		self.sagittalLabel.setEuler([-90,0,0])
		
		#set alignment of Text labels
		self.frontalLabel.alignment(viz.ALIGN_LEFT_TOP)
		self.transverseLabel.alignment(viz.ALIGN_LEFT_TOP)
		self.sagittalLabel.alignment(viz.ALIGN_LEFT_TOP)
		
		#disable rendering on planes
		self.frontalPlane.disable([viz.RENDERING])
		self.transversePlane.disable([viz.RENDERING])
		self.sagittalPlane.disable([viz.RENDERING])
		
		#disable rendering of Text labels
		self.frontalLabel.disable([viz.RENDERING])
		self.transverseLabel.disable([viz.RENDERING])
		self.sagittalLabel.disable([viz.RENDERING])

	def toggleModes(self):
		"""
		This function will switch viewcube between its 3 modes:
		- off
		- (AP/RL/SI) + cube mode
		- principle plane mode
		"""
		#logic so that each function gets called every 3rd time
		self.modeCounter += 1
		
		if self.modeCounter % 4 == 1:
			#(AP/RL/SI) + cube mode
		
			#enable rendering on labels
			self.anterior.enable([viz.RENDERING])
			self.posterior.enable([viz.RENDERING])
			self.left.enable([viz.RENDERING])
			self.right.enable([viz.RENDERING])
			self.superior.enable([viz.RENDERING])
			self.inferior.enable([viz.RENDERING])
			
			#enable rendering on cube
			self.cube.visible(viz.ON)
			
		elif self.modeCounter % 4 == 2:
			# principle plane mode
			
			#disable rendering of labels
			self.anterior.disable([viz.RENDERING])
			self.posterior.disable([viz.RENDERING])
			self.left.disable([viz.RENDERING])
			self.right.disable([viz.RENDERING])
			self.superior.disable([viz.RENDERING])
			self.inferior.disable([viz.RENDERING])
			
			#disable rendering of cube
			self.cube.visible(viz.OFF)
			
			#enable rendering of principle planes
			self.frontalPlane.enable([viz.RENDERING])
			self.transversePlane.enable([viz.RENDERING])
			self.sagittalPlane.enable([viz.RENDERING])
			
			#enable rendering of plane labels
			self.frontalLabel.enable([viz.RENDERING])
			self.transverseLabel.enable([viz.RENDERING])
			self.sagittalLabel.enable([viz.RENDERING])
		
		elif self. modeCounter % 4 == 3:
			#both on
			
			#planes previously enabled
			
			#enable rendering of(AP/RL/SI) + cube mode
			#enable rendering on labels
			self.anterior.enable([viz.RENDERING])
			self.posterior.enable([viz.RENDERING])
			self.left.enable([viz.RENDERING])
			self.right.enable([viz.RENDERING])
			self.superior.enable([viz.RENDERING])
			self.inferior.enable([viz.RENDERING])
			
			#enable rendering on cube
			self.cube.visible(viz.ON)
			
		elif self.modeCounter % 4 == 0:
			#all off
			
			#disable rendering of(AP/RL/SI) + cube mode
			#disable rendering of labels
			self.anterior.disable([viz.RENDERING])
			self.posterior.disable([viz.RENDERING])
			self.left.disable([viz.RENDERING])
			self.right.disable([viz.RENDERING])
			self.superior.disable([viz.RENDERING])
			self.inferior.disable([viz.RENDERING])
			
			#disable rendering of cube
			self.cube.visible(viz.OFF)
			
			#rendering of planes
			#disable rendering of principle planes
			self.frontalPlane.disable([viz.RENDERING])
			self.transversePlane.disable([viz.RENDERING])
			self.sagittalPlane.disable([viz.RENDERING])
			
			#disable rendering of plane labels
			self.frontalLabel.disable([viz.RENDERING])
			self.transverseLabel.disable([viz.RENDERING])
			self.sagittalLabel.disable([viz.RENDERING])
			
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
		"""Iterative score calculation"""
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

def snapGroup(boneNames):
	"""Specify a list of bones that should be snapped together"""
	print boneNames
	if (len(boneNames) > 0):
		bones = []
		[[bones.append(getBone(b)) for b in group] for group in boneNames]
		[b.snap(bones[0], animate = False) for b in bones[1:]]
	
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

def grab():
	"""Grab in-range objects with the pointer"""
	global gloveLink
	global grabFlag
	global closestBoneIdx
	global lastGrabbed
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
	global gloveLink
	global grabFlag
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
	
def load(dataset = 'right arm'):
	"""
	Load datasets and initialize everything necessary to commence
	the puzzle game.
	"""
	
	global RUNNING
	global path
	global manager
	global ds
	
	if not RUNNING:
		init() # Flush everything
		
		RUNNING = True
		
		# Dataset
		ds = datasetHandler.Dataset()

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
	getBone(source.id).mesh.color([1.0,1.0,0.5])
	getBone(source.id).setNameAudioFlag(1)
	proximityList.append(source)
	

def ExitProximity(e):
	source = e.sensor.getSourceObject()
	getBone(source.id).mesh.color([1.0,1.0,1.0])
	getBone(source.id).setNameAudioFlag(0)
	proximityList.remove(source)
#	removeBoneInfo(getBone(source.id))

def bindKeys():
	global keyBindings
	keyBindings.append(vizact.onkeydown('o', manager.setDebug, viz.TOGGLE)) #debug shapes
	keyBindings.append(vizact.onkeydown(' ', grab)) #space select
	keyBindings.append(vizact.onkeydown('65421', grab)) #numpad enter select
	keyBindings.append(vizact.onkeydown(viz.KEY_ALT_R, snap))
	keyBindings.append(vizact.onkeyup(' ', release))
	keyBindings.append(vizact.onkeyup('65421', release))

	
def setDisplay(displayInstance):
	"""
	Set the instance of the display
	Need to know if the display is oculus or not
	"""
	global display
	display = displayInstance

def setPointer(pointer):
	"""Set puzzle module global pointer"""
	global glove
	glove = pointer
	
def getBone(value):
	"""Return a bone instance with given ID or Name"""
	if type(value) == int:
		return bonesById[value]
	elif type(value) == str:
		return bonesByName[value]

def wireframeCube(dimensions):
	edges = [[x,y,z] for x in [-1,0,1] for y in [-1,0,1] for z in [-1,0,1] if abs(x)+abs(y)+abs(z) == 2]
	for edge in edges:
		viz.startLayer(viz.LINES)
		viz.vertexColor(0,1,0)
		i = edge.index(0)
		edge[i] = 1
		viz.vertex(map(lambda a,b:a*b,edge,dimensions))
		edge[i] = -1
		viz.vertex(map(lambda a,b:a*b,edge,dimensions))
	cube = viz.endLayer()
	return cube