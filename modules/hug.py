import json as J

from module import *

unhugged = []

nohugs_file = "modules/rsrc/nohugs.db"

def loaddb():
  global unhugged

  try:
    with open(nohugs_file, 'r') as f:
      unhugged = J.load(f)
      pass
    pass
  except:
    print "Failed to load nohugs.db; corruption possible!"
    pass
  return

def writedb():
  global unhugged

  try:
    with open(nohugs_file, 'w') as f:
      J.dump(unhugged, f)
      pass
    pass
  except:
    print "Failed to dump nohugs.db; hugs for everyone!"
    pass
  return

def cmdmsg(senderf, channel, speaker, cmd, isact):
  global unhugged

  if cmd == "hug me never":
    if speaker[0] not in unhugged:
      unhugged.append(speaker[0])
      writedb()
      senderf(speaker[0] + ": I will remember that")
      pass
    else:
      senderf(speaker[0] + ": psh, like I'd forget a thing like that")
      pass
    pass
  elif cmd.startswith("hug "):
    name = cmd.split(" ", 1)[1]
    if name == "me":
      name = speaker[0]
      pass
    if name not in unhugged:
      senderf("hugs " + name, isact=True)
      pass
    else:
      senderf("refuses to violate " + name, isact=True)
      pass
    return True
  return False

def unload():
  writedb()
  return

######

loaddb()
