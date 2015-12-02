﻿"""
Just a bunch of constants defining running configuration
"""

# Vizard modules
import vizshape
import collections

# Custom modules
import games

# Where is the dataset in relation to where I am?
DATASET_PATH = '.\\dataset\\full\\'

##############################
# Display mode options:
##############################
class DisplayMode:
	"""pseudo enumerated diplsy types"""
	#  0 - Regular computer
	#  1 - 3D TV
	#  2 - Oculus rift
	MODES = {\
		'Monitor':		0, \
		'TV':			1, \
		'Oculus':		2, \
		'Fullscreen':	3}
	
	monitor		= 0
	tv			= 1
	oculus		= 2
	fullscreen	= 3
	label		= {'monitor': 0, 'tv': 1, 'oculus': 2, 'fullscreen': 3}

dispMode = DisplayMode.monitor

menuScaleConfig = { \
	0:{'main': 1.2, 'mode': 1.0, 'layer': 0.75, 'ingame': 1.0, 'test': 2.0, 'loading': 1.0}, \
	1:{'main': 0.5, 'mode': 1.0, 'layer': 0.30, 'ingame': 1.0, 'test': 1.0, 'loading': 1.0}, \
	2:{'main': 1.0, 'mode': 1.0, 'layer': 0.30, 'ingame': 1.0, 'test': 2.0, 'loading': 1.0}, \
	3:{'main': 1.2, 'mode': 1.0, 'layer': 0.75, 'ingame': 1.0, 'test': 2.0, 'loading': 1.0}}
	
menuScale = menuScaleConfig[dispMode]

##############################
# Camera control mode options:
##############################
class CameraMode:
	#  0 - arrow button  keyboard control
	#  1 - SpaceMouse control
	#  2 -  Wiimote control
	MODES = {\
		'Keyboard':		0, \
		'SpaceMouse':	1, \
		'wiiMote':		2}
		
	keyboard	= 0
	spaceMouse	= 1
	wiiMote		= 2
	label		= {'Keyboard Control': 0, 'SpaceMouse Control': 1, 'Wiimote Control': 2}

camMode = CameraMode.keyboard

##############################
# Pointer control mode options:
##############################

class PointerMode:
	#  0 - X/Y/Z jog (tb/fh/vy)  keyboard control
	#  1 - SpaceMouse control
	#  2 - Mouse plane selection?
	MODES = {\
		'Keyboard': 0, \
		'SpaceMouse': 1\
		}
	keyboard	= 0
	spaceMouse	= 1
	label = {'Keyboard Control': 0, 'SpaceMouse Control': 1}

pointerMode = PointerMode.spaceMouse

"""
Dictionary of lists:
- used for game menu layer selections, currently only the skeletal system layers are available.
- format in dictionary: {superset: [subset, subset, etc.]}
- format in menu: superset is label for tab panel, subsets can be selected using check boxes from the tab panel.
"""

#layers = { \
#	'Axial':['skull', 'skeletal system of thorax'], \
#	'Upper Appen.': ['right arm', 'left free upper limb', 'right hand'], \
#	'Lower Appen.': ['right free lower limb', 'left free lower limb', 'pelvic girdle', 'pelvis'], \
#	'Tissues': ['bone organ', 'muscle organ', 'neck', 'muscle of free upper limb']}
#

class OntologicalGroups:
	"""Manually defined ontological groups"""
	#Associates regions of the body with region concept name(s)
	_key_value_Regions = [\
		('Head',			['head', 'tooth']), \
		('Thorax',			['body proper', 'muscle of shoulder', 'sternum', 'muscle of pectoral girdle', 'muscle of vertebral column', 'muscle of neck', 'left lung', 'right lung', 'gastrointestinal tract', 'urinary system', 'heart', 'costal cartilage', 'cartilage organ component']), \
		('Upper Appen.',	['right free upper limb', 'left free upper limb', 'muscle of free upper limb']), \
		('Lower Appen.',	['right free lower limb', 'left free lower limb', 'muscle of lower limb'])]
	regions = collections.OrderedDict(_key_value_Regions)
	
	#Associates tissue layers of the body with the full layer concept name
	_key_value_Layers = [\
	('Bone',		['bone organ', 'tooth']), \
	('Cartilage',	['costal cartilage', 'cartilage organ component', 'nasal cartilage', 'cartilage organ']), \
	('Muscle',		['costal cartilage']), \
	('Organs',		['brain', 'left lung', 'right lung', 'gastrointestinal tract', 'urinary system', 'heart'])]
	layers = collections.OrderedDict(_key_value_Layers)

