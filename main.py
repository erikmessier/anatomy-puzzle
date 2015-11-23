

"""
STEREOSCOPIC ANATOMY GAME

Originally started as a senior design project for the 2014-2015 academic year.
Senior design team members:
 Alex Dawson-Elli, Kenny Lamarka, Kevin Alexandre, Jascha Wilcox , Nate Burell

Development was continued in fall 2015 by:
 Jascha Wilcox, Erik Messier
"""

# Built-In 
import json

# Custom modules
import config
import anatomyTrainer
import menu
                 
def main():
	try:
		#Prompt for init config parameters
		configurations = menu.modalityGUI()
		
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
	except:
		raise
		
		

if __name__ == '__main__':
	main()
	
	