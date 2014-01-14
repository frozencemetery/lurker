import random
import re

from module import *

convodb = "modules/rsrc/convo.db"

convos = [] # globalize THIS
lastgrep = {} # remaining convos, associated by location

def loaddb():
  global convos

  with open(convodb, 'r') as f:
    convos = f.read().split('\n')
    pass
  if convos[-1] == "":
    # human editing of this file will introduce a newline because people are
    # sane.  However, python with the join/split functions does not expect
    # this newline, and kindly makes a mess on the floor when it goes to use
    # this array.
    del(convos[-1])
    writedb()
    return loaddb() # this is a tail call.  Python will ignore this fact.
  print "loaded okay"
  pass

def getconvo():
  global convos

  return random.choice(convos)

def grepconvos(channel, regex):
  global convos
  global lastgrep
  matching = filter((lambda line: re.match(".*" + regex + ".*", line, re.IGNORECASE)), convos)
  lastgrep[channel] = matching
  return nextgrep(channel)

def nextgrep(channel) :
  global lastgrep

  if not channel in lastgrep.keys() :
    return "No extant queries"
  if len(lastgrep[channel]) == 0 :
    return "No (more) matches found."
  fst, lastgrep[channel] = lastgrep[channel][0], lastgrep[channel][1:]
  return fst + (" {1}[+{0}]{1}".format(len(lastgrep[channel]), chr(2)))

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
  elif cmd.startswith("convo grep "):
    senderf(grepconvos(channel, cmd.split(" ", 2)[2]))
    return True
  elif cmd == "convo next":
    senderf(nextgrep(channel))
  return False

def unload():
  writedb()
  pass

######

loaddb()
