"""
Model components of the Puzzle game
"""

# Built-in modules
import csv, json

# Vizard Modules
import viz
import vizact, vizshape, vizproximity, viztask

# Custom modules
import config
import model

# Bone groups
groups = []

class MeshGroup(object):
	"""
	MeshGroup object manages a group of bones that need to stay
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
		self.members = list(set(self.members))
		#del source.group
		for b in source.group.members:
			b.setGroup(self)
		
		
class Mesh(viz.VizNode):
	"""
	Mesh object is a customized version of VizNode that is design to accomodate
	obj files from the BodyParts3D database.
	"""
	def __init__(self, fileName, SF = 1.0/500):
		"""Pull the BodyParts3D mesh into an instance and set everything up"""
		self.snapAttempts = 0
		self.metaData = model.ds.getMetaData(file = fileName)
		self.centerPoint = self.metaData['centerPoint']
		self.centerPointScaled = [a*SF for a in self.centerPoint]
		self.centerPointScaledFlipped = [a*SF*-1 for a in self.centerPoint]
		
		self.name = self.metaData['name']
		for region, names in config.OntologicalGroups.regions.iteritems():
			files = model.ds.getOntologySet([(set.union, names)])
			if self.metaData['filename'] in files:
				self.region = region
				break
		else:
			self.region = None

		self.nameFormatted = ''
		for i, w in enumerate(self.name.split()):
			if (i + 1) % 2 == 0 and i != 0: 
				self.nameFormatted += w + '\n'
			else:
				self.nameFormatted += w + ' '
		
		# We are using a 'center' viznode to make manipulation easy
		self.center = vizshape.addCube(0.001) # An arbitrary placeholder cube
		super(Mesh, self).__init__(self.center.id)
		
		# This is the actual mesh we will see
		self.mesh = viz.addChild(config.DATASET_PATH + fileName + '.obj')
		self.mesh.setScale([SF,SF,SF])
		
		# This is the viznode that will be moved around to check distances for snapping
		self.checker = vizshape.addCube(0.001)
		
		# Setup heirarchy for proper movement behavior
		self.mesh.setParent(self)
		self.checker.setParent(self.mesh)
		
		# Offset mesh to lie in center of center viznode
		self.mesh.setPosition(self.centerPointScaledFlipped, viz.ABS_PARENT)
		self.checker.setPosition(self.centerPoint)
		
		#Line between tooltip and mesh centerPoint
#		viz.startLayer(viz.LINES)
#		viz.vertexColor(viz.BLUE)
#		viz.lineWidth(5)
#		viz.vertex(self.getPosition(viz.ABS_GLOBAL))
#		viz.vertex(self.tooltip.getPosition(viz.ABS_GLOBAL))
#		self.nameLine = viz.endLayer()
#		self.nameLine.dynamic()
#		self.nameLine.visible(viz.OFF)
		
		# Turn off visibility of center and checker viznodes
		self.mesh.color(self.metaData['color'])
		self.checker.disable([viz.RENDERING,viz.INTERSECTION,viz.PHYSICS])
		self.center.disable([viz.RENDERING,viz.INTERSECTION,viz.PHYSICS])
		
		self.scale		= SF
		self._enabled	= True
		self.grounded	= False

		self.grabbedFlag	= 0
		self.proxCounter	= 0
		
		# Group handling
		self.group = MeshGroup([self])
#		groups.append(self.group)
		
	def enable(self, animate = False):
		"""Turn on visibility/set enabled flag"""
		self._enabled = True
		if animate:
			fadein = vizact.fadeTo(1.0, time = 1.0)
			self.mesh.alpha(0.0)
			self.mesh.visible(viz.ON)
			self.mesh.addAction(fadein)
			#self.tooltip.alpha(0.0)
			#self.tooltip.visible(viz.ON)
			#self.tooltip.addAction(fadein)
		else:
			self.mesh.visible(viz.ON)
			#self.tooltip.visible(viz.ON)
		model.proxManager.addSensor(self._sensor)
		
	def disable(self):
		"""Turn off visibility/set enabled flag"""
		self._enabled = False
		self.mesh.visible(viz.OFF)
#		self.tooltip.visible(viz.OFF)
		model.proxManager.removeSensor(self._sensor)
	
	def highlight(self, prox = False, grabbed = False, closest = False):
		if closest:
			self.color([4,0.5,0.5])
		elif grabbed:
			self.color([0.0,1.0,0.5])
			self.tooltip.visible(viz.ON)
		else:
			if prox:
				self.color([1.0,1.0,0.5])
				self.tooltip.visible(viz.OFF)
			elif not prox:
				self.color(reset = True)
				self.tooltip.visible(viz.OFF)
	
	def grab(self):
		pass
		
	def getEnabled(self):
		return self._enabled
		
	def storeMat(self, relation = viz.ABS_GLOBAL):
		"""Store current transformation matrix"""
		self._savedMat = self.getMatrix(relation)
		
	def loadMat(self):
		"""Recall stored transformation matrix"""
		return self._savedMat
	
	def incProxCounter(self):
		"""
		Used to determine how long the glove is close to a bone. Helps with
		debouncing for sound output
		"""
		self.proxCounter += 1
	
	def clearProxCounter(self):
		"""Resets the counter for how long glove is close to bone"""
		self.proxCounter = 0
		
	def addToolTip(self):
		self.tooltip = viz.addText(self.nameFormatted)
		self.tooltip.visible(viz.OFF)
		self.tooltip.color(0,5,1)
		self.tooltip.setParent(self.center)
		self.tooltip.billboard(viz.BILLBOARD_VIEW)
		self.tooltip.setScale(0.1,0.1,0.1) #set to prefered scale
		self.tooltip.setPosition(0,0,-1)
		self.tooltip.alignment(viz.TEXT_CENTER_CENTER)
		
	def addSensor(self):
		"""Add a sensor to a proximity manager"""
		if self.metaData['volume'] < 12:
			SF = 2*(12 - self.metaData['volume'])/12
			self._sensor = vizproximity.addBoundingSphereSensor(self, scale = (1+ 1*SF))
		else:
			self._sensor = vizproximity.addBoundingSphereSensor(self)
		model.proxManager.addSensor(self._sensor)
		
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
		
	def color(self, value = (1,1,1), reset = False):
		"""Set the color of the mesh"""
		if reset:
			self.mesh.color(self.metaData['color'])
		else:
			self.mesh.color(value)

	def moveTo(self, matrix, animate = True, time = 0.3, relation = viz.ABS_GLOBAL):
		"""
		Invoked by the puzzle.snap method to handle local business
		"""
		# WARNING the full setMatrix cannot be assigned because scale is different!
		if (animate):
			move = vizact.moveTo(matrix.getPosition(), time = time, mode = relation)
			spin = vizact.spinTo(euler = matrix.getEuler(), time = time, mode = relation)
			transition = vizact.parallel(spin, move)
			self.addAction(transition)
		else:
			self.setPosition(targetPosition, relation)
			self.setEuler(targetEuler, relation)

	def setNameAudioFlag(self, flag):
		"""True to allow bone name playback"""
		self.nameAudioFlag = flag
	
	def playDescription(self):
		"""Play the Bone description audio"""
		try:
			#print ("play " + boneObj.name + " description")
			viz.playSound(path + "audio_descriptions2\\" + self.name + ".wav")
		except ValueError:
			print ("the name of the audio description file was wrong")
		
	def removeBoneInfo(self):
		"""Removes bone description and bone tool tip and clears the proximity counter used for debouncing"""
		self.tooltip.disable([viz.RENDERING])
#		self.dialogue.disable([viz.RENDERING])
		self.clearProxCounter()
	
	def getNameAudioFlag(self):
		"""Return self.nameAudioFlag"""
		return self.nameAudioFlag
		
	def getGrabbedFlag(self):
		"""Return self.grabbedFlag"""
		return self.grabbedFlag
		
	def setGrabbedFlag(self, flag):
		"""
		Used for determining if a bone was grabbed or not
		True if bone was grabbed
		"""
		self.grabbedFlag = flag
	
	def displayBoneInfo(self):
		"""Displays the bone description and bone tool tip"""
		self.tooltip.enable([viz.RENDERING])
		self.dialogue.enable([viz.RENDERING])
			
	def getDescAudioFlag(self):
		"""Return seld.descAudioFlag """
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
		partOfElement = self.parseElementOntology('partof_element_parts.txt')
		isAElement = self.parseElementOntology('isa_element_parts.txt')
		self.fullOntology = {}
		self.fullOntology.update(partOfElement)
		self.fullOntology.update(isAElement)
		
		self.ontologyByName = {}
		names = [self.fullOntology[n]['name'] for n in self.fullOntology.keys()]
		self.ontologyByName.update(dict(zip(names, self.fullOntology.values())))
		
		self.allMetaData  = self.parseMetaData() # Dictionary of dictionary with concept ID as key
		
	def getByConcept(self, concept):
		"""Get filenames(s) by concept id"""
		pass
		
	def getByName(self, name):
		"""Get filenames(s) by concept name"""
		pass
			
	def getOntologySet(self, searchSets):
		"""
		Pull in filenames to load using a collection of set search
		groups. Takes in a set of tuples specifying an operation (i.e. set.intersection,
		set.union and set of set(s) on which to perform that operation, thus 
		filtering the desired subset.
		"""
		modelSet = []
		for searchSet in searchSets:
			setOperation = searchSet[0] # First entry should be the operation
			filenames = []
			for s in searchSet[1:]:
				# Unpack groups of FMA concept names to FJ filenames
				filenames.append([])
				for conceptName in s:
					try:
						filenames[-1].extend(self.ontologyByName[conceptName]['filenames'])
					except KeyError:
						print 'Unknown name ', str(conceptName), '!'
						continue
				filenames[-1] = set(filenames[-1])
			modelSet.extend(list(setOperation(*filenames)))
		
		#remove all files from modelSet that are also found in ignoreSets
		ignoreSets = config.ignoreSets
		removeFromModelSet = []
		for ignoreSet in ignoreSets:
			try:
				removeFromModelSet.extend(self.ontologyByName[ignoreSet]['filenames'])
			except KeyError:
#				print 'Unknown name for ignore set: ', str(ignoreSet)
				continue
		removeFromModelSet = set(removeFromModelSet)
		
		modelSet = set(modelSet) - removeFromModelSet
		
		return list(modelSet)
		
	def getPreSnapSet(self):
		#create lists of filenames that should be presnapped together
		preSnapSets = config.preSnapMeshes
		preSnap = []
		regionSet = []
		featureSet = []
		for preSnapSetRegion in preSnapSets.keys():
			try:
				regionSet.extend(self.ontologyByName[preSnapSetRegion]['filenames'])
			except KeyError:
				print 'Unknown name for ignore set: ', str(ignoreSet)
				continue
			for preSnapSetFeature in preSnapSets[preSnapSetRegion]:
				if preSnapSetFeature:
					try:
						featureSet.extend(self.ontologyByName[preSnapSetFeature]['filenames'])
					except KeyError:
						print 'Unknown name for ignore set: ', str(ignoreSet)
						continue
				else:
					featureSet = regionSet
				listOfFiles = set.intersection(set(regionSet), set(featureSet))
				featureSet = []
				preSnap.append(list(listOfFiles))
			regionSet = []
				
		return preSnap
		
	def getMetaData(self, concept = None, file = None):
		"""
		Returns all associated metadata with a particular entity in a dictionary
		"""
		if concept:
			print 'Pulling in multiple pieces of metadata not supported'
			return None
		elif file:
			try:
				thisMD = self.allMetaData[file]
			except KeyError:
				print 'Unknown filename!'
				return None
		else:
			print 'No search criteria specified'
			return None
		
		return thisMD
		
	def getColor(self, filename):
		"""Pull in coloring from config, if it is defined"""
		for ontologyName in config.colors.keys():
			if filename in self.ontologyByName[ontologyName]['filenames']:
				return config.colors[ontologyName]
				break
		else:
			return (1,1,1)
			
	def parseElementOntology(self, filename):
		"""
		Parse ontological relationship files supplied with the BodyParts3D dataset release.
		Currrently only designed to handle isa_element* and partof_element* files.
		"""
		elementOntology = {}
		with open(config.DATASET_PATH + filename, 'rb') as f:
			reader = csv.reader(f, delimiter = '\t')
			reader.next()
			for line in reader:
				if not elementOntology.has_key(line[0]):
					elementOntology[line[0]] = {'concept':line[0],'name':line[1],'filenames':[line[2]]}
				else:
					elementOntology[line[0]]['filenames'].append(line[2])
		return elementOntology
		
	def parseMetaData(self):
		with open(config.DATASET_PATH + 'metadata.json','rb') as f:
			full = json.load(f)
			
		for thisMD in full.values():
			thisMD['centerPoint'] = rightToLeft(thisMD['centerPoint'])
			thisMD['color'] = self.getColor(thisMD['filename'])
		
		return full
	
def rightToLeft(center):
	"""
	Convert from right handed coordinate system to left handed
	"""
	return [center[0], center[1], center[2]*-1]