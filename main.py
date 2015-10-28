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
import time
import Tkinter
import json

# Custom modules
import init
import menu	
import puzzle
import config

#import overHeadMenu

def main():
	### Configuration parameters
	#user input configurations GUI
	configParam = config.modalityGUI()
	proceedFromConfigGUI = True
	#opening file where user selections were stored
	with open('.\\dataset\\configurations\\configurations.json','rb') as f:
		configurations = json.load(f)
		config.dispMode = int(configurations['dispMode'])
		config.pointerMode = int(configurations['pointerMode'])
		proceedFromConfigGUI = configurations['proceed']
		f.close()
	if proceedFromConfigGUI:
		### Game startup
		#overwrite escape key
		viz.setOption('viz.default_key.quit','0')
		
		# Physics
		viz.phys.enable()
		#viz.phys.setGravity(0,0,0)

		# Initialize pointer tool
		# Unused?
		glove = viz.addChild('.\\dataset\\Hand\\handPoint_reduced.ply')
		glove.disable([viz.PHYSICS, viz.DYNAMICS])

		glovePhys = glove.collideSphere()
		glove.setPosition([0,1,0])
		glove.setScale([1,1,1])

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
		puzzle.model.pointer = glove
		puzzle.model.pointer.setScale(0.012, 0.012, 0.012)
		puzzle.model.pointer.setEuler(0, -115, 0)
		
		# Override default escape key map to call main menu
		vizact.onkeydown(viz.KEY_ESCAPE, menu.toggle)
		
	#	# Record moviefilms
	#	viz.setOption('viz.AVIRecorder.maxWidth', '1280')
	#	viz.setOption('viz.AVIRecorder.maxHeight', '720')
	#	vizact.onkeydown(viz.KEY_F11, viz.window.startRecording, 'D:\\recording.avi')
	#	vizact.onkeydown(viz.KEY_F12, viz.window.stopRecording)
		
		# Stuff to run on program termination
		vizact.onexit(puzzle.controller.end)
	

if __name__ == '__main__':
	main()