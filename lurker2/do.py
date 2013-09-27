# coding=utf8 # I hate python
# Copyright (C) 2012 Robbie Harwood
# Based on code from the python irclib python-irclib.sourceforge.net (GPL)

  # This file is part of lurker.

  # lurker is free software: you can redistribute it and/or modify
  # it under the terms of the GNU General Public License as published by
  # the Free Software Foundation, either version 3 of the License, or
  # (at your option) any later version.

  # lurker is distributed in the hope that it will be useful,
  # but WITHOUT ANY WARRANTY; without even the implied warranty of
  # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  # GNU General Public License for more details.

  # You should have received a copy of the GNU General Public License
  # along with lurker.  If not, see <http://www.gnu.org/licenses/>.


import math
import random
import urllib
import urllib2
import re
import cPickle
import time

def coff(f): # moderately naive method to get celsius from fahrenheit
  return str((int((int(f)-32)*(500.0)/(9.0)))/100.0)

def roll(t):
  testa = t[1].split("+", 1) #
  testb = t[1].split("-", 1) #
  if len(testa[0]) > len(testb[0]):
    numtoroll = int(t[0])
    sidenum = int(testb[0])
    bonus = -int(testb[1])
    pass
  elif len(testa[0]) < len(testb[0]): #testa's split is better
    numtoroll = int(t[0])
    sidenum = int(testa[0])
    bonus = int(testa[1])
    pass
  else: # the two were equal; in other words, no bonus
    numtoroll = int(t[0])
    sidenum = int(testa[0])
    bonus = 0
    pass
  if numtoroll < 1:
    numtoroll = 1
    pass
  if sidenum < 2:
    counter = numtoroll
    pass
  else:
    if numtoroll <= 1000:
      counter, i = 0, 0
      while i < numtoroll:
        roll = random.randint(1, sidenum)
        counter = counter + roll
        i = i + 1
        pass
      pass
    else:
      # approximate with Gaussian
      counter = int(round(random.gauss(
            numtoroll*(sidenum+1)/2.0,
            math.sqrt(numtoroll*(sidenum**2 - 1)/12.0))))
      pass
  counter = counter + bonus
  return counter

def unhtml(m):
  m = urllib2.unquote(m)
  m = m.replace("+noredirect/", "")
  m = m.replace("+", " ")
  m = m.replace("&quot;", "\"")
  m = m.replace("%26", "&")
  m = m.replace("/_/", " - ")
  return m

