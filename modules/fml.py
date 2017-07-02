import re
import requests

from module import *

fmlqueue = []

def obtain():
    global fmlqueue

    html = requests.get("http://www.fmylife.com/random").text
    html = re.findall("Today.*?FML", html)
    html = [re.sub("\<.*?>", "", x) for x in html]
    fmlqueue += [h for h in html if len(h) < 400]
    fmlqueue = list(set(fmlqueue)) # great api, folks
    return

def cmdmsg(senderf, channel, speaker, cmd, isact):
    global fmlqueue

    if cmd != "fml":
        return False

    if len(fmlqueue) <= 0:
        try:
            obtain()
            pass
        except:
            senderf("Could not load from FML and cache empty!")
            return True
        pass
    senderf(fmlqueue.pop())
    return True

######

obtain()
