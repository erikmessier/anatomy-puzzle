import viz
import vizshape
import vizact
import viztask

#import mouseHandler

class Control(viz.EventClass):


	def __init__(self,controlScheme):
		self.controlScheme = controlScheme
		viz.EventClass.__init__(self)
		self.camcenter = viz.VizChild
		self.pointer = viz.VizChild
		self.camlink = viz.VizLink
	
	def initializeScheme(self):
		self.callback(viz.MOUSEDOWN_EVENT,self.onMouseDown)


		self.initPointer()
		self.initCamera()
			

		return
	
	def initMouse(self):
		self.callback(viz.MOUSEDOWN_EVENT,self.onMouseDown)

	def initPointer(self):
		if self.controlScheme == "default":
			vizact.whilekeydown('w',self.pointer.setPosition,[0,vizact.elapsed(1),0],viz.REL_PARENT)
			vizact.whilekeydown('x',self.pointer.setPosition,[0,vizact.elapsed(-1),0],viz.REL_PARENT)
			vizact.whilekeydown('d',self.pointer.setPosition,[vizact.elapsed(1),0,0],viz.REL_PARENT)
			vizact.whilekeydown('a',self.pointer.setPosition,[vizact.elapsed(-1),0,0],viz.REL_PARENT)
			vizact.whilekeydown('e',self.pointer.setPosition,[0,0,vizact.elapsed(1)],viz.REL_PARENT)
			vizact.whilekeydown('z',self.pointer.setPosition,[0,0,vizact.elapsed(-1)],viz.REL_PARENT)
		elif self.controlScheme == "3dMouse":
			self.init3dMouse()


	def initCamera(self):
				
		self.pointer.setParent(self.camcenter)
	
		#Default camera keys
		vizact.whilekeydown(viz.KEY_RIGHT,self.camlink.setEuler,[vizact.elapsed(-90),0,0],viz.REL_GLOBAL)
		vizact.whilekeydown(viz.KEY_LEFT,self.camlink.setEuler,[vizact.elapsed(90),0,0],viz.REL_GLOBAL)
		vizact.whilekeydown(viz.KEY_UP,self.camlink.setEuler,[0,vizact.elapsed(90),0],viz.REL_LOCAL)
		vizact.whilekeydown(viz.KEY_DOWN,self.camlink.setEuler,[0,vizact.elapsed(-90),0],viz.REL_LOCAL)
		vizact.whilekeydown(viz.KEY_KP_0, camlink.preTrans,[0,0,vizact.elapsed(-4)])
		vizact.whilekeydown(viz.KEY_CONTROL_R, camlink.preTrans,[0,0,vizact.elapsed(4)])		
		
	def init3dMouse(self):
		connexion = viz.add('3dconnexion.dle')
		device = connexion.addDevice()
		device.setRotateScale([0,1,0])
		device.setTranslateScale([0,0,1])
		
		#link = viz.link(device, self.pointer, viz.REL_PARENT)
		#link.preEuler([0,90,0])

		myTask = viztask.schedule( getCoords(device,self.pointer))
	
	"""
	Sets the object which acts as the pointer
	"""
	def setpointer(self,pointer):
		self.pointer = pointer
		self.initPointer()
		
	"""
	Sets the object which acts as the camera center ( semi-sphere control scheme )
	"""
	def setCamcenter(self,cam):
		self.camcenter = cam
		self.camLink.remove
		self.camLink = viz.link(self.camcenter.getTrans(),viz.MainView)
		
	"""
	Depricated
	"""
	def onMouseDown(self,button):
		selectedObject = viz.pick()
		print(selectedObject.id)
		
	"""
	Returns the object which acts as the camera center ( semi-sphere control scheme )
	"""
	def getCamcenter(self):
		return self.camcenter
	
	"""
	Returns the object which acts as the pointer / selection tool
	"""
	def getPointer(self):
		return self.pointer


#_______________HELPER FUNCTIONS________________

#call this every loop
def getCoords(source, destination):
	"""
	source should be a 3D connection device, and 
	the destination should be a 3d node type
	"""
	#set source scale
	scale1 = [.001,.001,.001]
	scale2 =[.01,.01,.01]
	#device.setTranslateScale(scale2)
	#device.setRotateScale(scale)
	
	while True:
		yield viztask.waitTime( .01 ) 
		position = source.getRawTranslation()
		orientation = source.getRawRotation()
		
		#rescale position
		position = scalarMult(position,scale1)
		orientation = scalarMult(orientation,scale2)
		
		#invert signs of x and z 
		x,y,z = position
		position = [-x,y,-z]
		
		#invert signs of x and z rotations, and exchange b and a
		a,b,g = orientation
		orientation = [b,-a,-g]
		
		
		#print(orientation)
		destination.setPosition(position, viz.REL_PARENT)
		destination.setEuler(orientation, viz.REL_PARENT)
		#print('position' + str())
	



def scalarMult(lst1,lst2):
	""" 
	takes 2 lists, and returns the scalar 
	multiplication of the lists
	*lists must be the same length
	"""
	new_lst = []
	for i in range(len(lst1)):
		n_val = lst1[i]*lst2[i]
		new_lst.append(n_val)
		
	return new_lst
