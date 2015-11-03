"""
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
		'Monitor': 0, \
		'TV': 1, \
		'Oculus': 2, \
		'Fullscreen': 3, \
	}
	monitor		= 0
	tv			= 1
	oculus		= 2
	fullscreen	= 3
	label = {'monitor': 0, 'tv': 1, 'oculus': 2, 'fullscreen': 3}

dispMode = DisplayMode.monitor

menuScaleConfig = { \
	0:{'main':1.2, 'mode': 1, 'layer':.75, 'ingame': 1, 'test':2}, \
	1:{'main':.5, 'mode': 1, 'layer':.3, 'ingame': 1, 'test': 1}, \
	2:{'main':1, 'mode': 1, 'layer':.3, 'ingame': 1, 'test': 2}, \
	3:{'main':1.2, 'mode': 1, 'layer':.75, 'ingame': 1, 'test':2}}
	
menuScale = menuScaleConfig[dispMode]

##############################
# Camera control mode options:
##############################
class CameraMode:
	#  0 - arrow button  keyboard control
	#  1 - SpaceMouse control
	#  2 -  Wiimote control
	MODES = {\
		'Keyboard': 0, \
		'SpaceMouse': 1, \
		'wiiMote': 2\
	}
	keyboard	= 0
	spaceMouse	= 1
	wiiMote		= 2
	label = {'Keyboard Control': 0, 'SpaceMouse Control': 1, 'Wiimote Control': 2}

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
class menuLayerSelection:
	_key_value_Regions = [\
		('Head',			['head']), \
		('Thorax',		['body proper']), \
		('Upper Appen.',	['free upper limb', 'right free upper limb', 'left free upper limb']), \
		('Lower Appen.', ['right free lower limb', 'left free lower limb', 'muscle of lower limb'])]
	Regions = collections.OrderedDict(_key_value_Regions)
	
	_key_value_Layers = [\
	('Bone', ['bone organ']), \
	('Muscle', ['muscle organ']), \
	('Test', ['left lung', 'right lung'])]
	Layers = collections.OrderedDict(_key_value_Layers)

	_key_value_Modes = [ \
		('Free Play', games.puzzleGame.FreePlay), \
		('Quiz Mode', games.puzzleGame.TestPlay), \
		('Movement Tutorial', games.tutorialGame.InterfaceTutorial)]
		
	Modes = collections.OrderedDict(_key_value_Modes)

"""
Available modes for selection
"""

class Modes:
	freePlay	= games.puzzleGame.FreePlay
	quizPlay	= games.puzzleGame.TestPlay
	tutorial	= games.tutorialGame.InterfaceTutorial

"""
Position and Orientation Vectors Scales for spacemouse control 
"""

SMPositionScale	= [.0001,.0001,.0001]
SMEulerScale	= [0.001, 0.001, 0.001]

# Colors of the various tissue layes
colors = { \
	'muscle organ':	(1.0, 0.5, 0.5), \
	'bone organ':	(1.0, 1.0, 0.8)}
