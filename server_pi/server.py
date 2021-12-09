import socket
import sys
import time
import cv2

# tags in one udp package
# ID            -int
# True/False    -0/1
# Score         -int
# Sample udp:   1,0,40

# tags when server received
# time stamp    -time
# Sample output 1,0,40,2021-12-1 18:49:50

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Bind the socket to the port
server_address = ('0.0.0.0',8888)
#print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

score_a_ls = list() 
score_b_ls = list()
score_c_ls = list()

def ret_avg(inputLs,num):
    if len(inputLs) > num:
        sum = 0
        for i in range(1,num+1):
            sum += int(inputLs[-i])
        return sum/num
    else:
        pass

last_stamp_t = time.time()
while True:
    stamp_t = time.time()
    #print("\n waiting to receive message\n")
    data, address = sock.recvfrom(4096)
    # print('received {} bytes from {}'.format(len(data),address),data)
    capStr = str(data.decode("utf-8"))
    capLs = capStr[1:-1].split(',')
    #print(capLs,capLs[2],capLs[0])
    #print(capLs[0] == 1)
    if capLs[0] == '1':
        score_a_ls.append(capLs[2])

    elif capLs[0] == '2':
        score_b_ls.append(capLs[2]) 

    elif capLs[0] == '3':
        score_c_ls.append(capLs[2])
    
    if stamp_t - last_stamp_t > 5:
        hand_s = ret_avg(score_a_ls,20)
        head_s = ret_avg(score_b_ls,20)
        obj_s = ret_avg(score_c_ls,20)
        print("Hannnnnd score: ",hand_s)
        print("Head score：",head_s)
        print("Object socre:",obj_s)
        if obj_s:
            overall_score = (hand_s*0.33) + (head_s*0.49) + (obj_s*0.18)
            print("****Overall score:****:\n", overall_score,"\n")
            background = cv2.imread("black.png", flags=cv2.IMREAD_COLOR)
            cv2.putText(background,"Safety Socre", (100,130), cv2.FONT_HERSHEY_PLAIN,  3, (255,0,255), 2)
            cv2.putText(background,str(int(overall_score)), (100,370), cv2.FONT_HERSHEY_PLAIN, 20, (255,0,255), 5)
            cv2.imshow("Score Image", background)
            cv2.waitKey(1)
        