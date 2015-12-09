﻿"""
Controller components of the Puzzle game
"""

# Vizard modules
import viz
import vizact, viztask, vizproximity
import vizmat
import vizshape

# Python built-in modules
import random
import math, numpy
import json, csv
import time, datetime
import threading

# Custom modules
import init
import menu
import config
import model
import puzzleView
import bp3d

class PuzzleController(object):
	"""
	Puzzle game controller base class. Not intended to be used directly, derive
	children that feature the game mode functionality you want.
	"""
	def __init__(self, dataset):
		self.modeName = ''
		
		self._maxThreads = 8
		self._curThreads = 0
		
		self._meshes			= []
		self._meshesByFilename	= {}
		self._keystones			= []
		self._proximityList		= []
		self._boundingBoxes		= {}
		self._keyBindings		= []
		self._inRange			= []
		
		self._meshesById	= {}
		
		self._boneInfo			= None
		self._closestBoneIdx 	= None
		self._prevBoneIdx		= None
		self._lastGrabbed 		= None
		self._lastMeshGrabbed	= None
		self._lastBoxGrabbed	= None
		self._highlighted		= None
		self._gloveLink			= None

		self._grabFlag		= False
		self._snapAttempts	= 0
		self._imploded		= False
		
		self._pointerTexture	= model.pointer.getTexture()
		self._pointerOrigColor	= model.pointer.getColor()

#		self.viewcube = puzzleView.viewCube()
		
		viztask.schedule(self.load(dataset))
		
#		viztask.schedule(self.updateClosestBone())
		
	def load(self, dataset):
		"""
		Load datasets and initialize everything necessary to commence
		the puzzle game.
		"""
		
		# Dataset
		model.ds = bp3d.DatasetInterface()

		# Proximity management
		model.proxManager = vizproximity.Manager()
		target = vizproximity.Target(model.pointer)
		model.proxManager.addTarget(target)

		model.proxManager.onEnter(None, self.EnterProximity)
		model.proxManager.onExit(None, self.ExitProximity)

		#Setup Key Bindings
		self.bindKeys()

		self.score = PuzzleScore(self.modeName)
		
#		viztask.schedule(soundTask(glove))

		self._meshesToLoad = model.ds.getOntologySet(dataset)
		self._filesToPreSnap = model.ds.getPreSnapSet()
		
		yield self.loadControl(self._meshesToLoad)
		yield self.prepareMeshes()
		yield self.preSnap()
		yield self.setKeystone(1)
		
		viztask.schedule(self.updateClosestBone())
		
	def loadControl(self, meshes = [], animate = False):
		"""Control loading of meshes --- used to control multithreading"""
		while True:
			yield self.loadMeshes(meshes)
			#Check to make sure that all requested meshes were loaded if they aren't then load the missing meshes
			lingeringThreads = 0
			while True:
				if lingeringThreads >= 20:
					self.printNoticeable('Error: Issue with loading, not everything was loaded, going to load the remaining meshes')
					needToLoad = list(set(self._meshesToLoad) - set(self._meshes))
					self.loadControl(needToLoad)
					break
				if len(self._meshes) < len(self._meshesToLoad)- self.unknownFiles:
					self.printNoticeable('notice: some threads are still running, please wait')
				else:
					model.menu.updateLoad(len(self._meshes), len(self._meshesToLoad))
					model.menu.finishedLoading()
					self.printNoticeable('notice: All Items Were Loaded!')
					break
				yield viztask.waitTime(0.2)
				lingeringThreads += 1
			break
			
	def loadMeshes(self, meshes = [], animate = False):
		"""Load all of the files from the dataset into puzzle.mesh instances"""
		self.unknownFiles = 0
		model.threads = 0
		self.printNoticeable('start of rendering process')
		for i, fileName in enumerate(meshes):
			# This is the actual mesh we will see
			if not model.ds.getMetaData(file = fileName):
				print "WARNING, UNKNOWN FILE ", fileName
				self.unknownFiles += 1
				continue
				
			#Wait to add thread if threadThrottle conditions are not met
			model.threads += 1 #Add 1 for each new thread added --- new render started
			yield viztask.waitTrue(self.threadThrottle, self._maxThreads)
			yield viz.director(self.renderMeshes, fileName)
			model.menu.updateLoad(len(self._meshes), len(self._meshesToLoad))
			
		self.printNoticeable('end of rendering process')
	
	def renderMeshes(self, fileName):
		"""Creates a mesh class instance of the mesh fileName"""
		m = bp3d.Mesh(fileName, SF = config.SF)
		
		self._meshes.append(m)
		self._meshesById[m.id] = m
		
		model.threads -= 1 #Subtract 1 for each thread that has finished rendering
		
	def threadThrottle(self, maxThreads, threadFlag = True):
		"""
		If the number of current threads (curThreads) is greater than the decided maximum, then 
		returns false --- and vice-versa
		"""
		while True:
			if model.threads <= maxThreads:
				return True
				
	def setKeystone(self, number):
		"""Set Keystones"""
		for bb in self._boundingBoxes.values():
			bb.setKeystones(number)
#		for m in [self._meshes[i] for i in range(number)]:
#			cp = m.centerPointScaled
#			m.setPosition(cp, viz.ABS_GLOBAL)
##			m.setEuler([0, 0, 0], viz.ABS_GLOBAL)
#			m.group.grounded = True
#			self._keystones.append(m)
#			
#		for m in self._keystones[1:]:
#			self._keystones[0].group.merge(m)
	
	def addToBoundingBox(self, meshes):
		"""
		Populate environment with bounding boxes allowing easy manipulation
		of subassemblies of the entire model. Currently partitioned by region.
		"""
		for m in meshes:
			if m.region not in self._boundingBoxes.keys():
				self._boundingBoxes[m.region] = BoundingBox([m])
			else:
				self._boundingBoxes[m.region].addMembers([m])
	
	def prepareMeshes(self):
		"""Places meshes in circle around keystone(s)"""
		for m in self._meshes:
			m.addSensor()
			m.addToolTip(self._boundingBoxes[m.region])
		
	def disperseRandom(self, nodes, animate = False):
		for m in nodes:
			angle	= random.random() * 2 * math.pi
			radius	= random.random() + 1.5
			
			targetPosition	= [math.sin(angle) * radius, math.cos(angle) * radius, -1.0]
			targetEuler		= m.getEuler()
