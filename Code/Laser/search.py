#!/usr/bin/env python
import math

class PartsLaserSearch:
	
	def __init__(self, startLocation, targetData):
		self.__targetData=targetData

		self.__waitFrames=5

		#TODO: remove for real usage :P
		self.__location=startLocation

		#Init all searches to nothing
		self.__xSearch=None
		self.__ySearch=None

		#The min/max we can set for each search range
		self.__xRange=(0,100)
		self.__yRange=(0,100)

		#First is the most we should ever adjust
		#Second is the amount to adjust during pan/scan mode
		#Third is the least we can adjust
		self.__xResolution=(8,4,1)
		self.__yResolution=(8,4,1)

		print("Searching to",self.__targetData,"from",self.__location)


	##TODO we should update the target location here.
	#If we can't see it, then return null.
	#If we can see it, we should return the x,y distance between the target and the laser
	def getTargetDelta(self, targetData,retries):

		#TODO: get from vision
		target=(75.5,30.5)
		#TODO: we should loop for retries and only return None if we can't fid the target
		delta=(target[0]-self.__location[0],target[1]-self.__location[1])
		if math.sqrt(delta[0]*delta[0]+delta[1]*delta[1]) > 24:
			return None
		return delta

	#If we can see our target, search to it. If we can't pan and scan.
	#Pan and Scan will leave the target in vision and return the current position, or return None
	#TODO: If we could see the target, and now can, we should move back and do "something else"
	def search(self):
		target = self.panScanSearch(self.__targetData)
		if target is None:
			return False
		return self.__searchCanSee(target)

	#Pan and Scan will leave the target in vision and return the current position, or return None
	def panScanSearch(self,targetData):
		#We need to check the current location and not move if we cam see the target
        #This is basically a do/while loop, but it's easier to write this way :P
		target=self.getTargetDelta(targetData,self.__waitFrames)
		if target is not None:
			return target

		#we didn't find it. revert to pan/scan search
		self.__xSearch=None
		self.__ySearch=None

		for x in range(self.__xRange[0],self.__xRange[1],self.__xResolution[1]):
			for y in range(self.__yRange[0],self.__yRange[1],self.__yResolution[1]):
				##TODO: this should actually move something
				self.__location[0]=x
				self.__location[1]=y
				print("Scanning",self.__location)
				target=self.getTargetDelta(targetData,self.__waitFrames)
				if target is not None:
					return target
		return None
				

	#__target needs to be set
	#returns a best effort at moving the camera towards the target in a single dimension
	#TODO: we should add functionality if our last move caused us to lose the target
	#		the solution is probably to cut the resolution.
	def __searchCanSee(self,targetDelta,lost=False):
		self.__panScanSearch = None

		if self.__xSearch is None:
			self.__xSearch=OneDimensionSearch(self.__xResolution[0],self.__xResolution[2])
		if self.__ySearch is None:
			self.__ySearch=OneDimensionSearch(self.__yResolution[0],self.__yResolution[2])
			
		print("Delta is",targetDelta)
		if math.fabs(targetDelta[0]) > math.fabs(targetDelta[1]):
			delta=self.__xSearch.search(targetDelta[0],lost)
			if delta is not None:
				self.__location[0]+=delta
				self.__ySearch.lastDelta=None
				print("Moving to",self.__location)
				return True

		delta=self.__ySearch.search(targetDelta[1],lost)
		if delta is not None:
			self.__location[1]+=delta
			self.__xSearch.lastDelta=None
			print("Moving to",self.__location)
			return True
		return False

#Searches for the target along a single dimension, should be reset if any other dimesion was moved
class OneDimensionSearch():

	def __init__(self,resolution=8,minResolution=1):
		self.__resolution=resolution
		self.__minResolution=minResolution
		self.__lastDelta=None

	#TODO: we should add functionality if our last move caused us to lose the target
	#		the solution is probably to cut the resolution.
	def search(self,delta,lost):
		if delta==0:
			return None

		#If we passed the target, decrease resolution. If we're at the minimum
		#then we return.
		if self.__lastDelta is not None:
			if math.copysign(1,self.__lastDelta) != math.copysign(1,delta) or lost is True:
				if self.__resolution == self.__minResolution:
					#We could bounce back in an attempt to select the closest
					#position. We'd want to be careful about creating an 
					#infinite loop if that makes the other dimension larger
					print("overshot target at min resolution",self.__lastDelta,delta,lost)
					return None
				else:
					self.__resolution=max(self.__resolution/2, self.__minResolution)
		self.__lastDelta=delta
		return math.copysign(self.__resolution,delta)


if __name__ == '__main__':
	l=PartsLaserSearch([50,50],"doesn't matter")
	while l.search() is True:
		print("searching...")
