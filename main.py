#print("importing keras...",end = '')
#import keras
#print("done")
print("importing modules...",end = '')
import numpy as np
import cv2
import mediapipe as mp
import pyautogui as pg
import time
print("done")
print("waking mmcat up...",end = '')
from mmcat import mouseModeCAT
print("done")
print("waking kmcat up...",end = '')
from kmcat import keyboardModeCAT
print("done")
print()

#print("loading EYES...",end = '')
#PATH = "C:/Users/JOOWAN/Desktop/jonghab/gifted/korea/projects/re_CAT_dataset"
#model = keras.models.load_model(PATH+'/EYESOFCAT.h5')
#IDX = [x for x in range(0,16)] + [y for y in range(24,32)]
#print("done")
#print()

pg.PAUSE = 0
#pg.FAILSAFE = 0

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def create_dimage(h, w, d):
    image = np.zeros((h, w,  d), np.uint8)
    color = tuple(reversed((0,0,0)))
    image[:] = color
    return image

class CAT:
    hands = mp_hands.Hands(False,max_num_hands=2,min_detection_confidence=0.5,min_tracking_confidence=0.5)
    k_img = cv2.imread("KEYBOARD.png",cv2.IMREAD_COLOR)

    def __init__(self,i_shape):
        self.cus_bef = [-1,-1]
        self.cus_cur = [-1,-1]
        self.finger = [[[0,0],[0,0],[0,0],[0,0],[0,0]],[[0,0],[0,0],[0,0],[0,0],[0,0]]]
        self.shape = [0,0]
        self.stdp = [[-1,-1],[-1,-1]]
        self.image_shape = i_shape
        self.dimage = create_dimage(self.image_shape[0],self.image_shape[1],self.image_shape[2])
        self.Bimage = self.dimage.copy()
        self.mode = "sleeping"   #3가지 모드
        # mode 1 : "mouse" - 기존의 CAT의 기능인 마우스 모드(왼손 - 감도 조절)
        # mode 2 : "keyboard" - 왼손과 오른손의 조합으로 키를 입력하는 모드
        # mode 0 : "sleeping" - 대기 상태, 모드 변경 기능
        #                       모든 모드에서 오른손과 왼손을 모두 주먹쥐면 이 모드로 변경
        #                       모드 변경을 위해 반드시 거쳐야 하는 통로
        self.mmcat = mouseModeCAT()
        self.kmcat = keyboardModeCAT()

        self.k_img = cv2.resize(CAT.k_img, dsize = (self.kmcat.w,self.kmcat.h), interpolation=cv2.INTER_AREA)

    def action(self,fings):
        if self.shape == [31,31]:
            self.mode = "sleeping"

        if self.mode == "mouse":
            #mmcat에 전달할 값 리스트 생성
            pfm = (fings[1][1], self.stdp[1])
            
            self.mmcat.action(self.shape,pfm)

        if self.mode == "keyboard":
            #배경에 키보드 보이기
            h, w = self.kmcat.h, self.kmcat.w
            self.k_img = cv2.resize(CAT.k_img, dsize = (w,h), interpolation=cv2.INTER_AREA)
            
            h_c = self.kmcat.h_c
            w_c = self.kmcat.w_c
            roi = self.Bimage[h_c:h_c+h, w_c:w_c+w]

            mask = cv2.cvtColor(self.k_img, cv2.COLOR_BGR2GRAY)
            mask[mask[:]==255]=0
            mask[mask[:]>0]=255

            mask_inv = cv2.bitwise_not(mask)
            roi_fg = cv2.bitwise_and(self.k_img, self.k_img, mask=mask)
            roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

            dst = cv2.add(roi_fg, roi_bg)

            self.Bimage[h_c:h_c+h, w_c:w_c+w] = dst
            #키보드 액션
            #kmcat에 전달할 값 리스트 생성
            a = int(fings[0][1][0]*(self.image_shape[1]/100))
            b = int(fings[1][1][0]*(self.image_shape[1]/100))
            c = int(fings[0][1][1]*(self.image_shape[0]/100))
            d = int(fings[1][1][1]*(self.image_shape[0]/100))

            pfk = ((a,c),(b,d),self.image_shape)

            self.kmcat.action(self.shape,pfk)
            self.Bimage = cv2.circle(self.Bimage, (w_c,h_c), self.kmcat.rarr[0], (255,0,255), -1)
            self.Bimage = cv2.circle(self.Bimage, (w_c+w,h_c+h), self.kmcat.rarr[1], (255,0,255), -1)
            self.Bimage = cv2.circle(self.Bimage, (a,c), 5, (0,255,0), -1)
            self.Bimage = cv2.circle(self.Bimage, (b,d), 5, (0,255,0), -1)
            
        if self.mode == "sleeping":
            if self.shape == [29,29]:
                self.mode = "mouse"
            if self.shape == [25,25]:
                self.mode = "keyboard"
                
    def operate(self,video):
        self.Bimage = self.dimage.copy()
        
        image = cv2.cvtColor(cv2.flip(video, 1), cv2.COLOR_BGR2RGB)
        results = CAT.hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            hands_type_d = []
            for idx, hand_handedness in enumerate(results.multi_handedness):
                hands_type_d.append((hand_handedness.classification[0].label == "Right"))
            hands_type_d = hands_type_d[:2]

            self.shape = [0,0]
            is_folded = [[],[]]
            idx = 0
            for hls in results.multi_hand_landmarks:
                idx_real = hands_type_d[idx]
                
                self.finger[idx_real] = [(hls.landmark[4].x * 100, hls.landmark[4].y * 100),
                          (hls.landmark[8].x * 100, hls.landmark[8].y * 100),
                          (hls.landmark[12].x * 100, hls.landmark[12].y * 100),
                          (hls.landmark[16].x * 100, hls.landmark[16].y * 100),
                          (hls.landmark[20].x * 100, hls.landmark[20].y * 100)]
                discr = [(hls.landmark[2].x * 100, hls.landmark[2].y * 100),
                          (hls.landmark[6].x * 100, hls.landmark[6].y * 100),
                          (hls.landmark[10].x * 100, hls.landmark[10].y * 100),
                          (hls.landmark[14].x * 100, hls.landmark[14].y * 100),
                          (hls.landmark[17].x * 100, hls.landmark[17].y * 100)]

                is_folded[idx_real] = [self.finger[idx_real][0][0] > discr[0][0],
                             (self.finger[idx_real][1][1] > discr[1][1]),
                             (self.finger[idx_real][2][1] > discr[2][1]),
                             (self.finger[idx_real][3][1] > discr[3][1]),
                             (self.finger[idx_real][4][1] > discr[4][1])]
                
                if not idx_real:
                    is_folded[idx_real][0] = not is_folded[idx_real][0]

                self.shape[idx_real] = is_folded[idx_real][0]*1 + is_folded[idx_real][1]*2 + is_folded[idx_real][2]*4 + is_folded[idx_real][3]*8 + is_folded[idx_real][4]*16
                #hls_x = []
                #hls_y = []
                #hls_z = []
                a_x = hls.landmark[0].x
                a_y = hls.landmark[0].y
                #if hands_type_d[idx]:
                #    for j in range(1,21):
                #        hls_x.append(hls.landmark[j].x - a_x)
                #        hls_y.append(hls.landmark[j].y - a_y)
                #        hls_z.append(hls.landmark[j].z)
                #else:
                #    for j in range(1,21):
                #        hls_x.append(a_x - hls.landmark[j].x)
                #        hls_y.append(a_y - hls.landmark[j].y)
                #        hls_z.append(hls.landmark[j].z)
                #T = hls_x + hls_y + hls_z
                #self.shape[idx_real] = IDX[np.argmax(model.predict([T],verbose = None), axis=1)[0]]

                self.stdp[idx_real] = (a_x * 100, a_y * 100)

                mp_drawing.draw_landmarks(self.Bimage, hls, mp_hands.HAND_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(255,255,255), thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=(30,30,250) if idx_real else (250,30,30), thickness=2, circle_radius=2))
                idx = 1
                
            cv2.putText(self.Bimage, text='mode : %s  shape:(%d,%d)' % (self.mode,self.shape[0],self.shape[1]),
                        org=(10, 30),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,color=(255,255,255), thickness=2)
            
        self.action(self.finger)
        self.Bimage = cv2.pyrUp(self.Bimage)
        cv2.imshow('CAT', self.Bimage)

    def stop(self):
        cv2.destroyAllWindows()
        del self

    def __del__(self):
        print("Thank you for using CAT!!!")

#############################################################################################################################################

print("connecting cap...",end = '')
cap = cv2.VideoCapture(0)
print("done")
print()

global cat
print("CAT woke up")

while cap.isOpened():
    success, image = cap.read()
    if success:
        cat = CAT(image.shape)
        break

while cap.isOpened():
    success, video = cap.read()
    if not success :
        continue
    cat.operate(video)
    if cv2.waitKey(1) == 27 and cat.mode == "sleeping":
        cat.stop()
        break

cap.release()
del(cat)


time.sleep(2)
