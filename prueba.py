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
from prueba2 import cambio_de_monto

class dinero_invertido:
    def __init__(self, monto):
        self.monto = monto


if __name__ == "__main__":
    apuesta = dinero_invertido("1.45")
    print(apuesta.monto)
    cambio_de_monto(apuesta, "aumentar")
    print(apuesta.monto)
    cambio_de_monto(apuesta, "aumentar")
    print(apuesta.monto)
    cambio_de_monto(apuesta, "aumentar")
    print(apuesta.monto)
    cambio_de_monto(apuesta, "disminuir")
    print(apuesta.monto)
    cambio_de_monto(apuesta, "aumentar")
    print(apuesta.monto)
    cambio_de_monto(apuesta, "disminuir")
    print(apuesta.monto)
    cambio_de_monto(apuesta, "disminuir")
    print(apuesta.monto)
    cambio_de_monto(apuesta, "disminuir")
    print(apuesta.monto)
    cambio_de_monto(apuesta, "disminuir")
    print(apuesta.monto)