import urllib2
import re
import cPickle
import random

dictlocat = "rsrc/tfw.dict"
lookup = {}

f = open(dictlocat, 'r')
lookup = cPickle.load(f)
f.close()

def loaddict(self):
  f = open(dictlocat, 'r')
  self.lookup = cPickle.load(f)
  f.close()
  pass

def writedict(self):
  f = open(dictlocat, 'w')
  cPickle.dump(self.lookup, f)
  f.close()
  pass

def cmdmsg(self, channel, channame, speaker, cmd):
  try:
    if cmd == "fw":
      name = lookup[speaker]
      
      switch = random.randint(1,30)
      if switch == 1:
        channel.msg("IT'S RAINING MEN")
        return True
      elif switch == 2:
        channel.msg("CHOCOLATE RAIN")
        return True
      elif switch == 3:
        channel.msg("Cloudy.  With a chance of meatballs.")
        return True
      pass
    elif cmd[:7] == "fw set ":
      name = cmd.split(" ", 2)[2]
      lookup[speaker] = name
      pass
    elif cmd[:3] == "fw ":
      name = cmd.split(" ", 1)[1]

      switch = random.randint(1,30)
      if switch == 1:
        channel.msg("IT'S RAINING MEN")
        return True
      elif switch == 2:
        channel.msg("CHOCOLATE RAIN")
        return True
      elif switch == 3:
        channel.msg("Cloudy.  With a chance of meatballs.")
        return True
      pass
    else:
      return False
    
    url = "http://thefuckingweather.com/?where="
    name = urllib2.quote(cmd)
    url += cmd
    m = urllib2.urlopen(url).read()
    
    temp = int(re.search("(?<=<span class=\"temperature\" tempf=\").*?(?=\">)", m).group(0))
    location = re.search("(?<=<span id=\"locationDisplaySpan\" class=\"small\">).*?(?=</span>)", m).group(0)
    status = re.search("(?<=<p class=\"remark\">).*?(?=</p>)", m).group(0)
    paren = re.search("(?<=<p class=\"flavor\">).*?(?=</p>)", m).group(0)
    dayv = re.search("(?<=<th>DAY</th><th style=\"width:7.5em;\">).*(?=</th>)", m).group(0)
    highv = re.search("(?<=<th>HIGH</th><td class=\"temperature\" tempf=\").*(?=\r)", m).group(0)
    lowv = re.search("(?<=<th>LOW</th><td class=\"temperature\" tempf=\").*(?=\r)", m).group(0)
    fcv = re.search("(?<=<th>FORECAST</th><td>).*(?=\r)", m).group(0)

    highv = re.search("(?<=<td class=\"temperature\" tempf=\").*", highv).group(0)
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

    magic = "\x02" + location + "\x0F: " + str(temp) + " F (" + str(coff(temp)) + " C) | " + status + " (" + paren + ") | " + daya + ": High " + str(tempha) + " F (" + str(coff(tempha)) + " C), Low " + str(templa) + " F (" + str(coff(templa)) + " C).  " + fca + " | " + dayb + ": High " + str(temphb) + " F (" + str(coff(temphb)) + " C), Low " + str(templb) + " F (" + str(coff(templb)) + " C).  " + fcb
    magic = magic.replace("ITS", "IT'S")

    channel.msg(magic)
    pass

  except:
    return False
  pass

def unload(self):
  self.writedict()
  pass
