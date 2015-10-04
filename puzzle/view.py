import viz
viz.go()
viz.clearcolor(viz.GRAY)
viz.addChild('piazza.osgb')
import vizdlg

class TestSnapPanel(vizdlg.Panel):
	def __init__(self):
		#init canvas and create themes for the test panel
		self.canvas = viz.addGUICanvas()
		self.canvas.setPosition(3.8,2.3,0)
		viz.mouse.setVisible(False)
		self._theme = viz.Theme()
		self._theme.borderColor = (0.1,0.1,0.1,1)
		self._theme.backColor = (0.4,0.4,0.4,1)
		self._theme.lightBackColor = (0.6,0.6,0.6,1)
		self._theme.darkBackColor = (0.2,0.2,0.2,1)
		self._theme.highBackColor = (0.2,0.2,0.2,1)
		self._theme.textColor = (1,1,1,1)
		self._theme.highTextColor = (1,1,1,1)
		
		#initialize test panel
		vizdlg.Panel.__init__(self, parent = self.canvas, theme = self._theme, align = viz.ALIGN_RIGHT_TOP, fontSize = 10)
		self.visible(viz.OFF)
		#title
		title = vizdlg.TitleBar('INSTRUCTIONS')
		self.addItem(title, align = viz.ALIGN_CENTER_TOP)
		
		#bones to be snapped. source snapped to target.
		source = ''
		self.sourceText = viz.addTextbox()
		target = ''
		self.targetText = viz.addTextbox()
		
		#instructions 
		self.Instruct1 = self.addItem(viz.addText('Snap the: '), align = viz.ALIGN_CENTER_TOP)
		self.sourceCommand = self.addItem(self.sourceText, align = viz.ALIGN_CENTER_TOP)
		self.Instruct2 = self.addItem(viz.addText('To the: '), align = viz.ALIGN_CENTER_TOP)
		self.targetCommand = self.addItem(self.targetText, align = viz.ALIGN_CENTER_TOP)
		
		#render canvas
		bb = self.getBoundingBox()
		self.canvas.setRenderWorldOverlay([bb.height, bb.width], fov = bb.height*.1, distance = 5)
		
	def setFields(self, source, target):
		self.sourceText.message(source)
		self.targetText.message(target)
	def toggleTestPanel(self):
		self.visible(viz.TOGGLE)
class TestGrabPanel(vizdlg.Panel):
	def __init__(self):
		pass
		

