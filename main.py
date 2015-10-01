"""
########################################
#      STEREOSCOPIC ANATOMY GAME
########################################
# A Senior design project
#
# Authors:
# Alex Dawson-Elli, Kenny Lamarka, Kevin Alexandre, Jascha Wilcox , Nate Burell
#
# 2014-2015 Academic year
"""

# System modules
import viz
import vizact

# Custom modules
import init
import menu	
import puzzle
import config

#import overHeadMenu


def main():
	### Configuration parameters
	# moved to config.py

	### Game startup
	#overwrite escape key
	viz.setOption('viz.default_key.quit','0')
	
	# Physics
	viz.phys.enable()
	#viz.phys.setGravity(0,0,0)

	# Initialize pointer tool
	# Unused?
	glove = viz.addChild('glove.cfg')
	glove.disable([viz.PHYSICS, viz.DYNAMICS])

	glovePhys = glove.collideSphere()
	glove.setPosition([0,1,0])
	glove.setScale([2,2,2])

	# Initialize environment this will load the coliseum and sky
	sky = viz.addChild('sky_day.osgb')
	sky.collideMesh()
	sky.disable(viz.DYNAMICS)
	init.loadTemple()

	# Initialize pointer controls
	device = init.pointerInput(config.pointerMode, glove, sky)

	# Initialize display
	puzzle.model.display = init.DisplayInstance(config.dispMode,config.camMode,device,glove)
	#init.display(config.dispMode)

	# Initialize camera controls
	#init.cameraInput(config.camMode,config.dispMode, device, glove)

	# Launch menu system
	menu.init()
	puzzle.controller.setPointer(glove)
	puzzle.controller.init()
	puzzle.controller.setDisplay(puzzle.model.display)
	
	# Escape Key calls main menu
	vizact.onkeydown(viz.KEY_ESCAPE, menu.toggle)

	# Stuff to run on program termination
	vizact.onexit(puzzle.controller.end)

	# Will move this out of main and where it belongs
	viewcube = puzzle.controller.viewCube()
	vizact.onkeydown('65460', viewcube.toggleModes) # '4' key
	

if __name__ == '__main__':
	main()