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


def click_image(image, pos, action, timestamp, offset=5):
    img = cv2.imread(image)
    height, width, channels = img.shape
    pyautogui.moveTo(pos[0] + r(width / 2, offset), pos[1] + r(height / 2, offset),
                     timestamp)
    pyautogui.click(button=action)



if __name__ == "__main__":
    par = "EUR_JPY"
    click_image("par.jpg", (489, 228), "left", 0.05)
    time.sleep(0.3)
    pyautogui.leftClick(x=515, y=242)
    pyautogui.keyDown(par[0])
    pyautogui.keyDown(par[1])
    pyautogui.keyDown(par[2])
    pyautogui.keyDown("/")
    pyautogui.keyDown(par[4])
    pyautogui.keyDown(par[5])
    pyautogui.keyDown(par[6])
    time.sleep(0.3)
    click_image("par_sel.jpg", (635, 356), "left", 0.05)