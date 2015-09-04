"""This example demonstrates the use of the vizinfo module"""
import viz
import vizinfo
import vizinput
import vizact

def changeMessage():
	info.setText( vizinput.input('Enter info text:') ) #Change directions message

#vizact.onkeydown('m', changeMessage)

def changeTitle():
	info.title( vizinput.input('Enter title text:') ) #Change title message

#vizact.onkeydown('t', changeTitle)


def SetSpinSpeed(pos, objToSpin):
	#Make wheelbarrow spin according to slider position
	objToSpin.runAction( vizact.spin(0, -1, 0, 500 * pos) )

#vizact.onslider( slider, SetSpinSpeed )

#viz.setMultiSample(4)
#viz.fov(60)
#viz.go()

def playGame():
	vizinfo.InfoPanel(align=viz.ALIGN_RIGHT_BOTTOM)

	viz.clearcolor(viz.SLATE)

	#Add object that vizinfo GUI objects will modify
	wheelbarrow = viz.addChild('wheelbarrow.ive')
	wheelbarrow.setPosition([0,1,2])
	wheelbarrow.setAxisAngle([0,1,0, -90])

	#Initialize info box with some instructions
	info = vizinfo.InfoPanel('Use the slider to spin the wheelbarrow.\nThe radio button changes the color.', align=viz.ALIGN_RIGHT_TOP, icon=False)
	info.setTitle( 'Wheelbarrow Spinner' ) #Set title text
	info.addSeparator()

	#Add slider in info box
	slider = info.addLabelItem('Spin Speed', viz.addSlider())
	slider.label.color(viz.RED)

	#Add radio buttons
	red = info.addLabelItem('Red', viz.addRadioButton('color'))
	white = info.addLabelItem('White', viz.addRadioButton('color'))
	blue = info.addLabelItem('Blue', viz.addRadioButton('color'))

	#Set callbacks for changing wheelbarrow color with radio buttons
	vizact.onbuttondown( red, wheelbarrow.color, viz.RED )
	vizact.onbuttondown( white, wheelbarrow.color, viz.WHITE )
	vizact.onbuttondown( blue, wheelbarrow.color, viz.BLUE )

	#Keyboard commands that modify the info box
	vizact.onkeydown(' ', info.setPanelVisible, viz.TOGGLE)
	vizact.onkeydown('m', changeMessage)
	vizact.onkeydown('t', changeTitle)
	vizact.onslider( slider, SetSpinSpeed , wheelbarrow)


