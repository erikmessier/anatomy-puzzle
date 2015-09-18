import config
import csv, json

class Dataset():
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