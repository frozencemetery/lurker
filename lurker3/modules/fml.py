import re
import urllib2

from module import *

fmlqueue = []

def obtain():
  global fmlqueue

  html = urllib2.urlopen("http://www.fmylife.com/random").read()
  html = re.findall("Today.*?FML", html)
  del(html[0]) # delete how to make an FML
  html = [re.sub("\<.*?>", "", x) for x in html]
  fmlqueue += html
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
