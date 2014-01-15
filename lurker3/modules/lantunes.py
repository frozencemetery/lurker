import re
import urllib2

from module import *

url = "http://music.furstlabs.com/queue"

def unhtml(m):
  m = urllib2.unquote(m)
  m = m.replace("+noredirect/", "")
  m = m.replace("+", " ")
  m = m.replace("&quot;", "\"")
  m = m.replace("%26", "&")
  m = m.replace("/_/", " - ")
  return m

def cmdmsg(senderf, channel, speaker, cmd, isact):
  if isact or (cmd != "lt" and cmd != "lantunes"):
    return False

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

    senderf(artist + track + album + nptime)
    return True
  except:
    senderf("Lanqueue empty or inaccessible!")
    return True
  pass
