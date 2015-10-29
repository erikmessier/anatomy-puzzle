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

# Custom modules
import config
import anatomyTrainer

#import overHeadMenu

def main():
	
	#Prompt for init config parameters
	configurations = config.modalityGUI()
	
	#Initialize puzzle game
	anatomyTrainer.start()

if __name__ == '__main__':
	main()
	