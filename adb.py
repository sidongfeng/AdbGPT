import _init_paths
import time
import os
from loguru import logger
import uiautomator2 as u2
from pprint import pprint

import config

def screen_shot(index, save_path):
    """
    """
    cmd = r"adb shell /system/bin/screencap -p /sdcard/screenshot-" + str(index) + ".png"
    print("run command: {}".format(cmd))
    os.system(cmd)
    cmd = r"adb pull /sdcard/screenshot-" + str(index) + ".png " + save_path
    print("run command: {}".format(cmd))
    os.system(cmd)

def back():
    """
    :param uiobject:
    :return:
    """
    time.sleep(0.5)
    cmd = "adb shell input keyevent 4"
    print("run command: {}".format(cmd))
    os.system(cmd)
    

def click(bounds):
    """
    :param uiobject:
    :return:
    """
    time.sleep(0.5)
    x1, y1, x2, y2 = bounds
    cmd = "adb shell input tap {x} {y}"
    cmd = cmd.replace('{x}', str((x1 + x2) / 2)).replace('{y}', str((y1 + y2) / 2))
    print("run command: {}".format(cmd))
    os.system(cmd)

def double_click(bounds):
    """
    :param uiobject:
    :return:
    """
    time.sleep(0.5)
    x1, y1, x2, y2 = bounds
    cmd = "adb shell input tap {x} {y}"
    cmd = cmd.replace('{x}', str((x1 + x2) / 2)).replace('{y}', str((y1 + y2) / 2))
    print("run command: {}".format(cmd))
    os.system(cmd)
    time.sleep(0.1)
    print("run command: {}".format(cmd))
    os.system(cmd)

def input_text(bounds, content):
    """
    """
    time.sleep(0.5)
    x1, y1, x2, y2 = bounds
    cmd = "adb shell input tap {x} {y}"

    cmd = cmd.replace('{x}', str((x1 + x2) / 2)).replace('{y}', str((y1 + y2) / 2))
    print("run command: {}".format(cmd))
    os.system(cmd)

    content = content.replace(' ', '\ ')
    time.sleep(0.5)
    cmd = "adb shell input text " + content
    os.system(cmd)

def long_click(bounds):
    """
    """
    time.sleep(0.5)
    x1, y1, x2, y2 = bounds
    cmd = "adb shell input swipe {} {} {} {} {}".format(str((x1 + x2) / 2), str((y1 + y2) / 2), str((x1 + x2) / 2 + 1), str((y1 + y2) / 2 + 1), 500)
    print("run command: {}".format(cmd))
    os.system(cmd)

def scroll(direction):
    """
    """
    time.sleep(0.5)
    if direction == "down":
        cmd = "adb shell input swipe {} {} {} {} {}".format(str(config.XML_SCREEN_WIDTH / 2), str(config.XML_SCREEN_HEIGHT - 300), str(config.XML_SCREEN_WIDTH / 2 + 1), str(300), 500)
    else:
        cmd = "adb shell input swipe {} {} {} {} {}".format(str(config.XML_SCREEN_WIDTH / 2), str(config.XML_SCREEN_HEIGHT * 1 / 16 + 300), str(config.XML_SCREEN_WIDTH / 2 + 1), str(config.XML_SCREEN_HEIGHT - 300), 500)
    print("run command: {}".format(cmd))
    os.system(cmd)


if __name__ == '__main__':
    screen_shot('test', './')

    bounds = [958, 2629, 1058, 2696]
    # click(bounds)

    bounds = [455, 1053, 1324,1168]
    # input_text(bounds, '123')

    scroll('down')