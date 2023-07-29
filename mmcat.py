import math
from pynput.mouse import Button, Controller
import pyautogui as pg

class RemoteMouse:
    def __init__(self):
        self.mouse = Controller()

    def getPosition(self):
        return self.mouse.position

    def setPos(self, xPos, yPos):
        self.mouse.position = (xPos, yPos)
    def movePos(self, xPos, yPos):
        self.mouse.move(xPos, yPos)

    def click(self):
        self.mouse.click(Button.left)
    def doubleClick(self):
        self.mouse.click(Button.left, 2)
    def clickRight(self):
        self.mouse.click(Button.right)
    
    def down(self):
        self.mouse.press(Button.left)
    def up(self):
        self.mouse.release(Button.left)

class mouseModeCAT:
    SENSE = [0,1,2,4,6]
    def __init__(self):
        self.Rclicking = False
        self.Dclicking = False
        self.mouse = RemoteMouse()
        self.sense = 0 #왼손 숫자로 감도 조절(방식 : 카운트식)
        self.cus_bef = [-1,-1]
        self.cus_cur = [-1,-1]
        self.cus_dif = [0,0]
        self.R_zero_bef = [-1,-1]
        
    def act_move(self,cR_x,cR_y):
        self.cus_cur = [cR_x, cR_y]
        if self.cus_bef == [-1,-1]: self.cus_bef = self.cus_cur
        self.cus_dif = [self.cus_cur[0]-self.cus_bef[0], self.cus_cur[1]-self.cus_bef[1]]

        moveX = math.sqrt(pow(abs(self.cus_dif[0]*3),3))*(1 if self.cus_dif[0]>0 else -1)
        moveY = math.sqrt(pow(abs(self.cus_dif[1]*3),3))*(1 if self.cus_dif[1]>0 else -1)
        #moveX = (self.cus_dif[0])
        #moveY = (self.cus_dif[1])
        
        return moveX,moveY

    def act_subMove(self,cR_x,cR_y):
        self.cus_cur = [cR_x, cR_y]
        if self.cus_bef == [-1,-1]: self.cus_bef = self.cus_cur
        self.cus_dif = [self.cus_cur[0]-self.cus_bef[0], self.cus_cur[1]-self.cus_bef[1]]
        #if abs(self.cus_dif[0])<0.3 : self.cus_dif[0] = self.cus_dif[0] ** 2 *(1 if self.cus_dif[0]>0 else -1)
        #if abs(self.cus_dif[1])<0.3 : self.cus_dif[1] = self.cus_dif[1] ** 2 *(1 if self.cus_dif[1]>0 else -1)
        #moveX = mouseModeCAT.SENSE[self.sense] * self.cus_dif[0]
        #moveY = mouseModeCAT.SENSE[self.sense] * self.cus_dif[1]
        moveX = mouseModeCAT.SENSE[self.sense] * math.sqrt(pow(abs(self.cus_dif[0]*3),3))*(1 if self.cus_dif[0]>0 else -1)
        moveY = mouseModeCAT.SENSE[self.sense] * math.sqrt(pow(abs(self.cus_dif[1]*3),3))*(1 if self.cus_dif[1]>0 else -1)
        self.mouse.movePos(moveX,moveY)
        self.cus_bef = [-1,-1]
        
    def act_Rclick(self):
        if not self.Rclicking :
            self.Rclicking = True
            self.mouse.clickRight()

    def act_Dclick(self):
        if not self.Dclicking :
            self.Dclicking = True
            self.mouse.doubleClick()

    def act_scroll(self,zero_y):
        R_zero_ydif = zero_y-self.R_zero_bef[1]
        if abs(R_zero_ydif) < 0.3 : R_zero_ydif = 0
        
        moveY = self.sense * math.sqrt(pow(abs(R_zero_ydif*3),3))*(1 if R_zero_ydif>0 else -1)
        
        pg.scroll((-1)*int(moveY))

    def action(self,sh,pfm):
        if sh[0] == 31 or sh[0] == 0 : self.sense = 0
        elif sh[0] == 29 : self.sense = 1
        elif sh[0] == 25 : self.sense = 2
        elif sh[0] == 24 or sh[0] == 17: self.sense = 3
        elif sh[0] == 1 : self.sense = 4
        
        if sh[1] == 25 :
            self.act_subMove(pfm[0][0],pfm[0][1])
            self.mouse.down()
        else :
            self.mouse.up()
            if sh[1] == 24 :
                self.act_subMove(pfm[0][0],pfm[0][1])
            else : self.cus_bef = [-1,-1]
        
        if sh[1] == 9 : self.act_Dclick()
        else : self.Dclicking = False
        
        if sh[1] == 28 : self.act_Rclick()
        else : self.Rclicking = False
        
        if sh[1] == 12 : self.act_scroll(pfm[1][1])

        self.cus_bef = (pfm[0][0], pfm[0][1])
        self.R_zero_bef = (pfm[1][0], pfm[1][1])
