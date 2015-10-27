"""
Just a bunch of constants defining running configuration
"""

# Vizard modules
import vizshape
import collections

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
	monitor		= 0
	tv			= 1
	oculus		= 2
	fullscreen	= 3
	label = {'Regular Computer': 0, '3D TV': 1, 'Occulus Rift': 2, 'Full Screen': 3}

dispMode = DisplayMode.monitor

menuScaleConfig = { \
	0:{'main':1.2, 'game':.75, 'ingame': 1, 'test':2}, \
	1:{'main':.5, 'game':.3, 'ingame': 1, 'test': 1}, \
	2:{'main':1, 'game':0.75, 'ingame': 1, 'test': 2}, \
	3:{'main':1.2, 'game':.75, 'ingame': 1, 'test':2}}
menuScale = menuScaleConfig[dispMode]

##############################
# Camera control mode options:
##############################
class CameraMode:
	#  0 - arrow button  keyboard control
	#  1 - SpaceMouse control
	#  2 -  Wiimote control
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
	keyboard	= 0
	spaceMouse	= 1
	label = {'Keyboard Control': 0, 'SpaceMouse Control': 1}

pointerMode = PointerMode.keyboard

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
	('Bone', 'bone organ'), \
	('Muscle', 'muscle organ')]
	Layers = collections.OrderedDict(_key_value_Layers)

	_key_value_Modes = [\
		('Free Play', 'free play description'),\
		('Quiz Mode', 'test play description'),\
		('Movement Tutorial', 'movement tutorial description')]
	Modes = collections.OrderedDict(_key_value_Modes)

HELP_MESSAGE = \
'''
Welcome to the puzzle game demo!
Drag and drop the bones together to complete the anatomical model.
Controls:
	Press and hold space bar to grab bones
	Use the arrow keys to move the camera
	Use 'o' key to toggle proximity spheres
Note: This demo requires the 3D Connexion SpaceMouse. If you do not have
a SpaceMouse, see the code to enable wx/ad/ze control of the glove instead.
'''

"""
Position and Orientation Vectors Scales for spacemouse control 
"""
positionVector = [.00005,.00005,.00005]
orientationVector = [0,0,0]
