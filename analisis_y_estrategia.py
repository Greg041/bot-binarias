import cv2
import pyautogui
import random
import time
from ADX import ADX
from RSI import RSI
import winsound


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
        click_image("horario.jpg", (1805, 132), "left", 0.05)
        time.sleep(0.1)
        click_image("2minutos.jpg", (1514, 242), "left", 0.05)
        click_image("imagen compra.jpg", (1801, 379), "left", 0.05)
        winsound.Beep(440, 1000)
    elif signal == "venta":
        click_image("horario.jpg", (1805, 132), "left", 0.05)
        time.sleep(0.1)
        click_image("1minuto.jpg", (1517, 220), "left", 0.05)
        click_image("imagen venta.jpg", (1804, 513), "left", 0.05)
        click_image("horario.jpg", (1805, 132), "left", 0.05)
        time.sleep(0.1)
        click_image("2minutos.jpg", (1514, 242), "left", 0.05)
        click_image("imagen venta.jpg", (1804, 513), "left", 0.05)
        winsound.Beep(440, 1000)


def analisis_y_estrategia(ohlc_1min, ohlc_5s, resistencia_max_5min, soporte_min_5min, resistencia_max_1min,
                          soporte_min_1min):
    rsi_28 = RSI(ohlc_5s, 28)
    rsi_14 = RSI(ohlc_5s, 14)
    print(rsi_28.iloc[-1], rsi_14.iloc[-1])
    if (rsi_28.iloc[-1] < 30.0 or rsi_28.iloc[-2] < 30.0) and (
            rsi_14.iloc[-2] < rsi_28.iloc[-2] and rsi_14.iloc[-1] > rsi_28.iloc[-1]) and \
            (ohlc_5s["c"].iloc[-2] < ohlc_5s["c"].iloc[-1]):
        adx_1min = ADX(ohlc_1min, 21)
        adx_5s = ADX(ohlc_5s, 14)
        if adx_1min.iloc[-1, 0] < 25.0 and (adx_1min.iloc[-1, 1] < 25.0 or
                                            adx_1min.iloc[-1, 1] < adx_1min.iloc[-2, 1]) \
                and (adx_5s.iloc[-1, 1] < adx_5s.iloc[-2, 1]) and (adx_5s.iloc[-1, 2] > adx_5s.iloc[-2, 2]):
            print("compra contratendencia")
            return "compra"
        else:
            return ""
    elif rsi_28.iloc[-1] > 70.0 and (ohlc_5s["c"].iloc[-2] < ohlc_5s["c"].iloc[-1]):
        adx_1min = ADX(ohlc_1min, 21)
        adx_5s = ADX(ohlc_5s, 14)
        if (adx_5s.iloc[-1, 0] > 25.0 and adx_5s.iloc[-2, 2] < adx_5s.iloc[-1, 2] > adx_5s.iloc[-1, 1]) and (
                adx_1min.iloc[-2, 2] < adx_1min.iloc[-2, 0] and
                adx_1min.iloc[-1, 2] > adx_1min.iloc[-1, 0]):
            if resistencia_max_5min > resistencia_max_1min > ohlc_5s["c"].iloc[-1]:
                print("compra a favor")
                return "compra"
            elif resistencia_max_1min > resistencia_max_5min > ohlc_5s["c"].iloc[-1]:
                print("compra a favor")
                return "compra"
            else:
                return ""
        else:
            return ""
    elif (rsi_28.iloc[-1] > 70.0 or rsi_28.iloc[-2] > 70.0) and (
            rsi_14.iloc[-2] > rsi_28.iloc[-2] and rsi_14.iloc[-1] < rsi_28.iloc[-1]) and \
            (ohlc_5s["c"].iloc[-2] > ohlc_5s["c"].iloc[-1]):
        adx_1min = ADX(ohlc_1min, 21)
        adx_5s = ADX(ohlc_5s, 14)
        if adx_1min.iloc[-1, 0] < 25.0 and (adx_1min.iloc[-1, 2] < 25.0 or
                                            adx_1min.iloc[-1, 2] < adx_1min.iloc[-2, 2]) and \
                (adx_5s.iloc[-1, 1] > adx_5s.iloc[-2, 1]) and (adx_5s.iloc[-1, 2] < adx_5s.iloc[-2, 2]):
            print("venta contratendencia")
            return "venta"
        else:
            return ""
    elif rsi_28.iloc[-1] < 30.0 and (ohlc_5s["c"].iloc[-2] > ohlc_5s["c"].iloc[-1]):
        adx_1min = ADX(ohlc_1min, 21)
        adx_5s = ADX(ohlc_5s, 14)
        if (adx_5s.iloc[-1, 0] > 25.0 and adx_5s.iloc[-2, 1] < adx_5s.iloc[-1, 1] > adx_5s.iloc[-1, 2]) and (
                adx_1min.iloc[-2, 1] < adx_1min.iloc[-2, 0] and
                adx_1min.iloc[-1, 1] > adx_1min.iloc[-1, 0]):
            if soporte_min_5min < soporte_min_1min < ohlc_5s["c"].iloc[-1]:
                print("venta a favor")
                return "venta"
            elif soporte_min_1min < soporte_min_5min < ohlc_5s["c"].iloc[-1]:
                print("venta a favor")
                return "venta"
            else:
                return ""
        else:
            return ""
    else:
        return ""
