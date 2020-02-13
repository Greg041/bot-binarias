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
    pyautogui.doubleClick(x=710, y=440)
    pyautogui.doubleClick(x=710, y=440)
    pyautogui.keyDown('3')
    pyautogui.keyDown('.')
    pyautogui.keyDown('1')
    pyautogui.keyDown('5')