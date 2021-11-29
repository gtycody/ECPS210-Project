import cv2
import numpy as np
import mediapipe as mp
import time
import socket
import sys

def x_element(elem):
    return elem[0]

def y_element(elem):
    return elem[1]


def draw_annotation_box(img, rotation_vector, translation_vector, camera_matrix, color=(255, 255, 0), line_width=2):
    """Draw a 3D box as annotation of pose"""
    point_3d = []
    dist_coeffs = np.zeros((4,1))

    point_3d = [(-1,-1,0),\
                (-1,1,0),\
                (1,1,0),\
                (1,-1,0),\
                (-1,-1,0)]


    front_size = img.shape[1]
    front_depth = front_size*2
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d.append((-front_size, front_size, front_depth))
    point_3d.append((front_size, front_size, front_depth))
    point_3d.append((front_size, -front_size, front_depth))
    point_3d.append((-front_size, -front_size, front_depth))
    point_3d = np.array(point_3d, dtype=np.float).reshape(-1, 3)

    # Map to 2d img points
    (point_2d, _) = cv2.projectPoints(point_3d,
                                    rotation_vector,
                                    translation_vector,
                                    camera_matrix,
                                    dist_coeffs)
    point_2d = np.int32(point_2d.reshape(-1, 2))
    

    # Draw all the lines
    cv2.polylines(img, [point_2d], True, color, line_width, cv2.LINE_AA)
    k = (point_2d[5] + point_2d[8])//2
    cv2.line(img, tuple(point_2d[1]), tuple(
        point_2d[6]), color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[2]), tuple(
        point_2d[7]), color, line_width, cv2.LINE_AA)
    cv2.line(img, tuple(point_2d[3]), tuple(
        point_2d[8]), color, line_width, cv2.LINE_AA)
    
    return(point_2d[2], k)


    
class headTracking():
    def __init__(self,cameraID):
        #========================================================
        #                                                       |
        #   Socket initializing                                 |
        #                                                       |
        #========================================================

        #create a udp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #server_address=('192.168.0.115',8888)
        server_address=('192.168.0.238',8888)
        message = b'This is the message.'


        #========================================================
        #                                                       |
        #   Camera initializing                                 |
        #                                                       |
        #========================================================
        #set frame size
        font = cv2.FONT_HERSHEY_SIMPLEX 
        cap = cv2.VideoCapture(cameraID)
        cap.set(3,400)
        cap.set(4,300)
        cap.set(cv2.CAP_PROP_FPS,5)

        mpDraw = mp.solutions.drawing_utils
        mpFaceMesh = mp.solutions.face_mesh
        faceMesh = mpFaceMesh.FaceMesh(max_num_faces=1, min_detection_confidence=.9, min_tracking_confidence=.01)
        drawSpec = mpDraw.DrawingSpec(0,1,1)

        success, img = cap.read()
        height, width = img.shape[:2]
        size = img.shape
        print("size",size)

        # 3D model points.
        face3Dmodel = np.array([
            (0.0, 0.0, 0.0),  # Nose tip
            (0.0, -330.0, -65.0),  # Chin
            (-225.0, 170.0, -135.0),  # Left eye left corner
            (225.0, 170.0, -135.0),  # Right eye right corne
            (-150.0, -150.0, -125.0),  # Left Mouth corner
            (150.0, -150.0, -125.0)  # Right mouth corner
        ],dtype=np.float64)


        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        focal_length = size[1]
        center = (size[1] / 2, size[0] / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]], dtype="double"
        )
        faceXY = []


        #========================================================
        #                                                       |
        #   Main Loop                                           |
        #                                                       |
        #========================================================
        while True:
            success, img = cap.read()
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = faceMesh.process(imgRGB)
            if results.multi_face_landmarks:                                            # if faces found
                dist=[]
                for faceNum, faceLms in enumerate(results.multi_face_landmarks):                            # loop through all matches
                    mpDraw.draw_landmarks(img, faceLms, landmark_drawing_spec=drawSpec) # draw every match
                    faceXY = []
                    for id,lm in enumerate(faceLms.landmark):                           # loop over all land marks of one face
                        ih, iw, _ = img.shape
                        x,y = int(lm.x*iw), int(lm.y*ih)
                        # print(lm)
                        faceXY.append((x, y))                                           # put all xy points in neat array
                    image_points = np.array([
                        faceXY[1],      # "nose"
                        faceXY[152],    # "chin"
                        faceXY[226],    # "left eye"
                        faceXY[446],    # "right eye"
                        faceXY[57],     # "left mouth"
                        faceXY[287]     # "right mouth"
                    ], dtype="double")
                    for i in image_points:
                        cv2.circle(img,(int(i[0]),int(i[1])),4,(255,0,0),-1)
                    
                    maxXY = max(faceXY, key=x_element)[0], max(faceXY, key=y_element)[1]
                    minXY = min(faceXY, key=x_element)[0], min(faceXY, key=y_element)[1]

                    xcenter = (maxXY[0] + minXY[0]) / 2
                    ycenter = (maxXY[1] + minXY[1]) / 2

                    dist.append((faceNum, (int(((xcenter-width/2)**2+(ycenter-height/2)**2)**.4)), maxXY, minXY))     # faceID, distance, maxXY, minXY

                    #print(image_points)

                    (success, rotation_vector, translation_vector) = cv2.solvePnP(face3Dmodel, image_points,  camera_matrix, dist_coeffs)
                    (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)

                    p1 = (int(image_points[0][0]), int(image_points[0][1]))
                    p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
                    x1, x2 = draw_annotation_box(img, rotation_vector, translation_vector, camera_matrix)
                    
                    print("rotation:",rotation_vector)
                    if rotation_vector[1] > 2 or rotation_vector[1]< -2:
                        print("unsafe")
                        message = b'unsafe'
                    elif rotation_vector[0] < -3.30 or rotation_vector[0] > -2.70:
                        print("unsafe2")
                        message = b'unsafe2'
                    else:
                        print("safe")
                        message = b'safe'

                    # print("p1,p2=",p1,p2)

                    cv2.line(img, p1, p2, (255, 0, 0), 2)
                    cv2.line(img, tuple(x1), tuple(x2), (255, 255, 0), 2)
                        
                dist.sort(key=y_element)
                # print(dist)

                for i,faceLms in enumerate(results.multi_face_landmarks):
                    if i == 0:
                        cv2.rectangle(img,dist[i][2],dist[i][3],(0,255,0),2)
                    else:
                        cv2.rectangle(img, dist[i][2], dist[i][3], (0, 0, 255), 2)

            cv2.imshow("Image", img)
            cv2.waitKey(1)
            #send data
            print('sending {!r}'.format(message))
            sent = sock.sendto(message, server_address)