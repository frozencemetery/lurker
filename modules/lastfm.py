import re
import urllib
import urllib2

import json as J

from module import *

lastfmdict = "modules/rsrc/lastfm.dict"
users = {}

def loaddict():
    global users

    try:
        with open(lastfmdict, 'r') as f:
            users = J.load(f)
            pass
    except:
        print "failed to load lastfm.dict; corruption possible!"
        pass
    return

def writedb():
    global users

    with open(lastfmdict, 'w') as f:
        J.dump(users, f)
        pass
    return

# TODO(frozen) Handle escapes of the form %dd
def unhtml(m):
    m = urllib2.unquote(m)
    m = m.replace("+noredirect/", "")
    m = m.replace("+", " ")
    m = m.replace("&quot;", "\"")
    m = m.replace("&amp;", "&")
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
                senderf("Uage: `!fm [username]`.  "
                        "Set default username with `!fm set username`.")
                return True
            pass

        url = "http://www.last.fm/user/" + u
        response = urllib2.urlopen(url).read()
        response = response[response.index("Recent") + len("Recent"):]
        m = re.search("(?<=/music/)([^/\n]*)/[^/\n]*/([^/\n]*?)(?=\")",
                      response)
        senderf(speaker[0] + ": " +
                unhtml(m.group(1)) + " - " + unhtml(m.group(2)))
        return True
    return False

def unload():
    writedb()
    return

######

loaddict()
