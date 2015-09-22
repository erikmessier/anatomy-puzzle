"""
config.py

Just a bunch of constants defining running configuration
"""

# Where is the dataset in relation to where I am?
DATASET_PATH = '.\\dataset\\full\\'

# Display mode options:
class Displays:
	# pseudo enumerated type
	#  0 - Regular computer
	computer = 0
	#  1 - 3D TV
	tv = 1
	#  2 - Oculus rift
	oculus = 2
	label = {'Regular Computer': 0, '3D TV': 1, 'Occulus Rift': 2}

dispMode = Displays.computer
menuScaleConfig = { \
	0:{'main':1.2, 'game':.75, 'ingame': 1}, \
	1:{'main':.1, 'game':.3, 'ingame': 1}, \
	2:{'main':1, 'game':.3, 'ingame': 1}}
menuScale = menuScaleConfig[dispMode]


# Camera control mode options:
#  0 - arrow button  keyboard control
#  1 - SpaceMouse control
#  2 - Wiimote control
camChoices = {'Keyboard Control': 0, 'SpaceMouse Control': 1, 'Wiimote Control': 2}
camMode = 0

# Pointer control mode options:
#  0 - X/Y/Z jog (tb/fh/vy)  keyboard control
#  1 - SpaceMouse control
#  2 - Mouse plane selection?
pointerChoices = {'Keyboard Control': 0, 'SpaceMouse Control': 1}
pointerMode = 0

"""
Dictionary of lists:
- used for game menu layer selections, currently only the skeletal system layers are available.
- format in dictionary: {superset: [subset, subset, etc.]}
- format in menu: superset is label for tab panel, subsets can be selected using check boxes from the tab panel.
"""
layers = {'Axial':['skull', 'skeletal system of thorax'], 'Upper Appen.': ['right free upper limb', 'left free upper limb'], 'Lower Appen.': ['right free lower limb', 'left free lower limb', 'pelvic girdle']}


"""
Available modes for selection
"""
modes = {'Free Play': 'free play description', 'Test Mode': 'test play description'}

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
