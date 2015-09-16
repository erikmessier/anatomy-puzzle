"""
config.py

Just a bunch of constants defining running configuration
"""

# Display mode options:
#  0 - Regular computer
#  1 - 3D TV
#  2 - Oculus rift
dispMode = 0                                                                            

# Camera control mode options:
#  0 - arrow button  keyboard control
#  1 - SpaceMouse control
#  2 - Wiimote control
camMode = 0

# Pointer control mode options:
#  0 - X/Y/Z jog (tb/fh/vy)  keyboard control
#  1 - SpaceMouse control
#  2 - Mouse plane selection?
pointerMode = 0
layers = {'Axial':['Skull', 'Thorax'], 'Upper Appen.': ['Right Arm', 'Left Arm', 'Right Shoulder', 'Left Shoulder'], 'Lower Appen.': ['Right Leg', 'Left Leg', 'Pelvic Girdle']}