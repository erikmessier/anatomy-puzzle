import json, csv

DATASET_PATH = '..\\dataset\\full\\'
csvName = 'metadata.csv'

class layers():
	bone	= {name: 'bone',	fma: ['bone organ']}
	muscle	= {name: 'muscle',	fma: ['muscle organ']}
	other	= {name: 'other',	fma: []}

class regions():
	head	= {name: 'head',	fma: ['head']}
	thorax	= {name: 'thorax',	fma: ['body proper']}
	upperApp = {name: 'Upper Appendicular',	fma: ['right upper limb', 'left upper limb']}
	lowerApp = {name: 'Lower Appendicular',	fma: ['right lower limb', 'left lower limb']}
	other	= {name: 'other',	fma: []}

class DatasetInterface():
	def __init__(self):
		self.partOfElement = self.parseElementOntology('partof_element_parts.txt')
		self.isAElement = self.parseElementOntology('isa_element_parts.txt')
		self.allMetaData  = self.parseMetaData() # Dictionary of dictionary with concept ID as key
		self.indexByName = {}
		
		names = [self.partOfElement[n]['name'] for n in self.partOfElement.keys()]
		self.indexByName.update(dict(zip(names, self.partOfElement.values())))
		names = [self.isAElement[n]['name'] for n in self.isAElement.keys()]
		self.indexByName.update(dict(zip(names, self.isAElement.values())))
		
	def getConceptByFile(self, file):
		filenames = [self.allMetaData[n]['filename'] for n in self.allMetaData.keys()]
		indexByFile = dict(zip(filenames, self.allMetaData.values()))
		try:
			return indexByFile[file]['concept']
		except KeyError:
			print 'Unknown filename ' + file
			return None
	
	def getOntologySet(self, searchValue):
		"""
		Currently only supports seach by name
		"""
		if type(searchValue) == str:
			searchValue = [searchValue]
		modelSet = []
		for v in searchValue:
			try:
				modelSet.extend(self.indexByName[v]['filenames'])
			except KeyError:
				print 'Unknown name ' + str(searchValue)
		return set(modelSet)
		
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
			# silly dataset uses right-handed coordinate system
			thisMD['centerPoint'] = rightToLeft(thisMD['centerPoint'])
			return thisMD
		elif file:
			thisMD = self.allMetaData[self.getConceptByFile(file)]
			# silly dataset uses right-handed coordinate system
			thisMD['centerPoint'] = rightToLeft(thisMD['centerPoint'])
			return thisMD
		else:
			print 'No search criteria specified'
		
	def parseElementOntology(self, filename):
		elementOntology = {}
		with open(DATASET_PATH + filename, 'rb') as f:
			reader = csv.reader(f, delimiter = '\t')
			reader.next()
			for line in reader:
				if not elementOntology.has_key(line[0]):
					elementOntology[line[0]] = {'concept':line[0],'name':line[1],'filenames':[line[2]]}
				else:
					elementOntology[line[0]]['filenames'].append(line[2])
		return elementOntology
		
	def parseMetaData(self):
		with open(DATASET_PATH + 'metadata.json','rb') as f:
			return json.load(f)


ontology = DatasetInterface()

boneFiles = ontology.getOntologySet('bone organ')
muscleFiles = ontology.getOntologySet('muscle organ')
vessleFiles = ontology.getOntologySet('vasculature of body')

metadata = ontology.parseMetaData()

for concept in metadata:
	# Determine which layer
	if concept.filename in boneFiles:
		metadata[concept]['layer'] = layers.bone
	elif concept.filename in muscleFiles:
		metadata[concept]['layer'] = layers.muscle
	else:
		metadata[concept]['layer'] = layers.other
		
	# Determine which region
	
with open(DATASET_PATH + 'metadata.json','wb') as f:
	json.dump(metadata, f, indent = 1)