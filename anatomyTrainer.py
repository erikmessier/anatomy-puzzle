"""
Primary file from which the Anatomy Trainer game is run.
"""

# Vizard modules
import viz
import vizact, vizshape, viztask

# Custom modules
import model
import menu
import init
import config

def start():
	"""
	Run everything necessary for game startup
	"""
	# Physics
	viz.phys.enable()

	### Initialize pointer tool
	model.pointer = viz.addChild('.\\dataset\\Hand\\handPoint_reduced.ply')
	pointer = model.pointer
	
	pointer.setScale(0.012, 0.012, 0.012)
	pointer.setEuler(0, -115, 0)
	pointer.disable([viz.PHYSICS, viz.DYNAMICS])
	
	### Alpha slice plane setup
	viz.startLayer(viz.POINTS)
	viz.vertex(0,0,0)
	planeVert = viz.endLayer(parent = pointer)
	planeVert.dynamic()
	
	# Setup normal vector for alpha slicing plane calculation
	planeVert.setNormal(0,[0,1,0])
	model.planeVert = planeVert
	slicePlane = vizshape.addPlane(size = [20, 20, 20], parent = pointer, cullFace = False)
	slicePlane.alpha(0.20)
	slicePlane.color(viz.ORANGE)
	
	### Initialize environment this will load the coliseum and sky
	sky = viz.addChild('gallery.osgb')
	sky.setPosition([0, 0, -5])
	sky.collideMesh()
	sky.disable(viz.DYNAMICS)
	init.loadTemple()

	# Lighting
	lights = []
	[lights.append(viz.addLight()) for _ in range(2)]
	lights[0].setEuler(90, 40, 0)
	lights[0].intensity(0.5)
	lights[1].setEuler(270, 40, 0)
	lights[1].intensity(0.3)
	
	# Initialize pointer controls
	device = init.pointerInput(config.pointerMode, pointer, sky)

	### Initialize display
	model.display = init.DisplayInstance(config.dispMode,config.camMode,device,pointer)
	
	### Launch menu system
	model.menu = menu.MenuController()
	
	### Override escape key to toggle menu
	viz.setOption('viz.default_key.quit','0')
	
#	# Record moviefilms
#	viz.setOption('viz.AVIRecorder.maxWidth', '1280')
#	viz.setOption('viz.AVIRecorder.maxHeight', '720')
#	vizact.onkeydown(viz.KEY_F11, viz.window.startRecording, 'D:\\recording.avi')
#	vizact.onkeydown(viz.KEY_F12, viz.window.stopRecording)
	
	# Stuff to run on program termination
	vizact.onexit(endGame)
	
def startGame(game, dataset):
	if model.gameController:
		return
	model.gameController = game(dataset)

def restartGame(game, dataset):
	if not model.gameController:
		return
	model.gameController.end()
	model.gameController = None
	startGame(game, dataset)

def endGame():
	if not model.gameController:
		return
	model.gameController.end()
	model.gameController = None
	print model.gameController

