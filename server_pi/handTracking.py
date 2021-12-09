import cv2
import mediapipe as mp
import time
import socket
import sys

width = 400
height = 300
wheel_thickness = 30
out_radius = 130
inner_radius = out_radius - wheel_thickness
center = (width/2,height/2)


class handTracking:
    def __init__(self,cameraID):
        #========================================================
        #                                                       |
        #   Socket initializing                                 |
        #                                                       |
        #========================================================

        #create a udp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #server_address=('192.168.0.115',8888)
        server_address=('127.0.0.1',8888)
        #default
        #message = b'No point tracked'


        #========================================================
        #                                                       |
        #   Camera initializing                                 |
        #                                                       |
        #========================================================
        cap = cv2.VideoCapture(cameraID)
        cap.set(3,width)
        cap.set(4,height)
        cap.set(cv2.CAP_PROP_FPS,5)

        mpHands = mp.solutions.hands
        hands = mpHands.Hands(static_image_mode=False,
                            max_num_hands=2,
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5)
        mpDraw = mp.solutions.drawing_utils

        pTime = 0
        cTime = 0


        #========================================================
        #                                                       |
        #   Main Loop                                           |
        #                                                       |
        #========================================================
        while True:
            success, img2 = cap.read()
            h, w, c = img2.shape
            fx = width/2
            fy = height/2
            outRadSq = out_radius*out_radius
            inRadSq = inner_radius*inner_radius
            good_points = list()

            imgRGB = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            results = hands.process(imgRGB)
            sendLs = [1,1,0] 

            #print(results.multi_hand_landmarks)
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    for id, lm in enumerate(handLms.landmark):
                        #print(id,lm)
                        cx, cy = int(lm.x *w), int(lm.y*h)
                        
                        if abs(cx-fx)**2 + abs(cy-fy)**2 < outRadSq and abs(cx-fx)**2 + abs(cy-fy)**2 > inRadSq:
                            good_points.append([cx , cy])
                            #print(good_points)
                            print("number of Good point is",len(good_points))
                            
                            #sendLs[2] = 2.5 * len(good_points)
                            score = 0
                            if len(good_points) <= 10:
                                score += len(good_points) * 4 
                                
                            elif len(good_points) > 10 and len(good_points) <= 30:
                                score = 40 + (len(good_points)-10)*3
                            
                            elif len(good_points) > 30:
                                score = 100
                                

                            sendLs[2] = score  
                        
                        #points on hands
                        cv2.circle(img2, (cx,cy), 3, (255,0,255), cv2.FILLED)

                    mpDraw.draw_landmarks(img2, handLms, mpHands.HAND_CONNECTIONS)
                    if len(good_points) > 10:   print("safe drive")
                    else:print("unsafe drive")

            cTime = time.time()
            fps = 1/(cTime-pTime)
            pTime = cTime

            cv2.circle(img2, (200,150), out_radius,(0,0,255),2)
            cv2.circle(img2, (200,150), inner_radius,(0,0,255),2)
            cv2.putText(img2,str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
            cv2.imshow("Image2", img2)
            cv2.waitKey(1)
            
            #send data
            message_s = str(sendLs).encode() 
            #print('sending {!r}'.format(message_s))
            sent = sock.sendto(message_s, server_address)
