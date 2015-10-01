# Vizard display instance
display = None

meshes = None

def appendMesh(mesh):
	"""Store mesh"""
	global meshes
	meshes[mesh.id] = mesh

def getMesh(value):
	"""Return a mesh instance with given ID"""
	if type(value) == int:
		return meshes[value]

def getMeshes():
	"""Return all loaded meshes"""
	return meshes.values()