# this is the main program of dangerous driving
import cv2
import numpy as np
import mediapipe as mp
import time
import threading
from multiprocessing import Process
from handTracking import handTracking
from headTracking import headTracking


#create objects of both tracking
def createHandTracking(camID):
    handT = handTracking(camID)

def createHeadTracking(camID):
    headT = headTracking(camID)

p1=Process(target=createHandTracking,args=(0,))
p2=Process(target=createHeadTracking,args=(2,))

p1.start()
p2.start()
p1.join()
p2.join()


