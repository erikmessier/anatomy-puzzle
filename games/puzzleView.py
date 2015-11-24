"""
View elements of the puzzle game
"""

# Vizard Modules
import viz
import vizdlg, vizshape, vizact, sys, os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

#custom module
import config
import menu

class TestSnapPanel(vizdlg.Panel):
	"""Test panel that test snap directions are sent to"""
	def __init__(self):
		"""Init canvas and create themes for the test panel"""
		self.canvas = viz.addGUICanvas(parent = viz.ABS_GLOBAL)
		viz.mouse.setVisible(False)
		self.name = 'test'
		
		self._theme					= viz.Theme()
		self._theme.borderColor		= (0.1,0.1,0.1,1)
		self._theme.backColor		= (0.4,0.4,0.4,1)
		self._theme.lightBackColor	= (0.6,0.6,0.6,1)
		self._theme.darkBackColor	= (0.2,0.2,0.2,1)
		self._theme.highBackColor	= (0.2,0.2,0.2,1)
		self._theme.textColor		= (1,1,1,1)
		self._theme.highTextColor	= (1,1,1,1)
		
		# Initialize test panel
		vizdlg.Panel.__init__(self, parent = self.canvas, theme = self._theme, align = viz.ALIGN_CENTER, fontSize = 10)
		self.visible(viz.OFF)
		self.setScale(*[i*config.menuScale[self.name] for i in [1,1,1]])
		
		# Title
		title = vizdlg.TitleBar('INSTRUCTIONS')
		self.addItem(title, align = viz.ALIGN_CENTER_TOP)
		
		# Bones to be snapped. source snapped to target.
		self.sourceText = viz.addTextbox(parent = self.canvas)
		self.sourceText.setLength(1.5)
		self.targetText = viz.addTextbox(parent = self.canvas)
		self.targetText.setLength(1.5)
		
		# Instructions 
		self.Instruct1		= self.addItem(viz.addText('Snap the: ', parent = self.canvas), align = viz.ALIGN_CENTER_TOP)
		self.sourceCommand	= self.addItem(self.sourceText, align = viz.ALIGN_CENTER_TOP)
		self.Instruct2		= self.addItem(viz.addText('To the: ', parent = self.canvas), align = viz.ALIGN_CENTER_TOP)
		self.targetCommand	= self.addItem(self.targetText, align = viz.ALIGN_CENTER_TOP)
		
		# Render canvas
		bb = self.getBoundingBox()
		self.canvas.setRenderWorld([bb.height, bb.width],[4, 3*1.333])
		
		# On esc toggle menu (doesn't interfere with in-game menu)
#		vizact.onkeydown(viz.KEY_ESCAPE, self.toggle)
		self.canvas.setPosition(0.0,2.0,4.0)
		self.canvas.resolution(self.canvas.getResolution())
#		self.canvas.billboard(viz.BILLBOARD_VIEW_POS)
#		self.canvas.setBackdrop(viz.ALIGN_LEFT_TOP)
#		self.canvas.alignment(viz.ALIGN_LEFT_CENTER)

#		if config.dispMode == config.DisplayMode.oculus:
#			self.oculusPanelPos = self.canvas.getPosition()
#			self.oculusPanelPos[0] = 1
#			self.canvas.setPosition(self.oculusPanelPos)
#		
#		vizact.onbuttondown(viz.KEY_ESCAPE, self.toggle)

		
	def setFields(self, source, target):
		"""Populate the text fields"""
		self.sourceText.message(source)
		self.targetText.message(target)
		
	def toggle(self):
		"""Toggle visibility"""
		self.visible(viz.TOGGLE)

class TestGrabPanel(vizdlg.Panel):
	"""blah"""
	def __init__(self):
		pass

class WireFrameCube(viz.VizNode):
	"""Draw a wireframe rectangle. Currently comes in green only."""
	def __init__(self, dimensions, center = [0,0,0], corner = False):
		edges = [[x,y,z] for x in [-1,0,1] for y in [-1,0,1] for z in [-1,0,1] if abs(x)+abs(y)+abs(z) == 2]
		for edge in edges:
			viz.startLayer(viz.LINES)
			viz.vertexColor(0,1,0)
			i = edge.index(0)
			edge[i] = 1
			viz.vertex(map(lambda a,b:a*b/2, edge, dimensions))
			edge[i] = -1
			viz.vertex(map(lambda a,b:a*b/2, edge, dimensions))
		self.cube = viz.endLayer()
		if corner:
			corner = [float(p[0])/2 + p[1] for p in zip(dimensions,center)]
			self.cube.setPosition(corner, viz.ABS_GLOBAL)
		else:
			self.cube.setPosition(center, viz.ABS_GLOBAL)
			
		super(WireFrameCube, self).__init__(self.cube.id)
			
