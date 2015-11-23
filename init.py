""" 
init.py

The purpose of this file is to organize all of the input and
output initilization code onto one place so that IO parameters 
can be changed efficiently. 
"""

# Builtin modules
import math

# Vizard modules
import viz
import vizact
import vizshape
import viztask
import vizproximity
import oculus

# Custom modules
import config
import games

# Dependencies
import numpy

class CameraKeyboardControl(viz.EventClass): 
	""" 
	This class handles the overloading of the arrow control 
	system so that control of the camera can be handeled with 
	only one hand
	"""	
	def __init__(self): 
		#IMPORTANT: We need to initialize base class 
		viz.EventClass.__init__(self) 
		#Register callback with our event class 
		self.callback(viz.KEYDOWN_EVENT ,self.onKeyDown)
		self.callback(viz.KEYUP_EVENT , self.onKeyUp)
		
		#initialize dictionary with key - value pairs
			
		#direction states
		self.state = {}
		self.state['right']	= '65459' # 3 key on numpad
		self.state['left']	= '65457' # 1 key on numpad
		self.state['up']	= '65461' # 5 key on numpad
		self.state['down']	= '65458' # 2 key on numpad
		
			#change cam center states
		#self.state['home'] = '65460'  # 4 key on the numpad
		self.state['bone_centered'] = '65462' # 6 key on the numpad
	
		#initilize  states
			
			#direction states
		self.right	= False
		self.left	= False
		self.up		= False
		self.down 	= False
		
			#camera focus states
		self.center	= False
		self.home	= False
		
	def onKeyDown(self,key):
		""" handles what happens when each key is pressed"""
		#print("down", key)
		
		#set state variables about if left and right keys are pressed
		#print(key)
		if key == self.state['right']:
			self.right = True
		elif key == self.state['left']:
			self.left = True
		elif key == self.state['up']:
			self.up = True
		elif key == self.state['down']:
			self.down = True
		elif key == self.state['bone_centered']:
			self.center = True	
		
	def onKeyUp(self, key):
		""" handles all key up events"""
		#print("up", key)
		#set state variables about if left and right keys are released
		if key == self.state['right']:
			self.right = False
		elif key == self.state['left']:
			self.left = False
		elif key == self.state['up']:
			self.up = False
		elif key == self.state['down']:
			self.down = False
		elif key == self.state['bone_centered']:
			self.center = False
			
	def cameraFocus(self,camcenter,camlink):
		"""
		Allows the user to focus the camera on an object in the 
		proximity list. Press the Center key ('6' on numpad) to focus,
		moving the bone will cause the camera to refocus on it when it is
		released.Press the Center key again to refocus on another object or 
		the default cam center position. 
		"""
		global focused
		
		toggle	= False
		focused	= None	
		
		while True:
			yield viztask.waitTime( .05 )
			if toggle and (focused != None):
				if(not puzzle.grabFlag):
					#puzzle.release()
					x = focused.getPosition(viz.ABS_GLOBAL)
					camcenter.setPosition(x, viz.ABS_GLOBAL)
					#puzzle.grab([focused])
					
			#Rudimentary focus change, allows for a change in the camcenter to focus
			#only works when a bone is inRange of the pointer object
			#Recenter camera
			if self.center:
				if len(puzzle.proximityList) != 0:
					focused = puzzle.proximityList[0]
					x = focused.getPosition(viz.ABS_GLOBAL)
					camcenter.setPosition(x, viz.ABS_GLOBAL)
					toggle = True
				elif toggle:
					focused = None
					camcenter.setPosition([0,0,0], viz.ABS_GLOBAL)
					toggle = False
				pass
			
	def performKeyMovements(self , camcenter , camlink):
		"""
		The loop that is submitted to the scheduler 
		to act and move the camera, or change the camera center
		
		camcenter object is a 3d node object that is supplied to the 
		camera keyboard control  object, that is the parent of the
		camera to be manipulated
		"""
		n = 0

		while True:
				#refresh rate should be 120Hz due to the fact that the Oculus refreshs at 120Hz
				yield viztask.waitTime(0.0066666666666667)
				
				#check direction arrows (numpad keys 123 and 5)
				if (self.right and self.left):
					
					#decrease viewing radius
					if self.up:
						camlink.preTrans([0,0,.05])
						
					#increase viewing radius
					elif self.down:
						camlink.preTrans([0,0,-.05])
				
				#move right (only right pressed)
				elif self.right: 
					camcenter.setEuler([-1.5,0,0] , viz.REL_GLOBAL)
				
				#move left (only left pressed)
				elif self.left:
					camcenter.setEuler([1.5,0,0] , viz.REL_GLOBAL)
					
				#move up
				elif self.up:
					euler = camcenter.getEuler()
					if euler[1] > 48: #needed to subtract 30 deg
						pass
					else:
						camcenter.setEuler([0,1.5,0] , viz.REL_LOCAL)
				
				#move down
				elif self.down == True:
					#check if this move made us go through the floor
					if mainView.getPosition(viz.ABS_GLOBAL)[1] < 0: # y axis negative?
						pass
					else: # mainview above floor
						camcenter.setEuler([0,-1.5,0] , viz.REL_LOCAL)
					

