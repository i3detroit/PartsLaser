import Adafruit_BBIO.PWM as PWM
import time
import math
import servo
import platform
import numpy as np

class PartsLaserSearch:
	
	def __init__(self, startLocation, targetData, servos):
		self.__targetData=targetData

		self.__waitFrames=5

		#TODO: remove for real usage :P
		self.__location=startLocation

		self.__servos = servos

		#Init all searches to nothing
		self.__xSearch=None
		self.__ySearch=None

		#The min/max we can set for each search range
		self.__xRange=(8.75,11.3)
		self.__yRange=(6.8,9.7)
		#self.__xRange=(8.75,11.3)
		#self.__yRange=(6.8,9.7)

		#First is the most we should ever adjust
		#Second is the amount to adjust during pan/scan mode
		#Third is the least we can adjust
		self.__xResolution=(0.2,.4,0.1)
		self.__yResolution=(0.2,0.4,0.1)

		print("Searching to",self.__targetData,"from",self.__location)


	##TODO we should update the target location here.
	#If we can't see it, then return null.
	#If we can see it, we should return the x,y distance between the target and the laser
	def getTargetDelta(self, targetData,retries):


		#TODO: get the delta from vision
		# we should loop for retries
		target=(10.2,8.4)
		delta=(target[0]-self.__location[0],target[1]-self.__location[1])
		#TODO: we should loop over all of the targets we can see. 
		# If this is the closest we've been (or if the cache is stale?)
		# we should store the servo location into the cache

		
		#TODO: if we're at (near?) the cached position and we can't see
		# the target, we need to remove it from the cache

		#TODO: if we can't see the target, but it is in the cache, we
		# should compute a delta from the cached position
		# _______________OR_____________
		# When moving to a new target, we jump to the cached position 
		# first. If it isn't there, clear the cache. This is probably
		# a better choice, but requires more logic around the search
		

		#TODO: remove this, it simulates targets being out of sight
		if math.sqrt(delta[0]*delta[0]+delta[1]*delta[1]) > 0.25:
			return None
		return delta

	#If we can see our target, search to it. If we can't pan and scan.
	#Pan and Scan will leave the target in vision and return the current position, or return None
	#TODO: If we could see the target, and now can, we should move back and do "something else"
	def search(self):

		target = self.panScanSearch(self.__targetData,servos)

		if target is None:
			return False
		
		while target is not None and self.__searchCanSee(target,servos):
			time.sleep(0.1)
			target=self.getTargetDelta(self.__targetData,self.__waitFrames)
		return self.__location

	#Pan and Scan will leave the target in vision and return the current position, or return None
	def panScanSearch(self,targetData,servos):
		#We need to check the current location and not move if we can see the target
        #This is basically a do/while loop, but it's easier to write this way :P
		target=self.getTargetDelta(targetData,self.__waitFrames)
		if target is not None:
			return target

		#we didn't find it. revert to pan/scan search
		self.__xSearch=None
		self.__ySearch=None

		for x in np.arange(self.__xRange[0],self.__xRange[1],self.__xResolution[1]*2):
			self.__location[0]=x
			servos[0].servo_set_direct(self.__location[0])

			for y in np.arange(self.__yRange[0],self.__yRange[1],self.__yResolution[1]):
				self.__location[1]=y
				servos[1].servo_set_direct(self.__location[1])
				print("Scanning",self.__location)
				time.sleep(0.1)
				target=self.getTargetDelta(targetData,self.__waitFrames)
				if target is not None:
					return target

			self.__location[0]=x+self.__xResolution[1]
			servos[0].servo_set_direct(self.__location[0])
			for y in np.arange(self.__yRange[1],self.__yRange[0],-self.__yResolution[1]):
				self.__location[1]=y
				servos[1].servo_set_direct(self.__location[1])
				print("Scanning",self.__location)
				time.sleep(0.1)
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
				servos[0].servo_set_direct(self.__location[0])
				return True

		delta=self.__ySearch.search(targetDelta[1],lost)
		if delta is not None:
			self.__location[1]+=delta
			self.__xSearch.lastDelta=None
			print("Moving to",self.__location)
			servos[1].servo_set_direct(self.__location[1])
			return True
		return False

#Searches for the target along a single dimension, should be reset if any other dimesion was moved
class OneDimensionSearch():

	def __init__(self,resolution,minResolution):
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
				if self.__resolution - self.__minResolution < 0.01:
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
	print("servo setup")
	servos=servo.setupServos()

	l=PartsLaserSearch([9,9],"doesn't matter",servos)
	target = l.search()
	if target is not None:
		platform.draw_box(target,servos[0],servos[1],0.25,0.3)
	
	print("servo shutdown")
	servo.shutdownServos()
