import random

from module import *

convodb = "modules/rsrc/convo.db"

convos = [] # globalize THIS

def loaddb():
  global convos

  try:
    with open(convodb, 'r') as f:
      convos = f.read().split('\n')
      pass
    pass
  except:
    print "Failed to load convo.db; corruption possible!"
    return

  if convos[-1] == "":
    # human editing of this file will introduce a newline because people are
    # sane.  However, python with the join/split functions does not expect
    # this newline, and kindly makes a mess on the floor when it goes to use
    # this array.
    del(convos[-1])
    writedb()
    pass
  print "loaded okay"
  pass

def getconvo():
  global convos

  try:
    return random.choice(convos)
  except:
    return "CONVO.DB EMPTY; WORST PARTY EVER"

def writedb():
  with open(convodb, 'w') as f:
    f.write('\n'.join(convos))
    pass
  pass

def addconvo(convo):
  global convos

  convos.append(convo)
  with open(convodb, 'a') as f:
    # since we removed any trailing newline when we loaded, and since our full
    # write does not add one, we should not add one here else we introduce
    # gaps.
    f.write('\n' + convo)
    pass
  pass

def cmdmsg(senderf, channel, speaker, cmd, isact):
  if isact:
    return False

  if cmd == "convo":
    senderf(getconvo())
    return True
  elif cmd.startswith("convo add "):
    addconvo(cmd.split(" ", 2)[2])
    senderf("NOW WE'RE HAVING A GOOD TIME RIGHT")
    return True

  return False

def unload():
  writedb()
  pass

######

loaddb()
