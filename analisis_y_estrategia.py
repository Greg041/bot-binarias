import cv2
import numpy as np
import pyautogui
import random
import time


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


def ejecucion(signal):
    if signal == "compra":
        click_image("horario.jpg", (1805, 132), "left", 0.05)
        time.sleep(0.1)
        click_image("1minuto.jpg", (1517, 220), "left", 0.05)
        click_image("imagen compra.jpg", (1801, 379), "left", 0.05)
    elif signal == "venta":
        click_image("horario.jpg", (1805, 132), "left", 0.05)
        time.sleep(0.1)
        click_image("1minuto.jpg", (1517, 220), "left", 0.05)
        click_image("imagen venta.jpg", (1804, 513), "left", 0.05)


def analisis_y_estrategia(ohlc_5min):
