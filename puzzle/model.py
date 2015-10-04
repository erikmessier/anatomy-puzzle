"""
Model components of the Puzzle game
"""

# Built-in modules
import csv, json

# Vizard Modules
import viz
import vizact, vizshape, vizproximity

# Custom modules
import config

# Vizard display instance
display = None

# Pointer instance
pointer = None

# Dataset interface
ds = None

# Proximity Manager
proxManager = None

# Bone groups
groups = []

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
		#super(Mesh, self).__init__(self.center.id) #This is better
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
		"""
		Used to determine how long the glove is close to a bone.
		helps with debouncing for sound output
		"""
		self.proxCounter += 1
	
	def clearProxCounter(self):
		"""resets the counter for how long glove is close to bone"""
		self.proxCounter  = 0
	
	def addSensor(self):
		"""Add a sensor to a proximity manager"""
		sensor = vizproximity.addBoundingSphereSensor(self)
		proxManager.addSensor(sensor)
		
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
		"""
		Invoked by the puzzle.snap method to handle local business
		"""
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
		i don't even
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

class DatasetInterface():
	def __init__(self):
		self.partOfElement = self.parseOntology('partof_element_parts.txt')
		self.allMetaData  = self.parseMetaData() # Dictionary of dictionary with concept ID as key
		
	def getConceptByFile(self, file):
		filenames = [self.allMetaData[n]['filename'] for n in self.allMetaData.keys()]
		indexByFile = dict(zip(filenames, self.allMetaData.values()))
		try:
			return indexByFile[file]['concept']
		except KeyError:
			print 'Unknown filename ' + file
	
	def getOntologySet(self, searchValue):
		"""
		Currently only supports seach by name
		"""
		names = [self.partOfElement[n]['name'] for n in self.partOfElement.keys()]
		indexByName = dict(zip(names, self.partOfElement.values()))
		if type(searchValue) == str:
			searchValue = searchValue.split('\0')
		set = []
		for v in searchValue:
			try:
				set.extend(indexByName[v]['filenames'])
			except KeyError:
				print 'Unknown name ' + searchValue
		print set
		return set
		
	def getMetaData(self, concept = None, file = None):
		"""
		Returns all associated metadata with a particular entity in a dictionary
		"""
		metaData = {}
		if concept:
			try:
				thisMD = self.allMetaData[concept]
			except KeyError:
				print 'Unknown FMA concept id ' + concept
				return
			# silly vizard uses XZY coordinates instead of XYZ coordinates
			thisMD['centerPoint'] = rightToLeft(thisMD['centerPoint'])
			return thisMD
		elif file:
			thisMD = self.allMetaData[self.getConceptByFile(file)]
			# silly vizard uses XZY coordinates instead of XYZ coordinates
			thisMD['centerPoint'] = rightToLeft(thisMD['centerPoint'])
			return thisMD
		else:
			print 'No search criteria specified'
		
	def parseOntology(self, filename):
		FMAPartOfElement = {}
		with open(config.DATASET_PATH + filename, 'rb') as f:
			reader = csv.reader(f, delimiter = '\t')
			reader.next()
			for line in reader:
				if not FMAPartOfElement.has_key(line[0]):
					FMAPartOfElement[line[0]] = {'concept':line[0],'name':line[1],'filenames':[]}
				else:
					FMAPartOfElement[line[0]]['filenames'].append(line[2])
		return FMAPartOfElement
		
	def parseMetaData(self):
		with open(config.DATASET_PATH + 'metadata.json','rb') as f:
			return json.load(f)

class Ontology():
	partOfElement = 0
	
def rightToLeft(center):
	"""Convert from right handed coordinate system to left handed"""
	return [center[0], center[1], center[2]*-1]