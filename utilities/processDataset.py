import csv
import re
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

#csv = csv.writer(DATASET_PATH + csvName)
#csv.writerow(['filename','name','description','x','z','y'])

metadata = {}
knownFiles, unknownFiles = 0, 0

with open(DATASET_PATH + 'parts_list_e.txt', 'rb') as f:
	for line in f:
		if not re.search(r'FMA|BP',line): continue
		filename, name = line.split()[0], ' '.join(line.split()[1:])
		metadata[filename] = {'name':name}

for k in metadata.keys():
	try:
		with open(DATASET_PATH + k + '.obj', 'rb') as f:
			metadata[k].update(zip(['x','z','y'], getCenterOfMass(f)))
			knownFiles += 1
	except IOError:
		metadata.pop(k)
		unknownFiles += 1
	

print str(knownFiles) + ' files were parsed.'
print str(unknownFiles) + ' files were not found. Possibly assembly names.'

with open(DATASET_PATH + 'metadata.json','wb') as f:
	json.dump(metadata, f, indent = 1)