#			targetEuler		= [0.0,90.0,180.0]
			#targetEuler	= [(random.random()-0.5)*40,(random.random()-0.5)*40 + 90.0, (random.random()-0.5)*40 + 180.0]
			
			if (animate):
				move = vizact.moveTo(targetPosition, time = 2)
				spin = vizact.spinTo(euler = targetEuler, time = 2)
				transition = vizact.parallel(spin, move)
				m.addAction(transition)
			else:					
				m.setPosition(targetPosition)
				m.setEuler(targetEuler)
				
			if isinstance(m, BoundingBox):
				m.disperseMembers()

	def preSnap(self, percentCut = 0.1, distance = 0.1):
		"""Snaps meshes that are pre-determined in config or are a certain degree smaller than the average volume"""

		self._smallMeshes = []
		self._meshesToPreSnap = []
		average = 27
		
		#Create dictionary associating filename with mesh
		self._meshesByFilename = self.getMeshesByFilename(self._meshes)
		
		#Convert self._meshesToPreSnap from filenames to meshes
		for fileList in self._filesToPreSnap:
			meshList = self.convertListOfFiles(fileList)
			if meshList:
				self._meshesToPreSnap.append(meshList)
		
		#snap together items that are stated in config
		if self._meshesToPreSnap:
			for snapList in self._meshesToPreSnap:
				if set.intersection(set(snapList), set(self._meshes)):
					for m in snapList[1:]:
						try:
							self.snap(snapList[0], m, children = True, animate = False)
						except KeyError:
							continue
		
		for m in self._meshes:
			if m.metaData['volume'] < average * percentCut:
				self._smallMeshes.append(m)
		
		if self._meshesToPreSnap:
			for meshList in self._meshesToPreSnap:
				self._smallMeshes = list(set(self._smallMeshes) - set(meshList))
		
#		keystoneMeshes = set(self._keystones)
#		self._smallMeshes = list(meshesToPreSnap - keystoneMeshes)

		for m1 in self._smallMeshes:
			snapToM1 = self.getAdjacent(m1, self._smallMeshes, maxDist = distance)
			for m2 in snapToM1:
				self.snap(m1, m2, children = True, animate = False)
				

	def printNoticeable(self, text):
		"""Highly visible printouts"""
		print '-'*len(text)
		print text.upper()
		print '-'*len(text)
	
	def convertListOfFiles(self, fileNames):
		'''Converts a list of filenames to a list of meshes'''
		listOfMeshes = []
		
		for fileName in fileNames:
			try:
				listOfMeshes.append(self._meshesByFilename[fileName])
			except KeyError:
				continue
			
		return listOfMeshes
		
	def getMeshesByFilename(self, meshes):
		'''Creates a dictionary that associates obj filename with the mesh'''
		meshesByFilename = {}
		for m in meshes:
			meshesByFilename[m.metaData['filename']] = m
		return meshesByFilename
		
	def unloadMeshes(self):
		"""Unload all of the bone objects to reset the puzzle game"""
		for m in self._meshes:
			m.remove(children = True)
		for b in self._boundingBoxes.values():
			b.remove(children = True)
		
	def transparency(self, source, level, includeSource = False):
		"""Set the transparency of all the bones"""
		meshes = self._meshes
		if includeSource:
			for b in meshes:
				b.setAlpha(level)
		else:
			for b in [b for b in meshes if b != source]:
				b.setAlpha(level)			

	def moveCheckers(self, sourceChild):
		"""
		Move all of the checker objects on each bone into position, in order to
		see if they should be snapped.
		"""
		source = self._meshesById[sourceChild.id] # Just in case we pass in a node3D
		
		for bone in [b for b in self._meshes if b != source]:
			bone.checker.setPosition(source.centerPoint, viz.ABS_PARENT)

	def getAdjacent(self, mesh, pool, maxDist = None):
		"""Sort pool by distance from mesh"""
		self.moveCheckers(mesh)
		neighbors = []
		
		for m in pool:
			centerPos = m.getPosition(viz.ABS_GLOBAL)
			checkerPos = m.checker.getPosition(viz.ABS_GLOBAL)
			dist = vizmat.Distance(centerPos, checkerPos)	
			neighbors.append([m,dist])
		
		neighbors = sorted(neighbors, key = lambda a: a[1])

		if maxDist:
			neighbors = [m for m in neighbors if m[1] < maxDist]
		
		return [l[0] for l in neighbors]
		
	def snapCheck(self):
		"""
		Snap checks for any nearby bones, and mates a src bone to a dst bone
		if they are in fact correctly placed.
		"""
		for bb in self._boundingBoxes.values():
			if bb.getAction():
				return
			for m in bb._members:
				if m.getAction():
					return
		
		snapped = False
		
		if not self.getSnapSource():
			print 'nothing to snap'
			return

		
		if isinstance(self.getSnapSource(), bp3d.Mesh):
			SNAP_THRESHOLD		= 0.2; #how far apart the mesh you are snapping is from where it should be
			DISTANCE_THRESHOLD	= 0.75; #distance source mesh is from other meshes
			ANGLE_THRESHOLD		= 45.0; #min euler difference source mesh can be from target mesh
			sourceMesh		= self.getSnapSource()
			searchMeshes	= self.getSnapSearch(source = sourceMesh)
			targetMesh		= self.keyTarget
			
			self.moveCheckers(sourceMesh)
				
			# Search through all of the checkers, and snap to the first one meeting our snap
			# criteria
			
			if sourceMesh.snapAttempts >= 3 and not sourceMesh.group.grounded:
				self.snap(sourceMesh, self.keyTarget, children = True)
				viz.playSound(".\\dataset\\snap.wav")
				print 'Three unsuccessful snap attempts, snapping now!'
				self.score.event(event = 'autosnap', description = 'Three unsuccessful snap attempts, snapping now!', \
					source = sourceMesh.name, destination = targetMesh.name)