class DisplayInstance():
	"""?"""
	def __init__(self, displayMode, camMode, device, pointer):
		self.displayMode = displayMode
		self.camMode = camMode
		self.device = device
		self.pointer = pointer
		self.display()
		self.cameraInput()
	
	def display(self):
		"""
		Initialize the display
		
		Mode selection:
			0 - Regular computer
			1 - 3D TV
			2 - Oculus rift
		"""
		if self.displayMode == 0:
			viz.setMultiSample(4)
			viz.fov(60)
			viz.window.setSize([1280,720])
			viz.go()
			viz.window.setFullscreenMonitor(1)
#			viz.go(viz.FULLSCREEN) #viz.FULLSCREEN

		elif self.displayMode == 1:
			viz.setMultiSample(4)
			viz.go(viz.STEREO_HORZ | viz.FULLSCREEN)
			
		elif self.displayMode == 2:
			viz.go(viz.STEREO_HORZ)
			viz.setMultiSample(16)
			viz.window.setSize([1280,720])
			
			KEYS = {
				'reset'		: 'r',
				'camera'	: 'c'}
			
			# Helps reduce latency
			#do not use ? makes things worse.
			#viz.setOption('viz.glFinish',1)
		
		elif self.displayMode == 3:
			viz.setMultiSample(4)
			viz.fov(60)
			viz.go(viz.FULLSCREEN) #viz.FULLSCREEN
			viz.window.setFullscreenMonitor(2)

		# Initial direction of main view
		viz.MainView.setEuler([0,0,0])
		viz.MainView.setPosition([0,0,-3], viz.REL_LOCAL)
	
	def cameraInput(self):
		"""
		Initialize the camera movement controls
	
		Mode selection:
			0 - Arrow keys circular movement
			1 - Spacemouse (WARNING: potential conflict with pointer mode 1)
			2 - Wiimote (Not implemented)
		"""
		if self.camMode == 0:
			# Use the arrow keys to move
			self.camcenter = viz.addChild('ball.wrl')
			self.camcenter.setPosition(0,1.4,0)
			self.pointer.setParent(self.camcenter)
			self.camcenter.disable(viz.RENDERING)
		
	#		#occulus Rift enabled
			if(self.displayMode == 2):
				self.hmd = oculus.Rift()
				navigationNode = viz.addGroup()
				viewlink = viz.link(navigationNode, viz.MainView)
				viewlink.preMultLinkable(self.hmd.getSensor())
				camlink = viz.link(self.camcenter,navigationNode)
				
				#set initial positions
				camlink.preEuler([0,0,0])
				camlink.preTrans([0,0,-3.25])
				

			#2D display
			else:
				camlink = viz.link(self.camcenter,viz.MainView)
			
				#set initial positions
				camlink.preEuler([0,30,0])
				camlink.preTrans([0,0,-5])

			
			#instantiate control class
			controlScheme = CameraKeyboardControl()
			
			#schedule the control loop to be called
			viztask.schedule(controlScheme.performKeyMovements(self.camcenter, camlink))
			viztask.schedule(controlScheme.cameraFocus(self.camcenter, camlink))		
			
			#backup control functions:
			vizact.whilekeydown(viz.KEY_RIGHT,self.camcenter.setEuler,[vizact.elapsed(-90),0,0],viz.REL_GLOBAL)
			vizact.whilekeydown(viz.KEY_LEFT,self.camcenter.setEuler,[vizact.elapsed(90),0,0],viz.REL_GLOBAL)
			vizact.whilekeydown(viz.KEY_UP,self.camcenter.setEuler,[0,vizact.elapsed(90),0],viz.REL_LOCAL)
			vizact.whilekeydown(viz.KEY_DOWN,self.camcenter.setEuler,[0,vizact.elapsed(-90),0],viz.REL_LOCAL)
			vizact.whilekeydown( 't' , camlink.preTrans,[0,0,vizact.elapsed(-4)])
			vizact.whilekeydown( 'g' ,  camlink.preTrans,[0,0,vizact.elapsed(4)])
		
		
			default = self.camcenter.getPosition()


		elif self.camMode == 1:
			# Use the SpaceMouse to move camera
			MOVE_SCALE = 0.5
			ROTATE_SCALE = 5.0
			
			def UpdateMovement():
				elapsed = viz.getFrameElapsed()
				trans = device.getRawTranslation()
				rx,ry,rz = device.getRawRotation()
				viz.MainView.setAxisAngle([0,1,0,ry*elapsed*ROTATE_SCALE], viz.HEAD_ORI, viz.REL_LOCAL)
				viz.MainView.move(viz.Vector(trans)*elapsed*MOVE_SCALE)
			
			vizact.onupdate(0, UpdateMovement)

	#	elif mode == 2:
	#		# wiimote
	#		pass

		else:
			raise ValueError('Invaid control mode selection')
		
