"""
config.py

Just a bunch of constants defining running configuration
"""

## Display mode options:
# 0 - Regular computer
# 1 - 3D TV
# 2 - Oculus rift
dispMode = 0                                                                            

## Camera control mode options:
# 0 - arrow button  keyboard control
# 1 - SpaceMouse control
# 2 - Wiimote control
camMode = 0

## Pointer control mode options:
# 0 - X/Y/Z jog (tb/fh/vy)  keyboard control
# 1 - SpaceMouse control
# 2 - Mouse plane selection?
pointerMode = 1

## Dataset selection
# This list specifies what datasets will be made available
# for use in the menu
datasetNames = ['aorta', 'skull', 'pelvis']


DATASET_PATH = '.\\dataset\\full\\'