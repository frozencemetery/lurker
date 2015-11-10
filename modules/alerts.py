import time

import json as J

from module import *

alertdb = "modules/rsrc/alerts.db"
alerts = {}

def loaddb():
  global alerts

  try:
    with open(alertdb, 'r') as f:
      alerts = J.load(f)
    pass
  except:
    print "failed to load alerts.db; corruption possible!"
    pass
  return

def writedb():
  global alerts

  with open(alertdb, 'w') as f:
    J.dump(alerts, f)
    pass
  return

def maybe_alert(user):
  global alerts

  u = user[0].lower()
  sentalert = False
  try:
    while alerts[u] is not None:
      user[-1](alerts[u].pop())
      sentalert = True
      pass
    pass
  except:
    pass
  if sentalert:
    writedb()
    pass
  return

def cmdmsg(senderf, channame, speaker, cmdstr, isact):
  maybe_alert(speaker)

  if cmdstr.startswith("anonalert "):
    cmdstr = cmdstr[4:] # delete "anon"
    speaker = ["An anonymous user"]
    pass

  rem = speaker[0]
  rem += (" (" + speaker[1] + speaker[2] + ")") if len(speaker) > 1 else ""
  rem += time.strftime(" at %Y-%m-%d %H:%M:%S")
  if cmdstr.startswith("alert "):
    _, user, msg = cmdstr.split(" ", 2)
    user = user.lower()
    msg = rem + " told me to tell you " + msg
    try:
      alerts[user].append(msg)
      pass
    except:
      alerts[user] = [msg]
      pass
    writedb()
    senderf("Reminder saved!")
    return True
  return False

def regmsg(channame, speaker, cmdstr, isact):
  return maybe_alert(speaker)

def userjoin(channame, username):
  return maybe_alert(username)

def userpart(channame, username, message):
  return maybe_alert(username)

def unload():
  writedb()
  pass

######

loaddb()
