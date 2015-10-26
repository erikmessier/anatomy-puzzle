# Written for BodyParts3D v4.0

import csv
import re
import os
import json

DATASET_PATH = '..\\dataset\\full\\'
csvName = 'metadata.csv'

def getCenterOfMass(file):
	# Adapted from http://www.pygame.org/wiki/OBJFileLoader
	cm = [0,0,0]
	verts = 0
	for line in file:
		if line.startswith('#'): continue
		values = line.split()
		if not values: continue
		if values[0] == 'v':
			xyz = map(float,values[1:4])
			cm = map((lambda a,b: a + b), cm,xyz)
			verts += 1
	cm = [v/verts for v in cm]
	return cm

metadata = {}
knownFiles, unknownFiles = 0, 0

filenames = os.listdir(DATASET_PATH)

for i, name in enumerate(filenames):
	if '.obj' not in name: continue
	with open(DATASET_PATH + name, 'rb') as f:
		header = f.read(5000)
		f.seek(0)
		thisData = {}
		try:
			thisData['concept'] = re.search(r'FMA[0123456789]+',header).group(0)
			thisData['representation'] = re.search(r'BP[0123456789]+',header).group(0)
			thisData['name'] = re.search(r'(?:English name : )[a-zA-Z ]+',header).group(0)[15:]
			thisData['filename'] = name.strip('.obj')
		except (AttributeError, KeyError):
			print "File " + name + ' is missing metadata.'
			continue
			
		thisData['centerPoint'] = getCenterOfMass(f)
		
		metadata[thisData['concept']] = thisData
		knownFiles += 1


print str(knownFiles) + ' files were parsed.'
print str(unknownFiles) + ' files were not found. Possibly assembly names.'

with open(DATASET_PATH + 'metadata.json','wb') as f:
	json.dump(metadata, f, indent = 1)