#				self._snapAttempts = 0
				if self.modeName == 'testplay':
					self.pickSnapPair()
					
			elif sourceMesh.group.grounded:
				print 'That object is grounded. Returning!'
				
			else:
				for bone in [b for b in searchMeshes if b not in sourceMesh.group.members]:
					targetSnap = bone.checker.getPosition(viz.ABS_GLOBAL)
					targetPosition = bone.getPosition(viz.ABS_GLOBAL)
					targetQuat = bone.getQuat(viz.ABS_GLOBAL)
					
					currentPosition = sourceMesh.getPosition(viz.ABS_GLOBAL)
					currentQuat = sourceMesh.getQuat(viz.ABS_GLOBAL)		
					
					snapDistance = vizmat.Distance(targetSnap, currentPosition)
					proximityDistance = vizmat.Distance(targetPosition, currentPosition)
					angleDifference = vizmat.QuatDiff(bone.getQuat(viz.ABS_GLOBAL), sourceMesh.getQuat(viz.ABS_GLOBAL))
					
					if (snapDistance <= SNAP_THRESHOLD) and (proximityDistance <= DISTANCE_THRESHOLD) \
							and (abs(angleDifference) < ANGLE_THRESHOLD):
						print 'Snap! ', sourceMesh, ' to ', bone
						self.score.event(event = 'snap', description = 'Successful snap', source = sourceMesh.name, destination = bone.name)
						viz.playSound(".\\dataset\\snap.wav")
						self.snap(sourceMesh, bone, children = True)
						snapped = True
						if self.modeName == 'testplay':
							self.pickSnapPair()
						break
				if not snapped:
					print 'Did not meet snap criteria!'
					sourceMesh.snapAttempts += 1
					self.score.event(event = 'snapfail', description = 'did not meet snap criteria', source = sourceMesh.name)
				self.printNoticeable('snap attempts: ' + str(sourceMesh.snapAttempts))
						
			if len(self._lastBoxGrabbed._keystones) == len(self._lastBoxGrabbed._members):
				self.score.event(event = 'Finished Region', description = self._lastMeshGrabbed.region + ' was finished')
				self.printNoticeable('Finished Region!!')
				self._boundingBoxes[sourceMesh.region].finishedRegion = True
				
				# If all regions in a region group are finished than show all members
				self._lastBoxGrabbed.regionGroup.getFinished()
				if self._lastBoxGrabbed.regionGroup.allRegionsFinished:
					for bb in self._lastBoxGrabbed.regionGroup.members:
						bb.showMembers(True)
			if len(self._meshes) == len(sourceMesh.group.members):
				print "Assembly completed!"
				self.end()
				model.menu.endGame()
				
					
		elif isinstance(self.getSnapSource(), BoundingBox):
			SNAP_THRESHOLD		= 1.5; #how far apart the mesh you are snapping is from where it should be
			ANGLE_THRESHOLD		= 45.0; #min euler difference source mesh can be from target mesh
			
			#If lastGrabbed is a bounding box carry out this snap check procedure...
			sourceBB = self.getSnapSource()
			
			# Find closest bounding box
			targetBB, distance = sourceBB.findClosestBB(self._boundingBoxes.values())
			
			# Find Target Position and Euler for the Source BB
			tPos, tEuler = sourceBB.moveChecker(targetBB)
			
			# If the Source is close enough to the target position and euler then snap
			eulerDiff = vizmat.QuatDiff(targetBB.checker.getQuat(viz.ABS_GLOBAL), sourceBB.getQuat(viz.ABS_GLOBAL))
			if distance <= SNAP_THRESHOLD and abs(eulerDiff) <= ANGLE_THRESHOLD:
				sourceBB.snapToBB(targetBB)
			
			self._lastBoxGrabbed.regionGroup.getFinished()
			if self._lastBoxGrabbed.regionGroup.allRegionsFinished:
				for bb in self._lastBoxGrabbed.regionGroup.members:
						bb.showMembers(True)

	def snap(self, sourceMesh, targetMesh, children = False, animate = True):
		self.moveCheckers(sourceMesh)
		if children:
			sourceMesh.setGroupParent()
		if animate:
			sourceMesh.moveTo(targetMesh.checker.getMatrix(viz.ABS_GLOBAL))
		else:
			sourceMesh.setPosition(targetMesh.checker.getPosition(viz.ABS_GLOBAL))
			sourceMesh.setEuler(targetMesh.checker.getEuler(viz.ABS_GLOBAL))
		targetMesh.group.merge(sourceMesh)
		if targetMesh.group.grounded:
			for m in sourceMesh.group.members:
				self._boundingBoxes[sourceMesh.region]._keystones.append(m)
			self._boundingBoxes[sourceMesh.region]._keystones = list(set(self._boundingBoxes[sourceMesh.region]._keystones))
	
	def getSnapSource(self):
		"""Define source object for snapcheck"""
		return self._lastGrabbed
	
	def getSnapTarget(self, source, search = None):
		"""Define target object for snapcheck"""
		if search:
			return self.getAdjacent(self._lastGrabbed, search)[0]
		else:
			return self.getAdjacent(self._lastGrabbed, self.getEnabled())[0]
		
	def getSnapSearch(self, source = None):
		"""Define list of objects to search for snapcheck"""
#		return self.getEnabled()
#		return self._boundingBoxes[source.region]._members
		return self.getAdjacent(source, self._boundingBoxes[source.region]._members)
#		meshes = []
#		for i in meshesAndDist:
#			meshes.append(i[0])
#			
#		return meshes 
	
	def snapGroup(self, boneNames):
		"""Specify a list of bones that should be snapped together"""
		print boneNames
		if (len(boneNames) > 0):
			meshes = []
			[[meshes.append(self._meshesById[m]) for m in group] for group in boneNames]
			[m.snap(meshes[0], animate = False) for m in meshes[1:]]

	def grab(self):
		"""Grab in-range objects with the pointer"""
		if not self._lastBoxGrabbed:
			grabList = self._proximityList # Needed for disabling grab of grounded bones
			self._lastBoxGrabbed = self._boundingBoxes.values()[0]
		else:
			# if there is an active region, you cannot grab meshes on inactive regions
			meshGrabList = set.intersection(set(self._proximityList), set(self._lastBoxGrabbed._members))
			boxGrabList = set.intersection(set(self._proximityList), set(self._boundingBoxes.values()))
			grabList = list(set.union(meshGrabList, boxGrabList))
		
		if len(grabList) == 0 or self._grabFlag:
			return

		target = self.getClosestObject(model.pointer,grabList)
		
		if isinstance(target, bp3d.Mesh):
			if self._boundingBoxes.has_key(target.region):
				self.keyTarget = self._boundingBoxes[target.region]._keystones[0]
			else:
				# band-aid for test mode
				self.keyTarget = self._boundingBoxes['full']._keystones[0]
				
			if target.group.grounded:
				self.highlightGrabbedMesh(target, True)
				
			else:
				target.setGroupParent()
				self._gloveLink = viz.grab(model.pointer, target, viz.ABS_GLOBAL)
				self.score.event(event = 'grab', description = 'Grabbed bone', source = target.name)
#				self.transparency(target, 0.7)
				target.highlight(grabbed = True)
			if self._lastMeshGrabbed and self._lastMeshGrabbed is not target:
				if self._lastMeshGrabbed in grabList:
					self._lastMeshGrabbed.highlight(prox = True)
				else:
					self._lastMeshGrabbed.highlight(prox = False)
					
			self._lastMeshGrabbed = target
			
		elif isinstance(target, BoundingBox):
			target.grab()
			self._gloveLink = viz.grab(model.pointer, target, viz.ABS_GLOBAL)
			self.score.event(event = 'grab', description = 'Grabbed bounding box', source = target.name)
			target.highlight(True)
			
			self.hideNonActive(target)
			
			if self._lastBoxGrabbed and self._lastBoxGrabbed is not target:
				if self._lastBoxGrabbed in grabList:
					self._lastBoxGrabbed.highlight(True)
				else:
					self._lastBoxGrabbed.highlight(False)
					
			self._lastBoxGrabbed = target
			
		self._lastGrabbed = target
		self._grabFlag = True
		
	def highlightGrabbedMesh(self, mesh, flag):
		mesh.highlight(grabbed = flag)

	def release(self):
		"""Release grabbed object from pointer"""
		if self._gloveLink:
			if isinstance(self._lastGrabbed, bp3d.Mesh):
