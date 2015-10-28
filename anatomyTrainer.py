import model

def start():
	"""
	Run everything necessary for game startup
	"""
	
	# Override escape key to toggle menu
	viz.setOption('viz.default_key.quit','0')
	vizact.onkeydown(viz.KEY_ESCAPE, menu.toggle)
	
	# Physics
	viz.phys.enable()

	# Initialize pointer tool
	# Unused?
	model.pointer = viz.addChild('.\\dataset\\Hand\\handPoint_reduced.ply')
	pointer = model.pointer
	
	pointer.setScale(0.012, 0.012, 0.012)
	pointer.setEuler(0, -115, 0)
	pointer.disable([viz.PHYSICS, viz.DYNAMICS])


	# Initialize environment this will load the coliseum and sky
	sky = viz.addChild('sky_day.osgb')
	sky.collideMesh()
	sky.disable(viz.DYNAMICS)
	init.loadTemple()

	# Initialize pointer controls
	device = init.pointerInput(config.pointerMode, pointer, sky)

	# Initialize display
	puzzle.model.display = init.DisplayInstance(config.dispMode,config.camMode,device,pointer)
	
	# Launch menu system
	menu.init()
	
#	# Record moviefilms
#	viz.setOption('viz.AVIRecorder.maxWidth', '1280')
#	viz.setOption('viz.AVIRecorder.maxHeight', '720')
#	vizact.onkeydown(viz.KEY_F11, viz.window.startRecording, 'D:\\recording.avi')
#	vizact.onkeydown(viz.KEY_F12, viz.window.stopRecording)
	
	# Stuff to run on program termination
	vizact.onexit(puzzle.controller.end)
	
def startGame(game):
	if model.gameController:
		return
	model.gameController = config.controllers.game()

def restartGame():
	if not model.gameController:
		return
#	model.gameController.end()
#	model.gameController.start()

def endGame():
	game = model.gameController
	if not game:
		return
	game.end()
	game = None

