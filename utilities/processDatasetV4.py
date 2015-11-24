﻿# Written for BodyParts3D v4.0

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
overwrites = 0

filenames = os.listdir(DATASET_PATH)

for i, name in enumerate(filenames):
	if '.obj' not in name: continue
	with open(DATASET_PATH + name, 'rb') as f:
		header = f.read(5000)
		f.seek(0)
		thisData = {}
		try:
			thisData['concept']		= re.search(r'FMA[0123456789]+', header).group(0)
			thisData['representation'] = re.search(r'BP[0123456789]+', header).group(0)
			thisData['name']		= re.search(r'(?:English name : )([a-zA-Z ]+)', header).group(1)
			thisData['volume']		= float(re.search(r'(?:Volume\(cm3\): )([0-9.]+)', header).group(1))
			thisData['filename']	= name.strip('.obj')
			
			boundsRe				= re.search(r'(?:Bounds\(mm\): )\(([0-9.,-]+)\)-\(([0-9.,-]+)\)', header)
			boundsStr				= [boundsRe.group(1), boundsRe.group(2)]
			thisData['bounds']		= []
			for bound in boundsStr:
				thisData['bounds'].append([float(v) for v in bound.split(',')])
				
		except (AttributeError, KeyError):
			print "File " + name + ' is missing metadata.'
			continue
			
		thisData['centerPoint'] = getCenterOfMass(f)
		
		if metadata.has_key(thisData['concept']):
			overwrites += 1
			print 'Concept ', thisData['concept'], ' just got overwrote'
			
		metadata[thisData['filename']] = thisData
		knownFiles += 1

print knownFiles, ' files were parsed.'
print unknownFiles, ' files were not found. Possibly assembly names.'
print overwrites, ' overwrites occured.'

with open(DATASET_PATH + 'metadata.json','wb') as f:
	json.dump(metadata, f, indent = 1)