#				self.transparency(self._lastGrabbed, 1.0)
				self._gloveLink.remove()
				self._gloveLink = None
				self.score.event(event = 'release mesh')
			elif isinstance(self._lastGrabbed, BoundingBox):
				self._gloveLink.remove()
				self._gloveLink = None
				self.score.event(event = 'release bounding box')
		self._grabFlag = False
		
	def hideNonActive(self, activeBox):
		pass
	
	def getDisabled(self):
		""""""
		return [m for m in self._meshes if not m.getEnabled()]
		
	def getEnabled(self, includeGrounded = True):
		""""""
		if includeGrounded:
			return [m for m in self._meshes if m.getEnabled()]
		else:
			return [m for m in self._meshes if m.getEnabled() if not m.group.grounded]

	def getClosestObject(self, pointer, proxList):
		"""
		Looks through proximity list and searches for the closest bone to the glove and puts it at
		the beginning of the list
		"""
		if(len(proxList) >0):
			bonePos = proxList[0].getPosition(viz.ABS_GLOBAL)
			pointerPos = pointer.getPosition(viz.ABS_GLOBAL)
			shortestDist = vizmat.Distance(bonePos, pointerPos)	
			
			for i,x in enumerate(proxList):
				bonePos = proxList[i].getPosition(viz.ABS_GLOBAL)
				pointerPos = pointer.getPosition(viz.ABS_GLOBAL)
				tempDist = vizmat.Distance(bonePos,pointerPos)
				
				if(tempDist < shortestDist):
					shortestDist = tempDist
					tempBone = proxList[i]
					proxList[i] = proxList[0]
					proxList[0] = tempBone
		return proxList[0]
		
	def updateClosestBone(self):
		self._lastMesh = []
		while True:
			yield viztask.waitFrame(1)

			if self._lastBoxGrabbed:
				#only highlights bones for picking up in your active region
				prox = list(set.intersection(set(self._lastBoxGrabbed._members), set(self._proximityList)))
			else:
				prox = list(set(self._proximityList) - set(self._boundingBoxes.values()))
			
			if prox and not self._gloveLink:
				self._closestMesh = self.getClosestObject(model.pointer, prox)
				
				
				if self._lastMesh and self._lastMesh is not self._closestMesh:
					if self._lastMeshGrabbed is self._lastMesh[0]:
						self._lastMesh[0].highlight(grabbed = True)
					else:
						if self._lastMesh[0] in prox:
							self._lastMesh[0].highlight(prox = True)
						else:
							self._lastMesh[0].highlight(prox = False)
						
				self._closestMesh.highlight(closest = True)
					
				self._lastMesh = [self._closestMesh]
			else:
				self._closestMesh = None
			
			if self._lastGrabbed and self._closestMesh != self._lastGrabbed:
					self._lastGrabbed.color([0,1,0.5])
			
	def EnterProximity(self, e):
		"""Callback for a proximity entry event between the pointer and a mesh"""
		source = e.sensor.getSourceObject()
		model.pointer.color([4.0,0.5,0.5])
		source.highlight(True)
		self._proximityList.append(source)
		if self._lastMeshGrabbed:
			self._lastMeshGrabbed.highlight(grabbed = True)
	
	def ExitProximity(self, e):
		"""Callback for a proximity exit event between the pointer and a mesh"""
		source = e.sensor.getSourceObject()
		self._proximityList.remove(source)
		if len(self._proximityList):
			model.pointer.color([4.0,0.5,0.5])
		else:
			model.pointer.color(1,1,1)
		if source != self._lastGrabbed:
			source.highlight(False)
		if self._lastMeshGrabbed:
			self._lastMeshGrabbed.highlight(grabbed = True)
	
	def implode(self):
		"""Move bones to solved positions"""
		if not self._imploded:
			if self._boundingBoxes:
				for box in self._boundingBoxes.values():
					box.implode()
			else:
				target = self._keystones[0] # Move to the current keystone(s)
				for m in self._meshes[1:]:
					if m.getAction():
						return
					for bone in [b for b in self._meshes if b != m]:
						bone.checker.setPosition(m.centerPoint, viz.ABS_PARENT)
					m.storeMat()
					m.moveTo(target.checker.getMatrix(viz.ABS_GLOBAL), time = 0.6)

			self._keyBindings[3].setEnabled(viz.OFF)  #disable snap key down event
			self._keyBindings[4].setEnabled(viz.OFF)  #disable snap key down event
			self._imploded = True

	def explode(self):
		"""Move bones to position before implode was called"""
		if self._imploded:
			if self._boundingBoxes:
				for box in self._boundingBoxes.values():
					box.explode()
#					if not box._showGroupFlag:
#						box.showMembers(False)
			else:
				for m in self._meshes[1:]:
					if m.getAction():
						return
					m.moveTo(m.loadMat(), time = 0.6)
					
			self._keyBindings[3].setEnabled(viz.ON) #enable snap key down event
			self._keyBindings[4].setEnabled(viz.ON) #enable snap key down event
			self._imploded = False

	def solve(self):
		"""Operator used to toggle between implode and explode"""
		for m in self._meshes:
			if m.getAction():
				return
		if not self._imploded:
			self.implode()
		else:
			self.explode()


	def bindKeys(self):
		"""Define all key bindings and store them in a list"""
		self._keyBindings.append(vizact.onkeydown('o', model.proxManager.setDebug, viz.TOGGLE)) #debug shapes
		self._keyBindings.append(vizact.onkeydown(' ', self.grab)) #space select
		self._keyBindings.append(vizact.onkeydown('65421', self.grab)) #numpad enter select
		self._keyBindings.append(vizact.onkeydown(viz.KEY_ALT_R, self.snapCheck))
		self._keyBindings.append(vizact.onkeydown(viz.KEY_ALT_L, self.snapCheck))
#		self._keyBindings.append(vizact.onkeydown('65460', self.viewcube.toggleModes)) # Numpad '4' key
		self._keyBindings.append(vizact.onkeydown(viz.KEY_CONTROL_R, self.solve))
		self._keyBindings.append(vizact.onkeydown(viz.KEY_CONTROL_L, self.solve))
		self._keyBindings.append(vizact.onkeyup(' ', self.release))
		self._keyBindings.append(vizact.onkeyup('65421', self.release))
				
	def alphaSliceUpdate(self):
		"""This is the loop to get run on every frame to compute the alpha slice feature"""
		maxAlpha	= 1.00
		minAlpha	= 0.09
		topPlane	= 0.00005
		bottomPlane	= -0.0005
		
		while True:
			yield viztask.waitFrame(2)
			planePoint	= model.planeVert.Vertex(0).getPosition(viz.ABS_GLOBAL)
			planeNorm	= model.planeVert.Vertex(0).getNormal(viz.ABS_GLOBAL)
			for mesh in self._meshes:
				dist = planeProj(planePoint, planeNorm, mesh.getPosition(viz.ABS_GLOBAL))
				if dist >= topPlane:
					mesh.setAlpha(minAlpha)
				elif dist >= bottomPlane:
					distPercentage = 1 - ((dist - bottomPlane) / (topPlane - bottomPlane))
					mesh.setAlpha((distPercentage * (maxAlpha - minAlpha)) + minAlpha)
				else:
					mesh.setAlpha(maxAlpha)
	
	def enableSlice(self):
		"""Turn on slicing computation"""
		viztask.schedule(self.alphaSliceUpdate())
			
	def end(self):
		"""Do everything that needs to be done to end the puzzle game"""
		self.printNoticeable("Puzzle instance ending!")
		if self._lastMeshGrabbed:
			print self._lastMeshGrabbed
			self._lastMeshGrabbed.highlight(False)
