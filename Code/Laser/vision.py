#!/usr/bin/env python
import numpy as np
from gi.repository import Aravis
import Image
import zbar
import time

class CameraException(Exception):
    '''Any camera-related errors'''
    def __init__(self, msg):
        self.msg = msg

class Vision(object):

    def __init__(self):
        # Open camera, and get image dimensions
        Aravis.enable_interface('Fake')
        self.camera = Aravis.Camera.new(None)
        self.stream = self.camera.create_stream(None,None)
        payload = self.camera.get_payload()
        self.stream.push_buffer(Aravis.Buffer.new_allocate(payload))
        x,y,w,h = self.camera.get_region()
        self.width = w
        self.height = h
        self.camera.start_acquisition()
        
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
        buffer = self.stream.pop_buffer()
        frame = buffer.get_data()
        self.stream.push_buffer(buffer)

        # zbar needs a monochrome image in PIL string format
        image = zbar.Image(self.width, self.height, 'Y800', frame)
    
        # Scan image and annotate all the codes with outline, center, and data
        self.scanner.scan(image)
        for symbol in image:
    
            # outline symbol
            ul,ur,lr,ll = symbol.location
            avgx = (ul[0]+ur[0]+lr[0]+ll[0])/4
            avgy = (ul[1]+ur[1]+lr[1]+ll[1])/4
    
            # update cache
            try:
                if abs(self.cache[symbol.data][0] - avgx) > 10 or\
                   abs(self.cache[symbol.data][1] - avgy) > 10:
                    self.cache[symbol.data] = (avgx,avgy)
                    updated = True
                    print '%s moved to (%.1f,%.1f)'%(symbol.data,avgx,avgy)
                    Image.fromstring('L',(self.width,self.height),frame).\
                            save('codes/%s_%s_%s.png'%(symbol.data,avgx,avgy))
            except KeyError:
                self.cache[symbol.data] = (avgx,avgy)
                updated = True
                print 'New symbol %s at (%.1f,%.1f)'%(symbol.data,avgx,avgy)
                Image.fromstring('L',(self.width,self.height),frame).\
                        save('codes/%s_%s_%s.png'%(symbol.data,avgx,avgy))
    
        # Display the resulting frame and annotate with framerate
        etime = time.time()
        fps = 1.0/(etime - stime)
        print '%.1ffps'%fps
        if updated:
            return self.cache
        else:
            return None

    def cleanup(self):
        # When everything done, release the capture
        self.camera.stop_acquisition()

if __name__ == '__main__':
    from pprint import pprint
    import sys
    v = Vision()
    while(True):
        cache = v.updateCache()
        if cache is not None:
            pprint(cache)
        raw_input('Please hit ENTER when ready')
