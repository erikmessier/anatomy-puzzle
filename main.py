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

# Built-In 
import json

# Custom modules
import config
import anatomyTrainer

#import overHeadMenu

def main():
	
	#Prompt for init config parameters
	configurations = config.modalityGUI()
	
	#Handling configuration selections
	with open('.\\dataset\\configurations\\configurations.json','rb') as f:
		configurations = json.load(f)
		config.dispMode = int(configurations['dispMode'])
		config.pointerMode = int(configurations['pointerMode'])
		proceedFromConfigGUI = configurations['proceed']
		f.close()
	if proceedFromConfigGUI:
	
		#Initialize puzzle game
		anatomyTrainer.start()

if __name__ == '__main__':
	main()
	
	
	
	