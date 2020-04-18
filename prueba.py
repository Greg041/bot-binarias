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

def otro_mensaje():
    while True:
        print("comoestas")
        time.sleep(1)

def click_image():
    print("hola")
    time.sleep(3)
    click_image()


if __name__ == "__main__":
    proceso_10s = Process(target=click_image, name="extraccion")
    proceso_10s.start()
    otro_mensaje()