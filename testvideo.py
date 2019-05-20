# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 13:31:50 2019

@author: chaos
"""

import numpy as np
import cv2

# Open a sample video available in sample-videos
vcap = cv2.VideoCapture('http://140.136.155.137:5003/stream')
if not vcap.isOpened():
    print("File Cannot be Opened")

while(True):
    # Capture frame-by-frame
    ret, frame = vcap.read()
    #print cap.isOpened(), ret
    if frame is not None:
        # Display the resulting frame
        cv2.imshow('frame',frame)
        # Press q to close the video windows before it ends if you want
        if cv2.waitKey(22) & 0xFF == ord('q'):
            break
    else:
        print("Frame is None")
        break

# When everything done, release the capture
vcap.release()
cv2.destroyAllWindows()
print("Video stop")