def onCollide(e):
	print("collision")
	pointer.setVelocity([0,0,0],viz.ABS_GLOBAL)

def loadColiseum():
	"""loads colosseum enviornment"""
	sf = .5
	colosseum = viz.addChild('.\\dataset\\environment\\coliseum.OSGB')
	colosseum.setEuler([0, -90, 0])
	colosseum.setScale([sf, sf, sf])
	colosseum.setPosition([-37.5*sf, 0.0, 0.0]) #center colisseum

	pedistal = viz.addChild('.\\dataset\\environment\\capital.OSGB')
	pedistal.setScale([100,100,100])
	pedistal.setPosition([0,-7.26,0]) #Found by testing

def loadTemple(bounding = True):
	"""loads temple enviornment"""
	
	sf = 100
	temple = viz.addChild('.\\dataset\\environment\\temple.OSGB')
	temple.setEuler([0,90,0])
	temple.setScale([sf,sf,sf])
	temple.setPosition([0,-1.569, 0]) #Found by measuring

	pedistal = viz.addChild('.\\dataset\\environment\\Column.OSGB')
	pedistal.setScale([3.0,3.0,3.0])
	pedistal.setPosition([0,-1.5,0]) #Found by testing
	if bounding == True:
		dimensions = [2,4,1]
		boundingBox = games.puzzleView.WireFrameCube(dimensions)
#		boundingBox.setPosition(0,dimensions[1],0)
		boundingBox.alpha(0.25)