def command(self, e, cmd, c, nick):
  channel = e.target()
  if channel[:1] != "#" and channel[:1] != "&" and channel[:1] != "+" and channel[:1] != "!":
    # checking for private queries and responding accordingly
    channel = nick
    pass

  if cmd.startswith("nick ") and nick == "frozencemetery":
    cmd = cmd.split(" ", 1)[1]
    c.nick(cmd)
    pass
  elif cmd.startswith("sendroll ") and nick == "frozencemetery":
    s = cmd.split(" ", 2)
    if len(s) != 3:
      c.privmsg(nick, "Parsing error on token: " + cmd)
      f.write("Parsing error on token: " + cmd)
      pass
    else:
      t = s[2].split("d", 1)
      if len(t) != 2:
        c.privmsg(nick, "Parsing error on token: " + cmd)
        f.write("Parsing error on token: " + cmd)
        pass
      else:
        counter = roll(t)
        c.privmsg(s[1], nick + " rolled a " + str(counter))
        pass
      pass
    pass
  elif cmd == "disconnect" and nick == "frozencemetery":
    self.disconnect()
    pass
  elif cmd == "test" and nick == "frozencemetery":
    c.privmsg(channel, e.source())
    pass
  elif cmd == "die" and nick == "frozencemetery":
    self.die()
    pass
  elif cmd.startswith("join") and nick == "frozencemetery":
    z = cmd.split(" ", 1) 
    disp = z[1].split(" ", 1) 
    c.join(z[1])
    pass
  elif cmd.startswith("say") and nick == "frozencemetery":
    z = cmd.split(" ", 2)
    c.privmsg(z[1], z[2])
    pass
  elif cmd.startswith("action") and nick == "frozencemetery":
    z=cmd.split(" ", 2) 
    c.action(z[1], z[2])
    pass

  elif cmd.startswith("roll"): 
    s = cmd.split(" ", 1) 
    if len(s) != 2:
      c.privmsg(channel, "Syntax is: \"roll xdy[±z]\".")
      pass
    else:
      t = s[1].split("d", 1) 
      if len(t) != 2:
        c.privmsg(channel, "Syntax is: \"roll xdy[±z]\".")
        pass
      else:
        counter = roll(t)
        if nick != "frozencemetery" and channel == nick:
          c.privmsg("frozencemetery", "I rolled : " + str(counter) + " for " + nick + ".")
          pass
        c.privmsg(channel, "I rolled : " + str(counter) + " for " + nick + ".")
        pass
      pass
    pass
  elif cmd.startswith("help") or cmd.startswith("source"):
    c.privmsg(channel, nick + ": https://github.com/frozencemetery/lurker/blob/master/api.org is the current version.  My BTS, source, and other things can be found at https://github.com/frozencemetery/lurker")
    pass
  elif cmd.startswith("hug "):
    name = cmd.split(" ",1)[1]
    nohugs_file = "rsrc/nohugs.db"
    def load_hugs():
      return cPickle.load(open(nohugs_file, "r"))
    def write_hugs(ns):
      cPickle.dump(ns, open(nohugs_file, "w"))
      return ns
    try:
      ns = load_hugs()
      pass
    except IOError:
      ns = write_hugs(frozenset())
    if name == "me never":
      write_hugs(ns | frozenset([nick]))
      c.privmsg(channel, nick + ": I will remember that")
      pass
    else:
      if name == "me":
        name = nick
        pass
      if name not in ns:
        c.action(channel, "hugs {0}.".format(name))
        pass
      else:
        c.action(channel, "refuses to violate {0}.".format(name))
        pass
      pass
    pass
  elif cmd.startswith("fml"):
    response = urllib2.urlopen('http://www.fmylife.com/random')
    html = response.read()
    html = html.replace("Today and ends with FML", "")
    html = re.search("Today.*?FML", html)
    res = html.group(0)
    lst = re.findall("\<.*?>", res)
    for x in lst:
      res = res.replace(x, "")
      pass
    res = res.replace("&quot;", "\"")
    c.privmsg(channel, nick + ": " + res)
    pass
  elif cmd.startswith("fm") or cmd.startswith("np"):
    cmd = cmd.split(" ", 1)
    try:
      cmd = cmd[1]
      if len(cmd) >= 4 and cmd[:4] == "set ":
        cmd = cmd.split(" ", 1)
        user = cmd[1]
        ref = "rsrc/lastfm.dict"
        lf = open(ref, "r")
        bill = cPickle.load(lf)
        lf.close()
        bill[nick] = user
        lf = open(ref, "w")
        cPickle.dump(bill, lf)
        lf.close()
        pass
      else:
        user = cmd
        pass
      pass
    except:
      ref = "rsrc/lastfm.dict"
      lf = open(ref, "r")
      bill = cPickle.load(lf)
      user = bill[nick]
      lf.close()
      pass
    url = "http://ws.audioscrobbler.com/1.0/user/" + user + "/recenttracks.rss"
    response = urllib2.urlopen(url)
    urlload = response.read()
    m = re.search("(?<=/music/).*?(?=</link>)", urlload)
    m = m.group(0)
    ct = unhtml(m)
    c.privmsg(channel, nick + ": " + ct)
    pass
  elif cmd.startswith("fw"):
    try:
      url = "http://thefuckingweather.com/?where="
      ref = "rsrc/tfw.dict"
      cmd = cmd.split(" ", 1)

      try:
        cmd = cmd[1]
        if cmd[:4] == "set ":
          cmd = cmd.split(" ", 1)[1]
          fw = open(ref, "r")
          bill = cPickle.load(fw)
          fw.close()
          bill[nick] = cmd
          fw = open(ref, "w")
          cPickle.dump(bill, fw)
          fw.close()
          pass
        pass
      except:
        fw = open(ref, "r")
        bill = cPickle.load(fw)
        fw.close()
        cmd = bill[nick]
        pass

      cmd = urllib2.quote(cmd)
      url = url + cmd
      m = urllib2.urlopen(url).read()
      m = m.replace("\n", "")

      location = re.search("(?<=class=\"small\">).*?(?=</span>)", m).group(0)
      remark = re.search("(?<=class=\"remark\">).*?(?=</p>)", m).group(0)
      flavor = re.search("(?<=class=\"flavor\">).*?(?=</p>)", m).group(0)

      temps = re.findall("(?<=class=\"temperature\" tempf=\").*?(?=\">)", m)
      days = re.findall("(?<=style=\"width:7.5em;\">).*?(?=</th>)", m)

      fcv = re.search("(?<=<th>FORECAST</th>).*?(?=</tr>)", m).group(0)
      fcs = re.findall("(?<=<td>).*?(?=</td>)", fcv)

      curtemp = temps[0]
      del(temps[0])

      magic = "\x02" + location + "\x0F: " + curtemp + " F (" + coff(curtemp) + " C) | " + remark + " (" + flavor + ") | " + days[0] + ": High " + temps[0] + " F (" + coff(temps[0]) + " C), Low " + temps[len(days)] + " F (" + coff(temps[len(days)]) + " C).  " + fcs[0] + " | " + days[1] + ": High " + temps[1] + " F (" + coff(temps[1]) + " C), Low " + temps[len(days) + 1] + " F (" + coff(temps[len(days) + 1]) + " C).  " + fcs[1]

      switch = random.randint(1,30)
      if switch == 1:
        c.privmsg(channel, "IT'S RAINING MEN")
        pass
      elif switch == 2:
        c.privmsg(channel, "CHOCOLATE RAIN")
        pass
      elif switch == 3:
        c.privmsg(channel, "Cloudy.  With a chance of meatballs.")
        pass
      else:
        c.privmsg(channel, magic)
        pass
      pass
    except:
      c.privmsg(channel, "Syntax is !fw <location>.  If you have invoked !fw set <location>, you may invoke !fw.")
      pass
    pass
  elif cmd.startswith("alert "):
    stof = "rsrc/alerts.db"
    read = open(stof, "a")
    cmd = e.source() + " " + cmd.split(" ", 1)[1] 
    if len(cmd) > 380:
      cmd = cmd[:380]
      pass
    cmd += time.strftime(" at %Y:%m:%d:%H:%M:%S")
    read.write(cmd + "\n")
    read.close()
    c.privmsg(channel, "Reminder saved.")
    pass
  elif cmd.startswith("anonalert "):
    stof = "rsrc/alerts.db"
    read = open(stof, "a")
    cmd = "<anonymous_user> " + cmd.split(" ", 1)[1]
    if len(cmd) > 380:
      cmd = cmd[:380]
      pass
    cmd += time.strftime(" at %Y:%m:%d:%H:%M:%S")
    read.write(cmd + "\n")
    read.close()
    c.privmsg(channel, "Reminder saved.")
    pass
  elif cmd == "convo":
    stored = ""
    with open("rsrc/convo.db", "r") as f:
      for i,line in enumerate(f):
        if random.random() < (1.0/(i+1)):
          stored = line
          pass
        pass
      pass
    c.privmsg(channel, stored) 
    pass
  elif cmd.startswith("convo add "):
    cmd = cmd.split(" ", 2)[2]
    stof = open("rsrc/convo.db", 'a')
    stof.write(cmd + '\n')
    stof.close()
    finalline = "NOW WE'RE HAVING A GOOD TIME RIGHT"
    c.privmsg(channel, finalline)
    pass
  elif cmd.startswith("q ") or cmd.startswith("ddg ") or cmd.startswith("ddg ") or cmd.startswith("quack "):
    cmd = cmd.split(" ", 1)[1]
    url = "https://duckduckgo.com/html?kp=-1&q="
    beep = urllib.quote_plus(cmd)
    c.privmsg(channel, nick + ": " + url + beep)
    pass
  elif cmd.startswith("test"):
    c.privmsg(channel, nick + ": blargl")
    pass
  elif cmd.startswith("ping"):
    c.action(channel, "squeaks at " + nick)
    pass
  elif cmd == "static":    
    c.action(channel, "ssssssssssssSSSSSSSSSSSSHHHHHHHHHHHHHHHHHHHHHHHHHHHHHhsssssssssssssssssssss")
    pass
  elif cmd.startswith("lantunes") or cmd.startswith("lt"):
    parts = cmd.strip().split(" ",1)
    url = "http://music.furstlabs.com/"
    if len(parts) == 1:
      url += "queue"
      try:
        m = urllib2.urlopen(url).read().replace('\n', '')
        first = re.search("(?<=class=\"even\">).*?</tr>", m).group(0)
        info = re.findall("(?<=<td>).*?(?=</td>)", first)
        
        track = unhtml(info[0])
        artist = unhtml(info[1])
        nptime = unhtml(info[-2])
        if len(info) >= 5:
          album = unhtml(" [" + info[2] + "]")
          pass
        else:
          album = ""
          pass

        response = artist + " - \"" + track + "\"" + album + " (" + nptime + ")"
        c.privmsg(channel, nick + ": " + response)
      except:
        pass
      pass
    else:
      url += "submit"
      try:
        m = urllib2.urlopen(url, "uri="+urllib2.quote(parts[1]))
        m.read()
        c.privmsg(channel, "Queued to lantunes.")
        pass
      except:
        c.privmsg(channel, "Failed to queue to lantunes.")
        pass
      pass
    pass
  elif cmd == "sup":
    c.privmsg(channel, "notmuch.")
    pass
  elif cmd == "space":
    c.privmsg(channel, "http://spaaaaaaaaaaaaaaaaaaaaaaaccee.com/")
    pass
  elif cmd == "rain":
    try:
      url = "http://isitraining.in/"
      ref = "rsrc/tfw.dict"
      cmd = cmd.split(" ", 1)
      try:
        cmd = cmd[1]
        if cmd[:4] == "set ":
          cmd = cmd.split(" ", 1)[1]
          fw = open(ref, "r")
          bill = cPickle.load(fw)
          fw.close()
          bill[nick] = cmd
          fw = open(ref, "w")
          cPickle.dump(bill, fw)
          fw.close()
          pass
        pass
      except:
        fw = open(ref, "r")
        bill = cPickle.load(fw)
        fw.close()
        cmd = bill[nick]
        pass
      cmd = urllib2.quote(cmd)
      url = url + cmd
      response = urllib2.urlopen(url)
      m = response.read()
      stat = re.search("(?<=<h1>).*?(?=</h1>)", m).group(0)
      addi = re.search("(?<=<h2>).*?(?=</h2>)", m).group(0)
      addi = addi.replace("<br/>", " ")
      addi = addi.replace("&deg;", unichr(176).encode("latin-1"))
      addi = addi.replace("<strong>", "")
      addi = addi.replace("</strong>", "")
      addi[0] = 'c'
      c.privmsg(channel, nick + ": " + stat + ".  Furthermore, " + addi)
    except:
      c.privmsg("Fuck you and fuck your horse.")
      pass
  elif cmd.startswith("jacket"):
    try:
      url = "http://doineedajacket.com/weather/"
      ref = "rsrc/tfw.dict"
      cmd = cmd.split(" ", 1)
      try:
        cmd = cmd[1]
        if cmd[:4] == "set ":
          cmd = cmd.split(" ", 1)[1]
          fw = open(ref, "r")
          bill = cPickle.load(fw)
          fw.close()
          bill[nick] = cmd
          fw = open(ref, "w")
          cPickle.dump(bill, fw)
          fw.close()
          pass
        pass
      except:
        fw = open(ref, "r")
        bill = cPickle.load(fw)
        fw.close()
        cmd = bill[nick]
        pass
      cmd = urllib2.quote(cmd)
      url = url + cmd
      response = urllib2.urlopen(url)
      m = response.read()
      loc = re.search("(?<=<div class='location'>).*?(?=</div>)", m).group(0)
      jtime = re.search("(?<=<div class='time'>).*?(?=</div>)", m).group(0)
      need = re.search("(?<=<h1>).*?(?=</h1>)", m).group(0)
      twohrs = re.search("(?<=<h2>).*?(?=</h2>)", m).group(0)
      fourhrs = re.search("(?<=<h3>).*?(?=</h3>)", m).group(0)
      eighthrs = re.search("(?<=<h4>).*?(?=</h4>)", m).group(0)
      magic = "Based on the weather in " + loc + ", " + jtime + ": " + need + ". "
      magic = magic + twohrs + ". " + fourhrs + ". " + eighthrs + "."
      c.privmsg(channel, magic) 
    except:
      c.privmsg(channel, "Syntax is !jacket <location>.  If you have invoked !fw set <location>, you may invoke !jacket.")
      pass
  elif cmd.startswith("deal "):
    targets = cmd.split(" ", 5)[1:5]

    deck = []
    for x in range(13):
      deck.append((x+2, "S"))
      deck.append((x+2, "H"))
      deck.append((x+2, "D"))
      deck.append((x+2, "C"))
      pass
    random.shuffle(deck)

    def send_hand(target, cards):
      clubs = []
      diams = []
      harts = []
      spads = []
      for x in cards:
        if x[1] is "C": 
          clubs.append(x[0])
          pass
        elif x[1] is "D": 
          diams.append(x[0])
          pass
        elif x[1] is "H": 
          harts.append(x[0])
          pass
        elif x[1] is "S": 
          spads.append(x[0])
          pass
        pass
      clubs.sort()
      diams.sort()
      harts.sort()
      spads.sort()
      
      def make_suit(letter, suit_cards):
        string = letter + ": "
        for x in suit_cards:
          if x is 10: 
            string += "T"
            pass
          elif x is 11: 
            string += "J"
            pass
          elif x is 12: 
            string += "Q"
            pass
          elif x is 13: 
            string += "K"
            pass
          elif x is 14: 
            string += "A"
            pass
          else: 
            string += str(x)
            pass
          pass
        string += "  "
        return string
      
      clubs = make_suit("C", clubs)
      diams = make_suit("D", diams)
      harts = make_suit("H", harts)
      spads = make_suit("S", spads)

      c.privmsg(target, clubs + diams + harts + spads)

      pass

    for i in range(len(targets)):
      send_hand(targets[i], deck[i*13:(i+1)*13])
      pass
    pass
  elif len(cmd) <= 0:
    return
  else:
    print "Failed."
    c.action(channel, "doesn't know how to " + cmd + ".")
    pass
  pass
