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
from estrategia6 import chequear_estrategia_6


class CronometroEjecucionModulo:
    def __init__(self):
        self.tiempo_de_espera_minutos = Value('i', 0)

    def retornar_cronometro(self):
        return self.tiempo_de_espera_minutos.value

    # Este método siempre se debe de ejecutar a través de un subproceso
    def comenzar_cronometro(self, tiempo_de_espera_minutos):
        self.tiempo_de_espera_minutos.value = tiempo_de_espera_minutos
        print("comienza a correr cronometro")
        time.sleep(int(tiempo_de_espera_minutos) * 60)
        self.tiempo_de_espera_minutos.value = 0


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
    imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 690, 1250, 770)
    print(imagen_ver_compra)



