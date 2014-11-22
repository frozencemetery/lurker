import urllib2
import re
import random

import json as J

from module import *

dictlocat = "modules/rsrc/tfw.dict"
lookup = {}

def loaddict():
  global lookup

  with open(dictlocat, 'r') as f:
    lookup = J.load(f)
    pass
  return

def writedict():
  global lookup

  with open(dictlocat, 'w') as f:
    J.dump(lookup, f)
    pass
  return

def coff(f):
   return str(int( (int(f) - 32.0) * 5 / 9 ))

def cmdmsg(senderf, channame, speaker, cmdstr, isact):
  global lookup


  if cmdstr == "fw":
    try:
      name = lookup[speaker[0]]
      pass
    except:
      senderf(speaker[0] + ": I don't know your location!  Try `!fw set place`.")
      return True

    switch = random.randint(1,30)
    if switch == 1:
      senderf("IT'S RAINING MEN")
      return True
    elif switch == 2:
      senderf("CHOCOLATE RAIN")
      return True
    elif switch == 3:
      senderf("Cloudy.  With a chance of meatballs.")
      return True
    pass
  elif cmdstr.startswith("fw set "):
    name = cmdstr.split(" ", 2)[2]
    lookup[speaker[0]] = name
    pass
  elif cmdstr.startswith("fw "):
    name = cmdstr.split(" ", 1)[1]

    switch = random.randint(1,30)
    if switch == 1:
      senderf("IT'S RAINING MEN")
      return True
    elif switch == 2:
      senderf("CHOCOLATE RAIN")
      return True
    elif switch == 3:
      senderf("Cloudy.  With a chance of meatballs.")
      return True
    pass
  else:
    return False

  try:
    url = "http://thefuckingweather.com/?where="
    name = urllib2.quote(name)
    url += name
    m = urllib2.urlopen(url).read()

    temp = int(re.search( \
        "(?<=<span class=\"temperature\" tempf=\").*?(?=\">)", m).group(0))
    location = re.search( \
      "(?<=<span id=\"locationDisplaySpan\" class=\"small\">).*?(?=</span>)", \
        m).group(0)
    status = re.search("(?<=<p class=\"remark\">).*?(?=</p>)", m).group(0)
    paren = re.search("(?<=<p class=\"flavor\">).*?(?=</p>)", m).group(0)
    dayv = re.search( \
      "(?<=<th>DAY</th><th style=\"width:7.5em;\">).*(?=</th>)", m).group(0)
    highv = re.search( \
      "(?<=<th>HIGH</th><td class=\"temperature\" tempf=\").*(?=\r)", \
        m).group(0)
    lowv = re.search( \
      "(?<=<th>LOW</th><td class=\"temperature\" tempf=\").*(?=\r)", \
        m).group(0)
    fcv = re.search("(?<=<th>FORECAST</th><td>).*(?=\r)", m).group(0)

    highv = re.search("(?<=<td class=\"temperature\" tempf=\").*", \
                        highv).group(0)
    tempha = int(re.search(".*?(?=\">)", highv).group(0))
    highv = re.search("(?<=tempf=\").*", highv).group(0)
    templa = int(re.search(".*?(?=\">)", lowv).group(0))
    lowv = re.search("(?<=tempf=\").*", lowv).group(0)
    fca = re.search(".*?(?=</td>)", fcv).group(0)
    fcv = re.search("(?<=<td>).*", fcv).group(0)
    daya = re.search(".*?(?=</th>)", dayv).group(0)
    dayv = re.search("(?<=em;\">).*", dayv).group(0)
    dayb = re.search(".*?(?=</th>)", dayv).group(0)
    temphb = int(re.search(".*?(?=\">)", highv).group(0))
    templb = int(re.search(".*?(?=\">)", lowv).group(0))
    fcb = re.search(".*?(?=</td>)", fcv).group(0)

    magic = "\x02" + location + "\x0F: " + str(temp) + " F (" + \
        str(coff(temp)) + " C) | " + status + " (" + paren + ") | " + daya + \
        ": High " + str(tempha) + " F (" + str(coff(tempha)) + " C), Low " + \
        str(templa) + " F (" + str(coff(templa)) + " C).  " + fca + " | " + \
        dayb + ": High " + str(temphb) + " F (" + str(coff(temphb)) + \
        " C), Low " + str(templb) + " F (" + str(coff(templb)) + " C).  " + \
        fcb
    magic = magic.replace("ITS", "IT'S")

    senderf(magic)
    pass
  except:
    senderf("The weather machine is probably broken, sorry.")
    return True
  pass


def unload():
  writedict()
  pass

######

loaddict()
