import re
import urllib
import urllib2

import cPickle as P

from module import *

lastfmdict = "modules/rsrc/lastfm.dict"
users = {}

def loaddict():
  global users

  try:
    with open(lastfmdict, 'r') as f:
      users = P.load(f)
      pass
  except:
    print "failed to load lastfm.dict; corruption possible!"
    pass
  return

def writedb():
  global users

  with open(lastfmdict, 'w') as f:
    P.dump(users, f)
    pass
  return

def unhtml(m):
  m = urllib2.unquote(m)
  m = m.replace("+noredirect/", "")
  m = m.replace("+", " ")
  m = m.replace("&quot;", "\"")
  m = m.replace("%26", "&")
  m = m.replace("/_/", " - ")
  return m

def cmdmsg(senderf, channame, speaker, cmdstr, isact):
  global users

  if cmdstr.startswith("fm") or cmdstr.startswith("np"):
    cmd = cmdstr.split(" ", 2)
    if len(cmd) == 3 and cmd[1] == "set":
      u = cmd[2]
      users[speaker[0]] = u
      writedb()
      pass
    elif len(cmd) == 2:
      u = cmd[1]
      pass
    else:
      try:
        u = users[speaker[0]]
        pass
      except:
        senderf("Syntax is `!fm username`.  If you have invoked `!fm set username`, you may invoke `!fm`.")
        return True
      pass

    url = "http://ws.audioscrobbler.com/1.0/user/" + u + "/recenttracks.rss"
    response = urllib2.urlopen(url)
    urlload = response.read()
    m = re.search("(?<=/music/).*?(?=</link>)", urlload).group(0)
    ct = unhtml(m)
    senderf(speaker[0] + ": " + ct)
    pass
  return False

def unload():
  writedb()
  return

######

loaddict()