#			self_lastMeshGrabbed.nameLine.clearVertices()
#			self_lastMeshGrabbed._lineUpdateEvent.remove()
			self._lastMeshGrabbed = None
		if self._lastBoxGrabbed:
			self._lastBoxGrabbed = None
		if self._lastGrabbed:
			self._lastGrabbed = None
#		self.score.close()
		model.proxManager.clearSensors()
		model.proxManager.clearTargets()
		model.proxManager.remove()
		self.unloadMeshes()
		for bind in self._keyBindings:
			bind.remove()
			
#		if self._quizPanel:
#			self._quizPanel.remove()
			
		self.endSpecificObjects()
			
	def endSpecificObjects(self):
		"""Ends objects specific to the game instance created (quiz, freeplay, or pindrop)"""
		pass
		
class FreePlay(PuzzleController):
	"""Free play mode allowing untimed, unguided exploration of the selected dataset(s)"""
	def __init__(self, dataset):
		super(FreePlay, self).__init__(dataset)
		self.modeName = 'freeplay'
	
	def load(self, dataset):
		"""
		Load datasets and initialize everything necessary to commence
		the puzzle game.
		"""
		
		# Dataset
		model.ds = bp3d.DatasetInterface()

		# Proximity management
		model.proxManager = vizproximity.Manager()
		target = vizproximity.Target(model.pointer)
		model.proxManager.addTarget(target)

		model.proxManager.onEnter(None, self.EnterProximity)
		model.proxManager.onExit(None, self.ExitProximity)

		#Setup Key Bindings
		self.bindKeys()
		

		self.score = PuzzleScore(self.modeName)
		
#		viztask.schedule(soundTask(glove))

		self._meshesToLoad = model.ds.getOntologySet(dataset)
		self._filesToPreSnap = model.ds.getPreSnapSet()
		
		viz.MainWindow.setScene(viz.Scene2) #change to loading screen scene
		yield self.loadControl(self._meshesToLoad)
		yield self.addToBoundingBox(self._meshes)
		yield self.prepareMeshes()
		yield self.disperseRandom(self._boundingBoxes.values())
		yield self.preSnap()
		yield self.setKeystone(3)
		yield rotateAbout(self._boundingBoxes.values() + self._meshes, [0,0,0], [0,90,0])
		viz.MainWindow.setScene(viz.Scene1) #change back to game scene
#		yield self.enableSlice()

		viztask.schedule(self.updateClosestBone())

	def getSnapTarget(self, source, search):
		if search:
			target = list(set.intersection(set(self._keystones), set(search)))
			if target: 
				return target[0]
			else:
				target = self._boundingBoxes[source.region]._keystones[0]
				return target
		else:
			return self.getAdjacent(self._lastGrabbed, self.getEnabled())[0]
			
	def hideNonActive(self, activeBox):
		"""Hides non-active bounding boxes and their elements"""
		if not activeBox.regionGroup.allRegionsFinished:
				activeBox.showMembers(True)
				[b.showMembers(False) for b in self._boundingBoxes.values() if b is not activeBox]
		if activeBox.regionGroup.allRegionsFinished:
			for bb in activeBox.regionGroup.members:
				bb.showMembers(True)
			[b.showMembers(False) for b in self._boundingBoxes.values() if b not in activeBox.regionGroup.members]

class TestPlay(PuzzleController):
	"""
	Assembly test play mode where the user is tasked with assembling the dataset
	in a specific order based off of a provided prompt.
	"""
	def __init__(self, dataset):
		super(TestPlay, self).__init__(dataset)
		self.modeName = 'testplay'
		
		self._meshesDisabled	= []
		self._keystoneAdjacent	= {}
		self._renderMeshes 		= []
		
		self._quizSource = None
		self._quizTarget = None
	
	
	def getKeystones(self):
		keystones = []
		for b in self._boundingBoxes.values():
			keystones.extend(b._keystones)
		return keystones

	def implode(self):
		"""Override to disable"""
		pass
		
	def explode(self):
		"""Override to disable"""
		pass
		
	def load(self, dataset = 'right arm'):
		"""
		Load datasets and initialize everything necessary to commence
		the puzzle game. Customized for test mode.
		"""
		
		# Dataset
		model.ds = bp3d.DatasetInterface()
		

		# Proximity management
		model.proxManager = vizproximity.Manager()
		target = vizproximity.Target(model.pointer)
		model.proxManager.addTarget(target)

		model.proxManager.onEnter(None, self.EnterProximity)
		model.proxManager.onExit(None, self.ExitProximity)
		
		#create list of meshes to load
		self._meshesToLoad = model.ds.getOntologySet(dataset)
		self._filesToPreSnap = model.ds.getPreSnapSet()
		
		#create and add quiz panel
		self._quizPanel = puzzleView.TestSnapPanel()
		self._quizPanel.toggle()
		
		#load and prep meshes
		viz.MainWindow.setScene(viz.Scene2) #change to loading screen scene
		yield self.loadControl(self._meshesToLoad)
		yield self.prepareMeshes()
		yield self.preSnap()
		yield self.addToBoundingBox(self._meshes)
		yield self.disperseRandom(self._boundingBoxes.values())
		yield self.setKeystone(3)
		yield self.testPrep()
		yield self.hideMeshes()
		yield rotateAbout(self._boundingBoxes.values(), [0,0,0], [0,90,0])
		viz.MainWindow.setScene(viz.Scene1) #change back to game scene
		
		# Setup Key Bindings
		self.bindKeys()
		
		#Schedule closest bone calculation
		viztask.schedule(self.updateClosestBone)
		
	def addToBoundingBox(self, meshes):
		"""
		Populate environment with bounding boxes allowing easy manipulation
		of subassemblies of the entire model. Currently partitioned by region.
		"""
		self._boundingBoxes['full'] = BoundingBox(meshes)
		
		
	def startingAdjacents(self, source, pool, number):
			for m in self.getAdjacent(source, pool)[0:number]:
				for mGroup in m.group.members:
					mGroup.enable(animate = False)
					self._renderMeshes.append(mGroup)
					pool = list(set(pool) - set([mGroup]))
			
	def prepareMeshes(self):
		"""Places meshes in circle around keystone(s)"""
		for m in self._meshes:
			m.addSensor()
		
	def testPrep(self):
		self.score	= PuzzleScore(self.modeName)
		keystones = self._boundingBoxes.values()[0]._keystones
		pureKeystones = self._boundingBoxes.values()[0]._pureKeystones
		meshes = list(set(self._meshes) - set(keystones))
