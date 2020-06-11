import cv2
import pyautogui
import random
import time
import winsound
import numpy as np
'''
grabs a region (topx, topy, bottomx, bottomy)
to the tuple (topx, topy, width, height)
input : a tuple containing the 4 coordinates of the region to capture
output : a PIL image of the area selected.
'''


def region_grabber(region):
    x1 = region[0]
    y1 = region[1]
    width = region[2] - x1
    height = region[3] - y1
    return pyautogui.screenshot(region=(x1, y1, width, height))


def imagesearcharea(image, x1, y1, x2, y2, precision=0.8, im=None):
    if im is None:
        im = region_grabber(region=(x1, y1, x2, y2))
        # im.save('testarea.png') usefull for debugging purposes, this will save the captured region as "testarea.png"

    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc


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


def ejecucion(signal, par, tiempo, monto, array_de_precios):
    if signal != "":
        click_image("par.jpg", (489, 338), "left", 0.05)
        time.sleep(0.3)
        pyautogui.leftClick(x=504, y=375)
        pyautogui.keyDown(par[0])
        pyautogui.keyDown(par[1])
        pyautogui.keyDown(par[2])
        pyautogui.keyDown("/")
        pyautogui.keyDown(par[4])
        pyautogui.keyDown(par[5])
        pyautogui.keyDown(par[6])
        click_image("par_sel.jpg", (635, 490), "left", 0.05)
        time.sleep(1.5)
    if monto.monto is not None:
        pyautogui.doubleClick(x=710, y=600)
        pyautogui.doubleClick(x=710, y=600)
        try:
            pyautogui.keyDown(monto.monto[0])
            pyautogui.keyDown(monto.monto[1])
            pyautogui.keyDown(monto.monto[2])
            pyautogui.keyDown(monto.monto[3])
        except:
            pass
        time.sleep(1)
    if signal == "compra1":
        print("compra variacion 1")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        pyautogui.doubleClick(x=685, y=540)
        pyautogui.doubleClick(x=685, y=540)
        time.sleep(0.1)
        pyautogui.keyDown(tiempo[0])
        try:
            pyautogui.keyDown(tiempo[1])
        except:
            pass
        time.sleep(2)
        timeout = time.time() + 300
        precio_a_retornar = 0
        # Esperar a que el precio esté en la posición optima para ejecutar la operación y por un lapso de 5 minutos
        imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 715, 1250, 770)
        while imagen_ver_compra == [-1, -1]:
            click_image("x.jpg", (1388, 415), "left", 0.05)
            while array_de_precios[0] >= array_de_precios[3] or time.time() >= timeout:
                pass
                if time.time() >= timeout:
                    return 0
            click_image("imagen compra.jpg", (1089, 470), "left", 0.05)
            click_image("imagen compra.jpg", (1089, 470), "left", 0.05)
            precio_a_retornar = array_de_precios[0]
            winsound.Beep(440, 1000)
            time.sleep(4)
            imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 690, 1250, 770)
        click_image("x.jpg", (1388, 415), "left", 0.05)
        return precio_a_retornar
    elif signal == "compra2":
        print("compra variacion 2")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        pyautogui.doubleClick(x=685, y=540)
        pyautogui.doubleClick(x=685, y=540)
        time.sleep(0.1)
        pyautogui.keyDown(tiempo[0])
        try:
            pyautogui.keyDown(tiempo[1])
        except:
            pass
        time.sleep(2)
        timeout = time.time() + 300
        # Esperar a que el precio esté en la posición optima para ejecutar la operación y por un lapso de 5 minutos
        precio_a_retornar = array_de_precios[0]
        imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 690, 1250, 770)
        while imagen_ver_compra == [-1, -1]:
            click_image("x.jpg", (1388, 415), "left", 0.05)
            while array_de_precios[0] >= array_de_precios[2] or time.time() >= timeout:
                pass
                if time.time() >= timeout:
                    return 0
            click_image("imagen compra.jpg", (1089, 470), "left", 0.05)
            click_image("imagen compra.jpg", (1089, 470), "left", 0.05)
            precio_a_retornar = array_de_precios[0]
            winsound.Beep(440, 1000)
            time.sleep(4)
            imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 690, 1250, 770)
        click_image("x.jpg", (1388, 415), "left", 0.05)
        return precio_a_retornar
    elif signal == "venta1":
        print("venta variacion 1")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        pyautogui.doubleClick(x=685, y=540)
        pyautogui.doubleClick(x=685, y=540)
        time.sleep(0.1)
        pyautogui.keyDown(tiempo[0])
        try:
            pyautogui.keyDown(tiempo[1])
        except:
            pass
        time.sleep(2)
        timeout = time.time() + 300
        # Esperar a que el precio esté en la posición optima para ejecutar la operación y por un lapso de 5 minutos
        imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 690, 1250, 770)
        precio_a_retornar = array_de_precios[0]
        while imagen_ver_compra == [-1, -1]:
            click_image("x.jpg", (1388, 415), "left", 0.05)
            while array_de_precios[0] <= array_de_precios[4] or time.time() >= timeout:
                pass
                if time.time() >= timeout:
                    return 0
            click_image("imagen compra.jpg", (1089, 630), "left", 0.05)
            click_image("imagen compra.jpg", (1089, 630), "left", 0.05)
            precio_a_retornar = array_de_precios[0]
            winsound.Beep(440, 1000)
            time.sleep(4)
            imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 690, 1250, 770)
        click_image("x.jpg", (1388, 415), "left", 0.05)
        return precio_a_retornar
    elif signal == "venta2":
        print("venta variacion 2")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        pyautogui.doubleClick(x=685, y=540)
        pyautogui.doubleClick(x=685, y=540)
        time.sleep(0.1)
        pyautogui.keyDown(tiempo[0])
        try:
            pyautogui.keyDown(tiempo[1])
        except:
            pass
        time.sleep(2)
        timeout = time.time() + 300
        # Esperar a que el precio esté en la posición optima para ejecutar la operación y por un lapso de 5 minutos
        precio_a_retornar = array_de_precios[0]
        imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 715, 1250, 770)
        while imagen_ver_compra == [-1, -1]:
            click_image("x.jpg", (1388, 415), "left", 0.05)
            while array_de_precios[0] <= array_de_precios[1] or time.time() >= timeout:
                pass
                if time.time() >= timeout:
                    return 0
            click_image("imagen compra.jpg", (1089, 630), "left", 0.05)
            click_image("imagen compra.jpg", (1089, 630), "left", 0.05)
            precio_a_retornar = array_de_precios[0]
            winsound.Beep(440, 1000)
            time.sleep(4)
            imagen_ver_compra = imagesearcharea("imagen_ver_compra.jpg", 1130, 715, 1250, 770)
        click_image("x.jpg", (1388, 415), "left", 0.05)
        return precio_a_retornar