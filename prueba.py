import pandas as pd
import cv2
import time
from imagesearch import imagesearch, imagesearcharea
from analisis_y_estrategia import engulfing
import pyautogui
import random
import psutil
from multiprocessing import Process
from ExtraccionDatos10s import extraccion_10s_continua
import os
def r(num, rand):
    return num + rand * random.random()


'''
click on the center of an image with a bit of random.
eg, if an image is 100*100 with an offset of 5 it may click at 52,50 the first time and then 55,53 etc
Usefull to avoid anti-bot monitoring while staying precise.
this function doesn't search for the image, it's only ment for easy clicking on the images.
input :
image : path to the image file (see opencv imread for supported types)
pos : array containing the position of the top left corner of the image [x,y]
action : button of the mouse to activate : "left" "right" "middle", see pyautogui.click documentation for more info
time : time taken for the mouse to move from where it was to the new position
'''


def click_image(image, pos, action, timestamp, offset=5):
    img = cv2.imread(image)
    height, width, channels = img.shape
    pyautogui.moveTo(pos[0] + r(width / 2, offset), pos[1] + r(height / 2, offset),
                     timestamp)
    pyautogui.click(button=action)

class dinero_invertido:
    def __init__(self, monto):
        self.monto = monto


if __name__ == "__main__":
    par = "EUR/USD"
    tiempo = "10"
    monto = "1.50"
    pyautogui.doubleClick(x=685, y=540)
    pyautogui.doubleClick(x=685, y=540)
    time.sleep(0.1)
    pyautogui.keyDown(tiempo[0])
    try:
        pyautogui.keyDown(tiempo[1])
    except:
        pass
    time.sleep(2)
    click_image("imagen compra.jpg", (1089, 630), "left", 0.05)
    click_image("imagen compra.jpg", (1089, 630), "left", 0.05)
    time.sleep(4)
    click_image("x.jpg", (1388, 415), "left", 0.05)