#		keystone	= random.sample(self.getKeystones(), 1)[0]
#		self._keystoneAdjacent.update({keystone:[]})
		
#		for m in self.getAdjacent(keystone, self._meshes)[:4]:
#			for mGroup in m.group.members:
#				self._keystoneAdjacent[keystone].append(mGroup)
#				mGroup.enable(animate = False)
#		self.pickSnapPair()
		for keystone in pureKeystones:
			self.startingAdjacents(keystone, meshes, 3)
			meshes = list(set(meshes) - set(self._renderMeshes))
		self.pickSnapPair()
			
	def hideMeshes(self):
		keystones = set(self.getKeystones())
		meshes = set(self._meshes)
		renderMeshes = set(self._renderMeshes)
		hideMeshes = meshes - keystones - renderMeshes
		for m in hideMeshes:
			m.disable()
			
	def pickSnapPair(self):
		self._quizTarget = random.sample(self.getKeystones(), 1)[0]
		enabled = self.getEnabled(includeGrounded = False)
		if len(enabled) == 0:
			return
		self._quizSource = random.sample(self.getAdjacent(self._quizTarget, enabled)[:5],1)[0]
		self._quizPanel.setFields(self._quizSource.name, self._quizTarget.name)
		self.score.event(event = 'pickpair', description = 'Picked new pair of bones to snap', \
			source = self._quizSource.name, destination = self._quizTarget.name)
				
	def snap(self, sourceMesh, targetMesh, children = False, animate = True, add = True):
		"""Overridden snap that supports adding more bones"""
		self.moveCheckers(sourceMesh)
		if children:
			sourceMesh.setGroupParent()
		if animate:
			sourceMesh.moveTo(targetMesh.checker.getMatrix(viz.ABS_GLOBAL))
		else:
			sourceMesh.setPosition(targetMesh.checker.getPosition(viz.ABS_GLOBAL))
			sourceMesh.setEuler(targetMesh.checker.getEuler(viz.ABS_GLOBAL))
		targetMesh.group.merge(sourceMesh)
		if sourceMesh.group.grounded:
			self._keystones.append(sourceMesh)
		if add:
			self.addMesh()
		
	def addMesh(self):
		"""Add more meshes"""
		disabled = self.getDisabled()
		if len(disabled) == 0:
			return
		keystone = random.sample(self._keystones, 1)[0]
		try:
			m = self.getAdjacent(keystone, disabled)[random.randint(0,3)]
		except (ValueError, IndexError):
			m = self.getAdjacent(keystone, disabled)[0]
		for mGroup in m.group.members:
			mGroup.enable(animate = True)
			
	def highlightGrabbedMesh(self, mesh, flag):
		mesh.highlight(grabbed = flag, showTip = False)
	
	def getSnapSource(self):
		"""Define source object for snapcheck"""
		return self._quizSource
	
	def getSnapTarget(self):
		"""Define target object for snapcheck"""
		return self._quizTarget
		
	def getSnapSearch(self, source = None):
		"""Define list of objects to search for snapcheck"""
		return [self._quizTarget]
		
	def endSpecificObjects(self):
		"""Ends objects specific to the game instance created (quiz, freeplay, or pindrop)"""
		if self._quizPanel:
			self._quizPanel.remove()
		
		
class PinDrop(PuzzleController):
	"""
	The complementary of the puzzle assembly test mode, where the task is to annotate an assembled
	model instead of assemble a model from prompted annotations
	"""
	def __init__(self, dataset):
		super(PinDrop, self).__init__(dataset)
		self.modeName = 'pindrop'
		
		self._dropTarget = None
		self._dropAttempts = 0
		
	def pickLabelTarget(self):
		unlabeled = [m for m in self._meshes if not m.labeled]
		self._dropTarget = random.sample(unlabeled, 1)[0]
	
	def pinCheck(self):
		if self._dropAttempts >= 3:
			pass

	def loadControl(self):
		yield self.loadMeshes(self._meshesToLoad)
		for m in self._meshes:
			m.addSensor()
			m.addToolTip(self._boundingBoxes[m.region])
		self.setKeystone(len(self._meshes))
		
	def bindKeys(self):
		self._keyBindings.append(vizact.onkeydown('o', model.proxManager.setDebug, viz.TOGGLE)) #debug shapes
		self._keyBindings.append(vizact.onkeydown(viz.KEY_ALT_R, self.pinCheck))
		self._keyBindings.append(vizact.onkeydown(viz.KEY_ALT_L, self.pinCheck))
#		self._keyBindings.append(vizact.onkeydown('65460', self.viewcube.toggleModes)) # Numpad '4' key
	
class BoundingBox(viz.VizNode):
	def __init__(self, meshes):
		"""
		Populate environment with bounding boxes allowing easy manipulation
		of subassemblies of the entire model. Currently partitioned by region.
		"""
		
		self.name				= ''		
		self._alpha				= 0.3
		self._members			= []
		self._keystones 		= []
		self._pureKeystones		= []
		self.wireFrame			= None
		self._showGroupFlag 	= True
		
		self.finishedRegion = False
		
		self.axis = vizshape.addAxes()
		self.cube = vizshape.addCube()
		
		super(BoundingBox, self).__init__(self.cube.id)
		
		self.cube.disable(viz.RENDERING)
		self.axis.setParent(self)
		self.axis.setScale([0.2, 0.2, 0.2])
		
		self.addSensor()
		self.addMembers(meshes)
		
		self.regionGroup = RegionGroup([self])
