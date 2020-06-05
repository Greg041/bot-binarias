import pandas as pd
import cv2
import time
from imagesearch import imagesearch, imagesearcharea
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
class sumar:
    def __init__(self):
        self.numero = 0

def sumar_numero(objeto, valor_a_retornar):
    while True:
        print(objeto.numero)
        objeto.numero += 1
        valor_a_retornar[1] = True
        time.sleep(1)


if __name__ == "__main__":
    objeto_sumar = sumar()
    manager = Manager().Array('b', [True, False, True])
    proceso = Process(target=sumar_numero, args=(objeto_sumar, manager))
    proceso.start()
    time.sleep(20)
    print(manager[:])