class viewCube():
	"""
	the viewCube is an object that sits above the location
	where the skull is to be assembeled(the podium) and provides
	anatomical locational information (AP/ RL/ IS). There should
	also be a principle plane mode that shows midsagittal, frontal
	and transverse. the player should be able to toggle between these
	modes with a putton press.The parent of the viewcube is the podium
	"""
	def __init__(self):
		"""sets up viewcube and principle planes"""
		#Should appear ontop of podium
		
		self.modeCounter = 0 #Will be used to determine mode
		SF = 1 #Scale box
		
		#------------(AP/RL/SI) + cube mode setup-------------
		
		#add text objects set positions
		self.anterior = viz.addText('Anterior',pos = [0 ,SF*.5 ,SF*.5])
		self.posterior = viz.addText('Posterior',pos = [0, SF*.5 ,SF*-.5])
		self.left = viz.addText('Left', pos = [SF*-.5 ,SF*.5 ,0])
		self.right = viz.addText('Right', pos = [SF*.5 ,SF*.5 ,0])
		self.superior = viz.addText('Superior', pos = [0 ,SF*1.0 ,0])
		self.inferior = viz.addText('Inferior', pos = [0 ,SF*.01 ,0])
		
		#set orientation
		self.anterior.setEuler([180,0,0])
		self.posterior.setEuler([0,0,0])
		self.left.setEuler([90,0,0])
		self.right.setEuler([-90,0,0])
		self.superior.setEuler([0,90,0])
		self.inferior.setEuler([0,90,0])
		
		#set scale
		self.anterior.setScale([.1,.1,.1])
		self.posterior.setScale([.1,.1,.1])
		self.left.setScale([.1,.1,.1])
		self.right.setScale([.1,.1,.1])
		self.superior.setScale([.1,.1,.1])
		self.inferior.setScale([.1,.1,.1])
		
		#set each text object to be centered
		self.anterior.alignment(viz.ALIGN_CENTER_CENTER)
		self.posterior.alignment(viz.ALIGN_CENTER_CENTER)
		self.left.alignment(viz.ALIGN_CENTER_CENTER)
		self.right.alignment(viz.ALIGN_CENTER_CENTER)
		self.superior.alignment(viz.ALIGN_CENTER_CENTER)
		self.inferior.alignment(viz.ALIGN_CENTER_CENTER)
	
		#turn off rendering
		self.anterior.disable([viz.RENDERING])
		self.posterior.disable([viz.RENDERING])
		self.left.disable([viz.RENDERING])
		self.right.disable([viz.RENDERING])
		self.superior.disable([viz.RENDERING])
		self.inferior.disable([viz.RENDERING])

		#consider changing size, font, shading etc.
		
		#add cube
		RADIUS = .5 *SF
		self.cube = WireFrameCube([RADIUS*2, RADIUS*2, RADIUS*2])
		self.cube.setPosition([0,RADIUS, 0] , viz.ABS_PARENT)
		
		#turn off visability
		self.cube.visible(viz.OFF) 
		
		#---------------principle plane setup------------------------
		self.frontalPlane    = vizshape.addPlane(size = [1*SF ,1*SF] , axis = vizshape.AXIS_Z ,cullFace = False)
		self.transversePlane = vizshape.addPlane(size = [1*SF ,1*SF] , axis = vizshape.AXIS_Y ,cullFace = False)
		self.sagittalPlane   = vizshape.addPlane(size = [1*SF ,1*SF] , axis = vizshape.AXIS_X , cullFace = False)
		
		#setPosition(up in y so that origin is at bottom)
		self.frontalPlane.setPosition([0,SF*.5,0])
		self.transversePlane.setPosition([0,SF*.5,0])
		self.sagittalPlane.setPosition([0,SF*.5,0])
	
		#set alpha
		self.frontalPlane.alpha(.5)
		self.transversePlane.alpha(.5)
		self.sagittalPlane.alpha(.5)
		
		#set color
		self.frontalPlane.color([1,1,.5])
		self.transversePlane.color([1,1,.5])
		self.sagittalPlane.color([1,1,.5])
		
		#add text labels to upper corners of planes
		self.frontalLabel	= viz.addText('Frontal Plane',pos = [.5*SF ,SF*.5 , .01*SF]) #.01 prevents overlap with plane
		self.transverseLabel = viz.addText('Transverse Plane',pos = [-.5*SF , .01*SF ,SF*.5]) 
		self.sagittalLabel 	= viz.addText('Sagittal Plane',pos = [.01*SF ,SF*.5 ,SF*-.5])
		
		#scale text labels
		self.frontalLabel.setScale([.1,.1,.1])
		self.transverseLabel.setScale([.1,.1,.1])
		self.sagittalLabel.setScale([.1,.1,.1])
		
		#set planes to be parents of labels
		self.frontalLabel.setParent(self.frontalPlane)
		self.transverseLabel.setParent(self.transversePlane)
		self.sagittalLabel.setParent(self.sagittalPlane)

		#orient text labels
		self.frontalLabel.setEuler([180,0,0])
		self.transverseLabel.setEuler([0,90,0])
		self.sagittalLabel.setEuler([-90,0,0])
		
		#set alignment of Text labels
		self.frontalLabel.alignment(viz.ALIGN_LEFT_TOP)
		self.transverseLabel.alignment(viz.ALIGN_LEFT_TOP)
		self.sagittalLabel.alignment(viz.ALIGN_LEFT_TOP)
		
		#disable rendering on planes
		self.frontalPlane.disable([viz.RENDERING])
		self.transversePlane.disable([viz.RENDERING])
		self.sagittalPlane.disable([viz.RENDERING])
		
		#disable rendering of Text labels
		self.frontalLabel.disable([viz.RENDERING])
		self.transverseLabel.disable([viz.RENDERING])
		self.sagittalLabel.disable([viz.RENDERING])

	def toggleModes(self):
		"""
		This function will switch viewcube between its 3 modes:
		- off
		- (AP/RL/SI) + cube mode
		- principle plane mode
		"""
	
		#logic so that each function gets called every 3rd time
		self.modeCounter += 1
		
		if self.modeCounter % 4 == 1:
			#(AP/RL/SI) + cube mode
	
			#enable rendering on labels
			self.anterior.enable([viz.RENDERING])
			self.posterior.enable([viz.RENDERING])
			self.left.enable([viz.RENDERING])
			self.right.enable([viz.RENDERING])
			self.superior.enable([viz.RENDERING])
			self.inferior.enable([viz.RENDERING])
			
			#enable rendering on cube
			self.cube.visible(viz.ON)
			
		elif self.modeCounter % 4 == 2:
			# principle plane mode
			
			#disable rendering of labels
			self.anterior.disable([viz.RENDERING])
			self.posterior.disable([viz.RENDERING])
			self.left.disable([viz.RENDERING])
			self.right.disable([viz.RENDERING])
			self.superior.disable([viz.RENDERING])
			self.inferior.disable([viz.RENDERING])
			
			#disable rendering of cube
			self.cube.visible(viz.OFF)
			
			#enable rendering of principle planes
			self.frontalPlane.enable([viz.RENDERING])
			self.transversePlane.enable([viz.RENDERING])
			self.sagittalPlane.enable([viz.RENDERING])
			
			#enable rendering of plane labels
			self.frontalLabel.enable([viz.RENDERING])
			self.transverseLabel.enable([viz.RENDERING])
			self.sagittalLabel.enable([viz.RENDERING])
		
		elif self. modeCounter % 4 == 3:
			#both on
			
			#planes previously enabled
			
			#enable rendering of(AP/RL/SI) + cube mode
			#enable rendering on labels
			self.anterior.enable([viz.RENDERING])
			self.posterior.enable([viz.RENDERING])
			self.left.enable([viz.RENDERING])
			self.right.enable([viz.RENDERING])
			self.superior.enable([viz.RENDERING])
			self.inferior.enable([viz.RENDERING])
			
			#enable rendering on cube
			self.cube.visible(viz.ON)
			
		elif self.modeCounter % 4 == 0:
			#all off
			
			#disable rendering of(AP/RL/SI) + cube mode
			#disable rendering of labels
			self.anterior.disable([viz.RENDERING])
			self.posterior.disable([viz.RENDERING])
			self.left.disable([viz.RENDERING])
			self.right.disable([viz.RENDERING])
			self.superior.disable([viz.RENDERING])
			self.inferior.disable([viz.RENDERING])
			
			#disable rendering of cube
			self.cube.visible(viz.OFF)
			
			#rendering of planes
			#disable rendering of principle planes
			self.frontalPlane.disable([viz.RENDERING])
			self.transversePlane.disable([viz.RENDERING])
			self.sagittalPlane.disable([viz.RENDERING])
			
			#disable rendering of plane labels
			self.frontalLabel.disable([viz.RENDERING])
			self.transverseLabel.disable([viz.RENDERING])
			self.sagittalLabel.disable([viz.RENDERING])