#		self.moveToCenter()

		# Add Bounding Box checker
		self.checker = vizshape.addCube(0.001)
		self.checker.setParent(self)
		self.checker.disable([viz.RENDERING,viz.INTERSECTION,viz.PHYSICS])

		self.highlight(False)
		
		self._imploded = False
	
	def alpha(self, val):
		"""Set the alpha of both the axis and wireframe"""
		self._alpha = val
		self.axis.alpha(val)
		self.wireFrame.alpha(val)
		
	def addMembers(self, meshes):
		"""Add members, updating bounds of cube"""
		for m in meshes:
			self._members.append(m)
			changeParent(m, self)
		self.updateWireframe()
	
	def removeMembers(self, meshes):
		"""Remove members, updating bounds of cube"""
		for m in meshes:
			if m in self._members:
				changeParent(m)
				self._members.remove(m)
				
	def moveToCenter(self, meshes):
		"""Move any stray meshes to within bounds of cube"""
		for m in meshes:
			pass
		
	def updateWireframe(self):
		"""Compute size of wireframe and update given current members"""
		if self.wireFrame:
			self.wireFrame.remove()
		self.wireFrame = puzzleView.WireFrameCube(self.computeBounds(), corner = True)
		self.wireFrame.setParent(self)
		self.wireFrame.alpha(self._alpha)
			
	def computeBounds(self):
		"""Compute bounding box given current members"""
		min, max = self._members[0].metaData['bounds']		
		for m in self._members[1:]:
			for i, v in enumerate(m.metaData['bounds'][0]):
				if v < min[i]:
					min[i] = v
			for i, v in enumerate(m.metaData['bounds'][1]):
				if v > max[i]:
					max[i] = v
		
		min = rightToLeft(min) # WHY VIZARD WHY
		max = rightToLeft(max) # WHY WHYYYY
		self.bounds				= [(v[0]-v[1]) for v in zip(max,min)]
		self.boundsScaled		= [v/500.0 for v in self.bounds]
		self.cornerPoint		= min
		self.cornerPointScaled	= [v/500.0 for v in min]
		self.centerPoint		= [(v[0]/2.0 + v[1]) for v in zip(self.bounds,min)]
		self.centerPointScaled	= [v/500.0 for v in self.centerPoint]
		
		return self.boundsScaled
	
	def addSensor(self):
		"""Add a sensor around the axis to a proximity manager"""
		self._sensor = vizproximity.Sensor(vizproximity.Sphere(0.4),self)
		model.proxManager.addSensor(self._sensor)
	
	def storeMat(self):
		"""Store current transformation matrix"""
		self._savedMat = self.getMatrix(viz.ABS_GLOBAL)
		
	def loadMat(self):
		"""Recall stored transformation matrix"""
		return self._savedMat
		
	def grab(self):
		"""Run on grab"""
		for m in self._members:
			changeParent(m, self)
		self.setRegionGroupParent()

	def highlight(self, flag):
		"""Make visible out of the noise"""
		if flag:
			self.alpha(1.0)
		else:
			self.alpha(0.3)
			
	def showMembers(self, flag):
		if flag:
			val = 1.0
			if not self.finishedRegion:
				self.showRing(True)
			elif self.finishedRegion:
				self.showRing(True, val)
			self._showGroupFlag = True
		else:
			val = 0.2
			if not self.finishedRegion:
				self.showRing(False)
			elif self.finishedRegion:
				self.showRing(False, val)
			self._showGroupFlag = False
		
		self.showKeystones(val)
			
	def showKeystones(self, val = None):
		for m in self._keystones:
			m.setAlpha(val)
	
	def showRing(self, flag, val = None):
		if not flag:
			keystones = set(self._keystones)		
			meshes = set(self._members)
			ring = list(meshes - keystones)
			
			for m in [m for m in ring if m.getEnabled()]:
				if not val:
					m.disable()
				else:
					m.setAlpha(val)
		else:
			for m in self._members:
				if not val:
					m.enable()
				else:
					m.setAlpha(val)
		
	def disperseMembers(self):
		
		majorLength = max(self.computeBounds())
		
		for m in self._members:
			m.setGroupParent()
			changeParent(m, self)
			angle	= random.random() * 2 * math.pi
			radius	= random.random() * majorLength/2 + majorLength
			
			targetPosition	= [math.sin(angle) * radius, 0, math.cos(angle) * radius]
			targetEuler		= m.getEuler()
#			targetEuler		= [0.0,90.0,180.0]
			#targetEuler	= [(random.random()-0.5)*40,(random.random()-0.5)*40 + 90.0, (random.random()-0.5)*40 + 180.0]
			
			centervect		= list(numpy.subtract(self.centerPointScaled, self.cornerPointScaled))
			targetPosition	= list(numpy.add(targetPosition, centervect)) # Donut around center instead
			
			m.setPosition(targetPosition, viz.ABS_PARENT)
			m.setEuler(targetEuler, viz.ABS_PARENT)
			
	def setGroup(self, group):
		"""Set bone group"""
		self.regionGroup = group
		
	def setRegionGroupParent(self):
		"""
		When manipulating a group of bones, the grabbed bone must move all
		of the other group members
		"""
		self.regionGroup.setParent(self)
	
	def moveChecker(self, BB):
		"""Find the position that 'self' bounding box should move to in relation to BB"""
		BBVec = BB.getPosition(viz.ABS_GLOBAL)
		vecDiff = list(numpy.subtract(self.cornerPointScaled, BB.cornerPointScaled))
		BB.checker.setPosition(vecDiff, mode = viz.ABS_PARENT)
		
		targetEuler = BB.checker.getEuler(viz.ABS_GLOBAL)
		targetPos = BB.checker.getPosition(viz.ABS_GLOBAL)
		
		return targetPos, targetEuler
	
	def findClosestBB(self, boundingBoxes):
		"""Find and return the bounding box closest to self"""
		leastDistance = None
		closestBB = None
		distanceBtwn = None
		BBs = set(boundingBoxes) - set(self.regionGroup.members)
		for bb in BBs:
			tPos, tEuler = self.moveChecker(bb)
			distanceBtwn = vizmat.Distance(self.getPosition(viz.ABS_GLOBAL), tPos)
			if distanceBtwn <= leastDistance or leastDistance is None:
				closestBB = bb
				leastDistance = distanceBtwn
		return closestBB, leastDistance
		
	def snapToBB(self, BB):
		"""Snaps Bounding Box to Another Bounding Box, BB"""
		self.moveTo(BB)
		self.regionGroup.merge(BB)
		self.regionGroup.getFinished()
		if self.regionGroup.allRegionsFinished:
			for bb in self.regionGroup.members:
				bb.showMembers(True)
		
			
	def moveTo(self, BB, animate = True, time = 0.3):
		"""
		move bounding box to new targetPos and targetEuler
		"""
		targetPos = BB.checker.getPosition(viz.ABS_GLOBAL)
		targetEuler = BB.checker.getEuler(viz.ABS_GLOBAL)
		if (animate):
			move = vizact.moveTo(pos = targetPos, time = time, mode = viz.ABS_GLOBAL)
			spin = vizact.spinTo(euler = targetEuler, time = time, mode = viz.ABS_GLOBAL)
			transition = vizact.parallel(spin, move)
			self.addAction(transition)
		else:
			self.setPosition(targetPosition, viz.ABS_GLOBAL)
			self.setEuler(targetEuler,viz.ABS_GLOBAL)
			
	def formatAxisAfterSnap(self):
		lowestRegion = self
		bottom = 0
		a = set(self.regionGroup.members) - set([self])
		for bb in a:
			pos = bb.getPosition()
			pos = bb.getPosition()
