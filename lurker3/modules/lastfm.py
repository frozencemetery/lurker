import cPickle
import re
import urllib2

from module import *

lastfmdict = "rsrc/lastfm.dict"

f = open(lastfmdict, 'r')
lookup = cPickle.load(f)
f.close()

def reloaddict(self):
  f = open(lastfmdict, 'r')
  self.lookup = cPickle.load(f)
  f.close()
  pass

def dumpdict(self):
  f = open(lastfmdict, 'w')
  cPickle.dump(self.lookup, f)
  f.close()

def addentry(self, nick, lastfm):
  self.lookup[nick] = lastfm
  dumpdict(self)
  pass

def cmdmsg(self, channel, channame, speaker, cmd):
  if cmd == "fm" or cmd == "np":
    lastfm = self.lookup[speaker]
    pass
  elif cmd[:7] == "fm set " or cmd[:7] == "np set ":
    lastfm = cmd.split(" ", 2)[2]
    addentry(self, speaker, lastfm)
    pass
  elif cmd[:3] == "fm " or cmd[:3] == "np ":
    lastfm = cmd.split(" ", 1)[1]
    pass
  if not lastfm:
    return False
  else:
    try:
      url = "http://ws.audioscrobbler.com/1.0/user/" + user + "/recenttracks.rss"
      urlload = urllib2.urlopen(url).read()
      m = re.search("(?<=/music/).*?(?=</link>)", urlload)
      m = m.group(0)
      m = urllib2.unquote(m)
      m = m.replace("+noredirect/", "")
      m = m.replace("+", " ")
      m = m.replace("&quot;", "\"")
      m = m.replace("%26", "&")
      ct = m.replace("/_/", " - ")
      ct = urllib2.unquote(ct)
      channel.msg(speaker + ": " + ct)
      return True
    except:
      return False
    pass
  pass

def unload(self):
  dumpdict(self)
  pass
