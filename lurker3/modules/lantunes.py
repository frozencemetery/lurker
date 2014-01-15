import re
import urllib2

from module import *

url = "http://music.furstlabs.com/"

def unhtml(m):
  m = urllib2.unquote(m)
  m = m.replace("+noredirect/", "")
  m = m.replace("+", " ")
  m = m.replace("&quot;", "\"")
  m = m.replace("%26", "&")
  m = m.replace("/_/", " - ")
  return m

def getqueue():
  u = url + "queue"
  try:
    m = urllib2.urlopen(url).read().replace('\n', "")
    first = re.search("(?<=class=\"even\">).*?</tr>", m).group(0)
    info = re.findall("(?<=<td>).*?(?=</td>)", first)

    artist = unhtml(info[1])
    artist = artist + " -" if artist != "N/A" else ""

    track = unhtml(info[0])
    track = " \"" + track + "\"" if track != "N/A" else ""

    nptime = unhtml(info[-2])
    nptime = " (" + nptime + ")" if nptime != "N/A" else ""

    album = unhtml(info[2]) if len(info) >= 5 else ""
    album = " [" + album + "]" if album != "N/A" else ""

    ret = artist + track + album + nptime
    pass
  except:
    ret = "Lanqueue empty or inaccessible!"
    pass
  return ret
  

def cmdmsg(senderf, channel, speaker, cmd, isact):
  if cmd == "lt" or cmd == "lantunes":
    senderf(getqueue())
    return True
  elif cmd.startswith("lt submit ") or cmd.startswith("lantunes submit "):
    try:
      queue = cmd.split(" ", 2)[2]
      m = urllib2.urlopen(url + "submit", "uri=" + urllib2.quote(queue))
      m = m.read()
      senderf(speaker[0] + ": queued to lantunes!")
      pass
    except:
      senderf(speaker[0] + ": failed to queue!")
      pass
    return True
  return False
