"""
Just a bunch of constants defining running configuration
"""

# Vizard modules
import vizshape
import collections

#For modalityGUI
import Tkinter
import json

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
	('Bone', 'bone organ'), \
	('Muscle', 'muscle organ')]
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

positionVector		= [.00005,.00005,.00005]
orientationVector	= [0,0,0]

# Colors of the various tissue layes
colors = { \
	'muscle organ':	(1.0, 0.5, 0.5), \
	'bone organ':	(1.0, 1.0, 0.8)}

class modalityGUI():
	def __init__(self):
		
		self.PATH = '.\\dataset\\configurations\\'
		
		"""initialization variables: reading from previous created file to find what selections were 
		storing values in variables"""
		try:
			with open(self.PATH + 'configurations.json','rb') as f:
				try:
					self.prevInput = json.load(f)
				except ValueError:
					print 'no previous input file!'
		except IOError:
			print 'file has not yet been created'
			
		try:
			self.dispMode = self.prevInput['dispMode']
			self.pointerMode = self.prevInput['pointerMode']
		except:
			self.dispMode = None
			self.pointerMode = None
		self.camMode = None
		self.proceed = True
		
		#create the window
		self.root = Tkinter.Tk()
		self.root.resizable(0,0)
		self.root.protocol('WM_DELETE_WINDOW', self.__CancelCommand)
		
		#modify root window
		self.root.title('Modality Selection: ')
		
		#create main frame and directions frame
		mainFrame = Tkinter.Frame(self.root)
		mainFrame.pack(side = Tkinter.LEFT)
		
		#display modality label
		displayModeLabel = Tkinter.Label(mainFrame, text = 'Display Mode: ', bg = 'blue', fg = 'white')
		displayModeLabel.pack_configure(side = Tkinter.TOP)
		
		#display modality frame for radio buttons
		dispFrame = Tkinter.Frame(mainFrame)
		dispFrame.pack(side = Tkinter.TOP)
		
		#creating display modality radio buttons
		self.vDisp = Tkinter.StringVar()
		self.vDisp.set('dispMode')
		
		
		for label in DisplayMode.MODES.keys():
			val = DisplayMode.MODES[label]
			self.dispModeRadio = Tkinter.Radiobutton(dispFrame, text = label, variable = self.vDisp, value = val, command = self.dispSelected)
			self.dispModeRadio.pack_configure(side = Tkinter.LEFT)
		
		#pointer modality label
		pointModeLabel = Tkinter.Label(mainFrame, text = 'Pointer Mode: ', bg = 'blue', fg = 'white')
		pointModeLabel.pack_configure(side = Tkinter.TOP)
		
		#pointer modality frame for radio buttons
		pointFrame = Tkinter.Frame(mainFrame)
		pointFrame.pack(side = Tkinter.TOP)
		
		#creating pointer modality radio buttons
		self.vPoint = Tkinter.StringVar()
		self.vPoint.set('pointMode')
		
		for label in PointerMode.MODES.keys():
			val = PointerMode.MODES[label]
			self.pointModeRadio = Tkinter.Radiobutton(pointFrame, text = label, variable =  self.vPoint, value = val, command = self.pointSelected)
			self.pointModeRadio.pack_configure(side = Tkinter.LEFT)
	
		#setting display modality and pointer modality to most previously selected
		self.vDisp.set(self.dispMode)
		self.vPoint.set(self.pointerMode)
	
		#creating next and exit button frame
		exitFrame = Tkinter.Frame(mainFrame)
		exitFrame.pack(side = Tkinter.LEFT)
		
		nextFrame = Tkinter.Frame(mainFrame)
		nextFrame.pack(side = Tkinter.RIGHT)
		
		#creating next and exit buttons
		nextButton = Tkinter.Button(nextFrame, text = 'Next', fg = 'white', bg = 'green', command = self.next)
		exitButton = Tkinter.Button(exitFrame, text = 'Exit', fg = 'white', bg = 'red', command = self.exit)
		nextButton.pack_configure(side = Tkinter.RIGHT)
		exitButton.pack_configure(side = Tkinter.LEFT)
		
		#start gui
		self.root.mainloop()
	
	def __CancelCommand(self):
		pass
	def dispSelected(self):
		radioValue = self.vDisp.get()
		self.dispMode = radioValue
	def pointSelected(self):
		radioValue = self.vPoint.get()
		self.pointerMode = radioValue
	def camSelected(self):
		pass
	def next(self):
		with open(self.PATH + 'configurations.json','wb') as f:
			self.configurations = {'dispMode': self.dispMode, 'pointerMode': self.pointerMode, 'proceed': self.proceed}
			for _ in self.configurations.values():
				if _ == None:
					return
			json.dump(self.configurations, f, indent = 1)
		self.root.destroy()
	def exit(self):
		self.proceed = False
		with open(self.PATH + 'configurations.json','wb') as f:
			self.configurations = {'dispMode': self.dispMode, 'pointerMode': self.pointerMode, 'proceed': self.proceed}
			json.dump(self.configurations, f, indent = 1)
		self.root.destroy()