#			if pos > bottom:
#				lowestRegion = bb
#				bottom = pos
#				
#		for bb in list(set(self.regionGroup.members) - set([lowestRegion])):
#			bb.axis.disable(viz.RENDERING)
			
	def hideAxis(self):
		self.axis.disable(viz.RENDERING)
		
	def setKeystones(self, count):
		for k in random.sample(self._members, count):
			k.setGroupParent()
			changeParent(k, self)
			diff = list(numpy.subtract(k.centerPointScaled, self.cornerPointScaled))
			k.setPosition(diff, viz.ABS_PARENT)
			self._pureKeystones.append(k)
			for m in k.group.members:
				self._keystones.append(m)
			m.group.grounded = True
			
		[self._keystones[0].group.merge(key) for key in self._keystones[1:]]
			
	
	def implode(self):
		"""Move bones to solved positions"""
		if not self._imploded:
			target = self._keystones[0] # Move to the current keystone(s)
			for m in [m for m in self._members if not m.group.grounded]:
				if m.getAction():
					return
				changeParent(m, self.axis)
				for bone in [b for b in self._members if b != m]:
					bone.checker.setPosition(m.centerPoint, viz.ABS_PARENT)
				m.storeMat(relation = viz.ABS_PARENT)
				m.moveTo(target.checker.getMatrix(viz.ABS_GLOBAL), time = 0.6)
				
			self._imploded = True
#		self._keyBindings[3].setEnabled(viz.OFF)  #disable snap key down event

	def explode(self):
		"""Move bones to position before implode was called"""
		if self._imploded:
			for m in [m for m in self._members if not m.group.grounded]:
				if m.getAction():
					return
				changeParent(m, self.axis)
				m.moveTo(m.loadMat(), time = 0.6, relation = viz.ABS_PARENT)
			self._imploded = False
#		self._keyBindings[3].setEnabled(viz.ON) #enable snap key down event
		
class RegionGroup ():
		def __init__(self, members):
			self.members = []
			self.parent = members[0]
			self.addMembers(members)
			self.allRegionsFinished = False
			
		def setParent(self, parent):
			"""Set region bounding box to parent of all other bouding boxes in the group"""
			self.parent = parent
			curMat = parent.getMatrix(viz.ABS_GLOBAL)
			parent.setParent(viz.WORLD)
			parent.setMatrix(curMat, viz.ABS_GLOBAL)
			
			for r in [r for r in self.members if r != parent]:
				curMat = r.getMatrix(viz.ABS_GLOBAL)
				r.setParent(parent)
				r.setMatrix(curMat, viz.ABS_GLOBAL)
		
		def addMembers(self, members):
			"""Add a list of regions to members list"""
			self.members += members 
			for r in members:
				r.regionGroup = self
				
		def merge(self, source):
			"""Merge group members into source group"""
			self.members += source.regionGroup.members
			self.members = list(set(self.members))
			#delet source.group
			for r in source.regionGroup.members:
				r.setGroup(self)
				
		def getFinished(self):
			"""Determines if all bounding boxes in the RegionGroup have been finished"""
			numMembers = len(self.members)
			membersFin = 0
			for bb in self.members:
				print bb.finishedRegion
				if bb.finishedRegion:
					membersFin += 1
			if numMembers == membersFin:
				self.allRegionsFinished = True
			else:
				self.allRegionsFinished = False

class PuzzleScore():
	"""Handles scoring for the puzzle game"""
	def __init__(self, modeName):
		"""Init score datastructure, open up csv file"""
		self.startTime = datetime.datetime.now()
		self.scoreFile = open('.\\log\\'+ modeName + '\\' + self.startTime.strftime('%m%d%Y_%H%M%S') + '.csv', 'wb')
		self.csv = csv.writer(self.scoreFile)
		
		# Starting score
		self.score = 100
		
		self.header = ['timestamp','event name','description','source','destination']
		self.events = []
		
		self.csv.writerow(self.header)
		
#		self.textbox = viz.addTextbox()
#		self.textbox.setPosition(0.8,0.1)
#		self.textbox.message('Score: ' + str(self.score))
	
	def event(self, event = None, description = None, source = None, destination = None):
		"""Record an event in the score history"""
		print 'Score event!'
		currentEvent = dict(zip(self.header,[time.clock(), event, description, source, destination]))
		self.events.append(currentEvent)
		self.csv.writerow([self.events[-1][column] for column in self.header])
		
		self.update(self.events)
		
	def update(self, events):
		"""Iterative score calculation"""
		curEvent = events[-1]
		
		if curEvent['event name'] == 'snap' or curEvent['event name'] == 'autosnap':
			scoreWeights = [10, 5, 2, 0] # 10pt for first attempt, 5 for second attempt, etc...
			snapCount = 0
			i = -2

			while True: # How many snaps did it take?
				if events[i] == 'snap' or events[i] == 'autosnap':
					self.score += scoreWeights[snapCount]
					break
				if events[i] == 'snapfail':
					snapCount += 1
				if -i > len(events) - 1:
					break
				i -= 1
				
		print self.score
#		self.textbox.message('Score: ' + str(self.score))

	def close(self):
		"""
		Close CSV file
		"""
		self.csv.close()

def end():
	"""Do everything that needs to be done to end the puzzle game"""
	print "Puzzle Quitting!"
	global controlInst
	if controlInst:
		controlInst.end()
#	except AttributeError:
#		print 'Not initialized'
#	del(controlInst)

def start(mode, dataset):
	"""Start running the puzzle game"""
	global controlInst
	global menuMode
	
	menuMode = mode
	
	if mode == 'Free Play':
		controlInst = FreePlay()
	elif mode == 'Quiz Mode':
		controlInst = TestPlay()
	try:
		controlInst.load(dataset)
	except KeyError:
		print "Dataset does not exist!"
		raise

def csvToList(location):
	"""Read in a CSV file to a list of lists"""
	raw = []
	try:
		with open(location, 'rb') as csvfile:
			wowSuchCSV = csv.reader(csvfile, delimiter=',')
			for row in wowSuchCSV:
				raw.append(row)
	except IOError:
		print "ERROR: Unable to open CSV file at", location
	return raw

def playName(boneObj):
	"""Play audio with the same name as the bone"""
	try:
		viz.playSound(path + "audio_names\\" + boneObj.name + ".wav") # should be updated to path
	except ValueError:
		print ("the name of the audio name file was wrong")
		
def planeProj(planePoint, planeNormal, targetPoint):
	"""
	Take in plane given by equation ax+by+cz+d=0 in the format [a, b, c, d] and
	compute projected distance from point
	"""
	planeToTarget = numpy.subtract(targetPoint, planePoint)
	return numpy.dot(planeNormal, planeToTarget)

def rotateAbout(meshes, point, euler):
	pointCube = vizshape.addCube()
	pointCube.setPosition(point, viz.ABS_GLOBAL)
	
	for m in meshes:
		changeParent(m, pointCube)
		
	pointCube.setEuler(euler)
	
	for m in meshes:
		m.storeMat()
		m.setParent(viz.WORLD)
		m.setMatrix(m.loadMat())
		
	pointCube.remove()

def changeParent(mesh, newParent = viz.WORLD):
	"""Set a new parent while maintaining position"""
	curMat = mesh.getMatrix(viz.ABS_GLOBAL)
	mesh.setParent(newParent)
	mesh.setMatrix(curMat, viz.ABS_GLOBAL)

def rightToLeft(center):
	"""
	Convert from right handed coordinate system to left handed
	"""
	return [center[0], center[1], center[2]*-1]