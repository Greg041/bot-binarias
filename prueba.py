import pandas as pd
import cv2
import time
from imagesearch import imagesearch, imagesearcharea
from analisis_y_estrategia import engulfing
import pyautogui
import random


def r(num, rand):
    return num + rand * random.random()


def click_image(image, pos, action, timestamp, offset=5):
    img = cv2.imread(image)
    height, width, channels = img.shape
    pyautogui.moveTo(pos[0] + r(width / 2, offset), pos[1] + r(height / 2, offset),
                     timestamp)
    pyautogui.click(button=action)


if __name__ == "__main__":
    click_image("par.jpg", (489, 228), "left", 0.05)
    time.sleep(0.3)
    pyautogui.leftClick(x=1072, y=265)
    pyautogui.leftClick(x=1072, y=265)
    pyautogui.leftClick(x=1072, y=265)
    pyautogui.leftClick(x=1072, y=265)
    pyautogui.leftClick(x=1072, y=265)
    click_image("par_eur_usd.jpg", (817, 455), "left", 0.05)
    time.sleep(1)
    pyautogui.doubleClick(x=685, y=403)
    pyautogui.doubleClick(x=685, y=403)
    time.sleep(0.1)
    pyautogui.keyDown('5')
    time.sleep(2)
    click_image("imagen compra.jpg", (1089, 347), "left", 0.05)