class MenuConfig:
	"""Used to model region-layer relationship, and to relate modes to their mode operations"""
	
	""" Developer Tool to disable checkboxes if no content is available for that layer
		Format: List(Tuple(Region, List(layers to ignore)))"""
	_key_value_RemoveCheckFromTab = [\
	('Head',		[]), \
	('Thorax',		[]), \
	('Upper Appen.', ['Organs', 'Cartilage']), \
	('Lower Appen.', ['Organs', 'Cartilage'])]
	RemoveCheckFromTab = collections.OrderedDict(_key_value_RemoveCheckFromTab)
	
	""" Relates mode to its mode operation"""
	_key_value_Modes = [ \
		('Free Play',		games.puzzleGame.FreePlay), \
		('Puzzle Quiz',		games.puzzleGame.TestPlay), \
		('Pin Drop Quiz',	games.puzzleGame.PinDrop), \
		('Movement Tutorial', games.tutorialGame.InterfaceTutorial)]
	Modes = collections.OrderedDict(_key_value_Modes)

"""
Available modes for selection
"""

class Modes:
	freePlay	= games.puzzleGame.FreePlay
	quizPlay	= games.puzzleGame.TestPlay
	pinDrop		= games.puzzleGame.PinDrop
	tutorial	= games.tutorialGame.InterfaceTutorial

"""
Position and Orientation Vectors Scales for spacemouse control 
"""

SMPositionScale	= [0.0001, 0.0001, 0.0001]
SMEulerScale	= [0.0010, 0.0010, 0.0010]

# Ignore filenames with these concept names when calculating union/intersection for loading final dataset
ignoreSets = ( \
	'portal vein', \
	'systemic vein', \
	'pulmonary vein', \
	'systemic artery', \
	'pulmonary artery', \
	'segment of bronchial tree', \
	'right hepatic biliary tree', \
	'left hepatic biliary tree', \
	'mitral valve', \
	'aortic valve', \
	'pulmonary valve', \
	'left hepatic duct', \
	'right hepatic duct', \
	'common hepatic duct', \
	'pancreatic duct tree', \
	'cystic duct', \
	'trunk of right portal vein', \
	'trunk of left portal vein', \
	'hepatic artery proper', \
	'pancreatic duct', \
	'coronary artery' \
	'leaf of cardiac valve', \
	'trunk of coronary artery', \
	'region of papillary muscle', \
	'leaflet of tricuspid valve', \
	'branch of left coronary artery', \
	'branch of right coronary artery', \
	'coronary sinus', \
	'region of papillary muscle', \
	'trunk of anterior interventricular branch of left coronary artery', \
	'trunk of right apical segmental vein', \
	'subdivision of left hepatic artery', \
	'subdivision of right hepatic artery', \
	'anterolateral head of lateral papillary muscle of left ventricle', \
	'anterolateral head of lateral papillary muscle of right ventricle', \
	'sesamoid bone')


# Colors of the various tissue layes
colors = { \
	'muscle organ':					(1.0, 0.5, 0.5), \
	'bone organ':					(1.0, 1.0, 0.8), \
	'brain':						(0.45, 0.7, 0.7), \
	'left lung':					(1.0, 0.70, 0.85), \
	'right lung':					(1.0, 0.70, 0.85), \
	'gastrointestinal tract': 		(1.0, 0.85, 0.6), \
	'heart':						(1.0, 0.45, 0.4), \
	'urinary system':				(1.0, 1.0, 0.4), \
	'costal cartilage':				(1.0, 0.85, 0.7), \
	'cartilage organ component':	(1.0, 0.85, 0.7), \
	'nasal cartilage':				(1.0, 0.85, 0.7)}

#PreSnap Meshes (region: feature)
preSnapMeshes = {\
	'left free upper limb':		['phalanx of finger', 'metacarpal bone', 'carpal bone'], \
	'right free upper limb':	['phalanx of finger', 'metacarpal bone', 'carpal bone'], \
	'left free lower limb':		['phalanx of toe', 'metatarsal bone', 'tarsal bone'], \
	'right free lower limb':	['phalanx of toe', 'metatarsal bone', 'tarsal bone'], \
	'vertebral column':			['cervical vertebral column', 'thoracic vertebral column', 'lumbar vertebral column'], \
	'zone of jejunum':			['zone of jejunum'], \
	'zone of ileum':			['zone of ileum'], \
	'rib':						['true rib', 'typical rib', 'false rib'], \
	'sternum':					['sternum'], \
	'costal cartilage':			['costal cartilage'], \
	'nasal cartilage':			['nasal cartilage'], \
	'tooth':					['tooth']}

# Scaling Factor for meshes
SF = 1.0/500


