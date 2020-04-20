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


def ejecucion(signal, par, tiempo, monto):
    if signal != "":
        click_image("par.jpg", (489, 228), "left", 0.05)
        time.sleep(0.3)
        pyautogui.leftClick(x=504, y=242)
        pyautogui.keyDown(par[0])
        pyautogui.keyDown(par[1])
        pyautogui.keyDown(par[2])
        pyautogui.keyDown("/")
        pyautogui.keyDown(par[4])
        pyautogui.keyDown(par[5])
        pyautogui.keyDown(par[6])
        click_image("par_sel.jpg", (635, 356), "left", 0.05)
        time.sleep(1)
    if monto is not None:
        pyautogui.doubleClick(x=710, y=475)
        pyautogui.doubleClick(x=710, y=475)
        pyautogui.keyDown(monto[0])
        pyautogui.keyDown(monto[1])
        pyautogui.keyDown(monto[2])
        pyautogui.keyDown(monto[3])
        time.sleep(1)
    if signal == "comprac":
        print("compra contratendencia")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        pyautogui.doubleClick(x=685, y=415)
        pyautogui.doubleClick(x=685, y=415)
        time.sleep(0.1)
        pyautogui.keyDown(tiempo[0])
        try:
            pyautogui.keyDown(tiempo[1])
        except:
            pass
        time.sleep(2)
        click_image("imagen compra.jpg", (1089, 340), "left", 0.05)
        click_image("imagen compra.jpg", (1089, 340), "left", 0.05)
        #winsound.Beep(440, 1000)
        time.sleep(3)
        click_image("x.jpg", (1388, 292), "left", 0.05)
    elif signal == "compraf":
        print("compra a favor")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        pyautogui.doubleClick(x=685, y=415)
        pyautogui.doubleClick(x=685, y=415)
        time.sleep(0.1)
        pyautogui.keyDown(tiempo[0])
        time.sleep(2)
        click_image("imagen compra.jpg", (1089, 340), "left", 0.05)
        click_image("imagen compra.jpg", (1089, 340), "left", 0.05)
        #winsound.Beep(440, 1000)
        time.sleep(3)
        click_image("x.jpg", (1388, 292), "left", 0.05)
    elif signal == "ventac":
        print("venta contratendencia")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        pyautogui.doubleClick(x=685, y=415)
        pyautogui.doubleClick(x=685, y=415)
        time.sleep(0.1)
        pyautogui.keyDown(tiempo[0])
        try:
            pyautogui.keyDown(tiempo[1])
        except:
            pass
        time.sleep(2)
        click_image("imagen compra.jpg", (1088, 495), "left", 0.05)
        click_image("imagen compra.jpg", (1088, 495), "left", 0.05)
        #winsound.Beep(440, 1000)
        time.sleep(3)
        click_image("x.jpg", (1388, 292), "left", 0.05)
    elif signal == "ventaf":
        print("venta a favor")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        pyautogui.doubleClick(x=685, y=415)
        pyautogui.doubleClick(x=685, y=415)
        time.sleep(0.1)
        pyautogui.keyDown(tiempo[0])
        time.sleep(2)
        click_image("imagen compra.jpg", (1088, 495), "left", 0.05)
        click_image("imagen compra.jpg", (1088, 495), "left", 0.05)
        #winsound.Beep(440, 1000)
        time.sleep(3)
        click_image("x.jpg", (1388, 292), "left", 0.05)