# coding=utf8

import random
import re
import requests

import json as J

from bs4 import BeautifulSoup as BS

from module import *

dictlocat = "modules/rsrc/tfw.dict"
lookup = {}

def loaddict():
    global lookup

    try:
        with open(dictlocat, 'r') as f:
            lookup = J.load(f)
            pass
        pass
    except:
        print("failed to load tfw.dict; corruption possible!")
        pass
    return

def writedict():
    global lookup

    with open(dictlocat, 'w') as f:
        J.dump(lookup, f)
        pass
    return

def coff(f):
    return int( (int(f) - 32.0) * 5 / 9 )

def get_cute(st):
    t = int(st)
    ct = coff(t)
    temps = [t, ct]
    if 69 in temps:
        return "IT'S FUCKING SEXY TIME"
    elif t == 32:
        return "TWO NIPPLES MOTHERFUCKER"
    elif ct == 20:
        return "NO NIPPLES MOTHERFUCKER"
    elif 21 in temps:
        return "FUCKING BLACKJACK"
    elif 13 in temps:
        return "WHO BROKE A FUCKING MIRROR"
    elif 7 in temps:
        return "IT'S YOUR LUCKY FUCKING DAY"
    elif t < -75:
        return "GOOD LUCK BUILDING A FIRE ASSHOLE"
    elif t == 100:
        return "IF TEMPERATURE WERE A PERCENT YOU'D HAVE ALL OF IT"
    elif t < 32:
        # "frozen" range
        return random.choice(
            [ "IT'S FUCKING COLD"
            , "MY NIPPLES CAN CUT GLASS"
            ])
    elif t < 50 or 100 > t >= 75:
        return random.choice(
            [ "WEATHER IS FUCKING HAPPENING"
            , "GOOD DAY FOR CLAM EROTICA"
            , "IT'S RAINING MEN"
            , "CHOCOLATE RAIN"
            , "CAN SOMEONE CHECK THE PRESSURE IN MY BELL VALVE"
            , "MY CAR WON'T FUCKING START"
            ])
    elif t < 68:
        return "IT'S FUCKING HOODIE WEATHER"
    elif t < 75:
        return "YOU COULD WALK OUTSIDE AND NOT NOTICE"
    return "TOO HOT FOR WEATHER MESSAGES"

def cmdmsg(senderf, channame, speaker, cmdstr, isact):
    global lookup

    if cmdstr == "fw":
        try:
            name = lookup[speaker[0]]
            pass
        except:
            senderf(speaker[0] +
                    ": I don't know your location!  Try `!fw set place`.")
            return True
        pass
    elif cmdstr.startswith("fw set "):
        name = cmdstr.split(" ", 2)[2]
        lookup[speaker[0]] = name
        pass
    elif cmdstr.startswith("fw "):
        name = cmdstr.split(" ", 1)[1]
        pass
    else:
        return False

    u = "https://www.wunderground.com/cgi-bin/findweather/getForecast?query="
    try:
        s = BS(requests.get(u + name).text, "lxml")
        place = s.title.string.split(" Forecast")[0]
        forecast = s.find_all("div",
                              attrs={"id": "curCond"})[0].span.contents[0]

        current = s.find_all("span", attrs={"data-variable": "temperature"})
        current = current[0].span.contents[0]
        if "." in current: # ugh, too precise
            current = current[:current.index('.')]
            pass

        pass
    except Exception as e:
        senderf("The weather machine is probably broken, sorry.")
        print(e)
        return True

    s = "%(user)s: %(place)s %(forecast)s %(current)sF/%(current_c)sC %(cute)s"
    d = {"user": speaker[0], "place": place, "current": current,
         "forecast": forecast, "current_c": coff(current),
         "cute": get_cute(current)}
    senderf(s % d)
    return True


def unload():
    writedict()
    pass

######

loaddict()
