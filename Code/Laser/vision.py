#!/usr/bin/env python
import numpy as np
import cv2
import Image
import zbar
import time

class CameraException(Exception):
    '''Any camera-related errors'''
    def __init__(self, msg):
        self.msg = msg

class Vision(object):

    def __init__(self,camera):
        # Open camera, and get image dimensions
        self.cap = cv2.VideoCapture(camera)
        self.width = int(self.cap.get(3))
        self.height = int(self.cap.get(4))
        
        # Set up scanner
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')
        
        # Set up code cache
        self.cache = {}
    
    def updateCache(self):
        # Get time for framerate caluclation
        stime = time.time()

        # Set cache-update flag
        updated = False
    
        # Capture frame-by-frame
        ret, frame = self.cap.read()
        if not ret:
            raise CameraException('Dropped frame!')
    
        # zbar needs a monochrome image in PIL string format
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        pil_gray = Image.fromarray(gray).tostring()
        image = zbar.Image(self.width, self.height, 'Y800', pil_gray)
    
        # Scan image and annotate all the codes with outline, center, and data
        self.scanner.scan(image)
        for symbol in image:
    
            # outline symbol
            ul,ur,lr,ll = symbol.location
            #loc = np.array(symbol.location,np.int32)
            #loc = loc.reshape((-1,1,2))
            #cv2.polylines(frame,[loc],True,(0,0,255),2)
            
            # draw a circle at the center of the symbol
            avgx = (ul[0]+ur[0]+lr[0]+ll[0])/4
            avgy = (ul[1]+ur[1]+lr[1]+ll[1])/4
            #cv2.circle(frame,(avgx,avgy),5,(0,255,0),2)
    
            # label the symbol center with its data
            #cv2.putText(frame,symbol.data,(avgx,avgy),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2)
    
            # update cache
            try:
                if abs(self.cache[symbol.data][0] - avgx) > 10 or\
                   abs(self.cache[symbol.data][1] - avgy) > 10:
                    self.cache[symbol.data] = (avgx,avgy)
                    updated = True
                    print '%s moved to (%.1f,%.1f)'%(symbol.data,avgx,avgy)
            except KeyError:
                self.cache[symbol.data] = (avgx,avgy)
                updated = True
                print 'New symbol %s at (%.1f,%.1f)'%(symbol.data,avgx,avgy)
    
        # Display the resulting frame and annotate with framerate
        etime = time.time()
        fps = 1.0/(etime - stime)
        print '%.1ffps'%fps
        #cv2.putText(frame,'%.1ffps'%fps,(5,15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1)
        #cv2.imshow('frame',frame)
        #cv2.destroyAllWindows()
        if updated:
            return self.cache
        else:
            return None

    def cleanup():
        # When everything done, release the capture
        cap.release()

if __name__ == '__main__':
    from pprint import pprint
    import sys
    print sys.argv[1]
    v = Vision(int(sys.argv[1]))
    while(True):
        cache = v.updateCache()
        if cache is not None:
            pprint(cache)
        raw_input('Please hit ENTER when ready')
