import pandas as pd
import cv2
import time
from imagesearch import imagesearch, imagesearcharea, click_image
from analisis_y_estrategia import engulfing
import pyautogui
import random
import psutil
from multiprocessing import Process, Value, Array, Manager
import array
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


if __name__ == "__main__":
    imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 715, 1250, 770)
    while imagen_ver_compra == [-1, -1]:
        click_image("x.jpg", (1388, 415), "left", 0.05)
        while -1 >= 0:
            pass
        click_image("imagen compra.jpg", (1089, 470), "left", 0.05)
        click_image("imagen compra.jpg", (1089, 470), "left", 0.05)
        precio_a_retornar = 5
        time.sleep(4)
        imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 700, 1250, 770)
        print(imagen_ver_compra)
    click_image("x.jpg", (1388, 415), "left", 0.05)

