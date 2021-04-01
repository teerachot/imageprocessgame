# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import random
import threading

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())
# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
blueLower = np.array([110,50,50])
blueUpper = np.array([130,255,255])

# redLower = np.array([])
# redUpper = np.array([])

# greenLower = np.array([])
# greenUpper = np.array([])

pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# allow the camera or video file to warm up
time.sleep(2.0)
draw = 1
point = 0
x_1 = 0
y_1 = 0
timer = 0
timeCount = 0
endgame = True

def sedEnd():
    endgame = True
    
# keep looping
while True:
    # while timer:
    #     time.sleep(1)
    #     timer -= 1
    
  
    # grab the current frame
    frame = vs.read()

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, blueLower, blueUpper)
    mask = cv2.erode(mask, None, iterations=4)
    mask = cv2.dilate(mask, None, iterations=4)
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

   

    if(draw==1):
        x_1 = random.randint(100,400)
        y_1 = random.randint(50,400)
        draw = 0
    if(endgame==False):
        timeCount = int(time.time()-timer)
        cv2.circle(frame, (int(x_1), int(y_1)), int(30),(0, 0, 255), 2)
    

    

        

    

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))



        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            print("frame {}".format(frame.shape))
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
         
        comparm_x = [x_1 - 30,x_1+30]
        comparm_y = [y_1 - 30,y_1 + 30] 
        x_c, y_c = center
    
   
        if((comparm_x[0]< x_c and comparm_x[1] > x_c) and (comparm_y[0] < y_c and  comparm_y[1] > y_c)):
            point = point +1
            draw = 1


    # update the points queue
    pts.appendleft(center)
    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    # frame = cv2.flip(frame,1)
    if endgame == True and timer == 0:
         cv2.putText(frame,"Start",(180,250),cv2.FONT_HERSHEY_SIMPLEX,2,(255,50,200),2)

    elif endgame == True:
         cv2.putText(frame,"Try Agian",(180,250),cv2.FONT_HERSHEY_SIMPLEX,2,(255,50,200),2)    
   
    cv2.putText(frame,"point: {}".format(point),(400,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
    cv2.putText(frame,"time: {}".format(timeCount),(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
    cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN) 
    cv2.setWindowProperty("Frame",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
 
    if timeCount >=30:
        endgame = True

    if key == ord("r"):
        timer = time.time()
        endgame = False
        point = 0

    if key == ord("s"):
        timer = time.time()
        endgame = False


    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