def pointerInput(mode, pointer, arena):
	viz.phys.enable()
	"""
	Initialize the pointer tool
	
	Mode selection:
		0 - Keyboard driven
		1 - Spacemouse (WARNING: potential conflict with camera mode 1)
	"""
	
	proxy = vizproximity.Manager()
	proxy.setDebug(viz.TOGGLE)
	
	theSensor = vizproximity.addBoundingBoxSensor(arena, scale=[0.95, 0.95, 0.95])
	theTarget = vizproximity.Target(pointer)
	
	proxy.addSensor(theSensor)
	proxy.addTarget(theTarget)
		
	vizact.onkeydown('l',pointer.setPosition,[0,1,0])
	vizact.onkeydown('l',pointer.setVelocity,[0,0,0])	
	vizact.onkeydown('l',pointer.setAngularVelocity,[0,0,0])
	
	if mode == 0:
		# Keyboard driven pointer, in case you don't have a space mouse
		# wx/da/ez control
		
		#For keyboard controls the glove is only linked via orientation
		#linking via position was causing issues with the camera focusing feature
		#fixedRotation = viz.link(viz.MainView,pointer)
		#fixedRotation.setMask(viz.LINK_ORI)
		
		speed = 3.0
		vizact.whilekeydown('w',pointer.setPosition,[0,vizact.elapsed(speed),0],viz.REL_LOCAL)
		vizact.whilekeydown('x',pointer.setPosition,[0,vizact.elapsed(-speed),0],viz.REL_LOCAL)
		vizact.whilekeydown('d',pointer.setPosition,[vizact.elapsed(speed),0,0],viz.REL_LOCAL)
		vizact.whilekeydown('a',pointer.setPosition,[vizact.elapsed(-speed),0,0],viz.REL_LOCAL)
		vizact.whilekeydown('e',pointer.setPosition,[0,0,vizact.elapsed(speed)],viz.REL_LOCAL)
		vizact.whilekeydown('z',pointer.setPosition,[0,0,vizact.elapsed(-speed)],viz.REL_LOCAL)
		
	elif mode == 1:
		# Set up pointer control with the Spacemouse
		connexion = viz.add('3dconnexion.dle')
		device = connexion.addDevice()		

		def buttonPress(e):
			pointer.setPosition([0,1,0])
			pointer.setVelocity([0,0,0])
			pointer.setAngularVelocity([0,0,0])
			
		viz.callback(viz.SENSOR_DOWN_EVENT,buttonPress)
		
		#call this every loop
		#all of this should likely go in controls, we need to fix controls!! -ADE
		def getCoords(source, destination, log = False):
			"""
			source should be a 3D connection device, and 
			the destination should be a 3d node type
			"""
			while True:
				yield viztask.waitTime( .01 ) 
				position	= source.getRawTranslation()
				orientation	= source.getRawRotation()
				
				#sets the velocity of the glove (destination) to zero 
				destination.setVelocity([0,0,0], viz.ABS_GLOBAL)
				destination.setAngularVelocity([0,0,0] ,viz.ABS_GLOBAL)
				
				#if selected do log scale on orientation
				if log:
					config.SMEulerScale= [0.5, 0.5 , 0.5]
					orientation = logScale(orientation)

				#rescale position
				position	= list(numpy.multiply(position,config.SMPositionScale))
				orientation	= list(numpy.multiply(orientation,config.SMEulerScale))
				
				#invert signs of x and z 
				x,y,z = position
				
				#invert signs of x and z rotations, and exchange b and a
				a,b,g		= orientation
				orientation	= [b,a,g]
				
				destination.setPosition(position, viz.REL_PARENT)
				destination.setEuler(orientation, viz.REL_PARENT)

		#schedule controller loop with viztask scheduler
		viztask.schedule(getCoords(device, pointer))
		
		return device
		
	else:
		raise ValueError('Invaid control mode selection')	

def EnterProximity(e):
	#print('Hit the wall')
	pointer.setVelocity([0,0,0])
	pointer.setAngularVelocity([0,0,0])
	print(e.target.getPosition())
	temp = e.target.getPosition()
	#pointer.setPosition([1,1,1])

def ExitProximity(e):
	#print('Hit the wall')
	x,y,z = pointer.getPosition()
	
	if(y < .4):
		y = .5
	elif(y > 4.5 ):
		y = 4.4
	if(abs(x) > abs(z) and abs(x) > 5):
		if(x<0):
			x = -4.9
		else:
			x = 4.9
	elif(abs(z) > 4):
		if(z<0):
			z = -3.9
		elif(z>0):
			z = 3.9
	pointer.setPosition(x,y,z)
	pointer.setVelocity([0,0,0])
	pointer.setAngularVelocity([0,0,0])

				
def logScale(orientation):
	""" 
	list or len() = 3 -> list of len 3 
	takes the orintation list and returns the log of
	the magnitude of each element , and then keeps the 
	original sign
	
	ex) [ 10 , -10 , 1000] -> [1 , -1, 3]
	"""
	base			= 2
	mag_orientation	= []
	sign			= [] #list of signs
	
	#make all elements positive, store original signs
	for element in orientation:
		if element >= 0:
			#element is positive
			mag_orientation.append(element)
			sign.append(1)
		else:
			#element is negative
			mag_orientation.append(-1 * element)
			sign.append(-1)
	#handle case where number is zero, and set to 1
	n = 0
	for element in mag_orientation:
		if element == 0:
			mag_orientation[n] = 1
		n += 1
	
	#take log of each element
	log_orientation = []
	for element in mag_orientation:
		log = math.log(element, base)
		log_orientation.append(log)
	
	#restablish original signs
	orientation = list(numpy.multiply(sign, log_orientation))
	
	return orientation