import config

class Dataset():
	def __init__(self):
		self.partOfElement = self.parseOntology('partof_element_parts.txt')
		self.allMetaData  = self.parseMetaData() # Dictionary of dictionary with concept ID as key
		
	def getFile(self, concept):
		pass
		
	def getConcept(self, file):
		pass
		
	def getEntry(self, concept = None, file = None):
		"""
		Returns all associated metadata with a particular entity in a dictionary
		"""
		metaData = {}
		if concept:
			try:
				return self.allMetaData[concept]
			except KeyError:
				print 'Unknown FMA concept id ' + concept
		elif file:
			filenames = [self.allMetaData[n] for n in self.allMetaData.keys()]
			indexByFile = zip(filenames, self.allMetaData.keys())
			try:
				return indexByFile[file]
			except KeyError:
				print 'Unknown filename ' + file
		else:
			print 'No search criteria specified'
		
	def parseOntology(self, filename):
		FMAPartOfElement = {}
		with open(config.DATASET_PATH + filename, 'rb') as f:
			reader = csv.reader(f, delimiter = '\t')
			reader.next()
			for line in reader:
				if not FMAPartOfElement.has_key(line[1]):
					FMAPartOfElement[line[1]] = []
				else:
					FMAPartOfElement[line[1]].append(line[2])
		return FMAPartOfElement
		
	def parseMetaData(self):
		with open(PATH + 'metadata.json','rb') as f:
			return json.load(f)