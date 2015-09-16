import viz
import vizdlg

viz.go()

p1 = vizdlg.TickerDialog(label='Circle',units='pixels',range=(1,5,1),editable=True,border=False,background=False,margin=0)
p2 = vizdlg.TickerDialog(label='Crosshair',units='pixels',range=(1,5,1),editable=True,border=False,background=False,margin=0)
p3 = vizdlg.TickerDialog(label='Border',units='pixels',range=(1,5,1),editable=True,border=False,background=False,margin=0)

tp = vizdlg.TabPanel(align=vizdlg.ALIGN_RIGHT_TOP)
tp.addPanel('Circle',p1,align=vizdlg.ALIGN_LEFT_TOP)
tp.addPanel('Crosshair',p2,align=vizdlg.ALIGN_CENTER_TOP)
tp.addPanel('Border.',p3,align=vizdlg.ALIGN_RIGHT_TOP)
tp.addPanel('checkbox',viz.addCheckbox(),align=vizdlg.ALIGN_LEFT_BOTTOM)
tp.addPanel('slider',viz.addSlider(),align=vizdlg.ALIGN_CENTER_BOTTOM)
tp.addPanel('movie',viz.addTexQuad(size=75,texture=viz.add('vizard.mpg',loop=True,play=True)),align=vizdlg.ALIGN_RIGHT_BOTTOM)

viz.link(viz.RightTop,tp,offset=(-20,-20,0))