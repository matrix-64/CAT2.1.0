import pyautogui as pg
import math

pg.PAUSE = 0
pg.FAILSAFE = 0

def distance(x1, y1, x2, y2):
    result = math.sqrt( math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    return result

class keyboardModeCAT:
    K_locs = []
    
    def __init__(self):
        #키 위치 파일 read
        input_layers = [2,3,4,5]
        not_a_key = ["tab","backspace","capslock","shift","shift","enter"]

        f = open("locs.txt", "r", encoding="utf-8")
        layer_level = 0
        for line in f:
            if line == "\n" : continue
            if line[0] == "<":
                keyboardModeCAT.K_locs.append([[],(int(line.split(' ')[4]),int(line.split(' ')[6]))])
                layer_level += 1
            else :
                l = [(line[:-1].split(' '))[x] for x in (0,2,4)]
                l[1], l[2] = int(l[1]), int(l[2])
                if layer_level in input_layers:
                    if l[0] in not_a_key :
                        l.append(False)
                    else :
                        l.append(True)
                else :
                    l.append(False)
                keyboardModeCAT.K_locs[-1][0].append(l)

        #인스턴스 변수 초기화
        self.rarr = [5,5]
        
        self.pressed_bef = []
        self.pressed = []

        self.pressing = set()
        self.pressing_bef = set()

        self.h = 240
        self.w = 544
        self.h_c = 64
        self.w_c = 48

    def what_is_this_key(self,x,y):
        for L in keyboardModeCAT.K_locs:
            if y > L[-1][0] and y < L[-1][1]:
                for keys in L[0]:
                    if x > keys[1] and x < keys[2]:
                        return (keys[0],keys[3])
        return None

    def convert2disc(self,pfk):
        a = (pfk[0][0]-self.w_c)*(1693 / self.w)
        b = (pfk[1][0]-self.w_c)*(1693 / self.w)
        c = (pfk[0][1]-self.h_c)*(676 / self.h)
        d = (pfk[1][1]-self.h_c)*(676 / self.h)

        return ((a,c),(b,d))
    
    def action(self,sh,pfk):
        #인식
        C = self.convert2disc(pfk)
        self.pressed = []
        self.pressing = set()

        if sh[0] != 29 :
            self.rarr[0] = 5
        if sh[1] != 29 :
            self.rarr[1] = 5
        if distance(0,0,C[0][0],C[0][1]) < 30 :
            self.rarr[0] = 10
        if distance(1693,676,C[1][0],C[1][1]) < 30 :
            self.rarr[1] = 10

        if sh[0] == 29:
            if self.rarr[0] == 10 :
                if pfk[0][1] + self.h < pfk[2][0] :
                    self.h_c = pfk[0][1]
                    if self.h_c < 0 : self.h_c = 0
                if pfk[0][0] + self.w < pfk[2][1] :
                    self.w_c = pfk[0][0]
                    if self.w_c < 0 : self.w_c = 0
            else :
                a = self.what_is_this_key(C[0][0],C[0][1])
                if a is not None :
                    self.pressed.append(a)
                
        if sh[1] == 29:
            if self.rarr[1] == 10 :
                if pfk[1][1] < pfk[2][0] and (pfk[1][1] - self.h_c) > 0:
                    self.h = int(pfk[1][1] - self.h_c)
                if pfk[1][0] < pfk[2][1] and (pfk[1][0] - self.w_c) > 0:
                    self.w = int(pfk[1][0] - self.w_c)
            else :
                b = self.what_is_this_key(C[1][0],C[1][1])
                if b is not None :
                    self.pressed.append(b)

        #입력
        for key in self.pressed :
            if key[1] :
                if not key in self.pressed_bef :
                    pg.write(key[0])
            else :
                self.pressing.add(key[0])
                if not key[0] in self.pressing_bef :
                    pg.keyDown(key[0])

        for key in list(self.pressing_bef - self.pressing) :
            pg.keyUp(key)
            
        self.pressed_bef = self.pressed
        self.pressing_bef = self.pressing

