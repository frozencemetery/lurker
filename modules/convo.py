import random
import re

from collections import defaultdict
from module import *
from ircutil import NICK

convodb = "modules/rsrc/convo.db"

convos = [] # globalize THIS
lastgrep = {} # remaining convos, associated by location
lastseen = defaultdict(dict) # last lines, by channel, then user
lastconvo = None # last convo made
lastconvoer = None # last person who convod, to avoid undoing the wrong one
oldconvos = None # convo before last add operation

class SeenLine:
  def __init__(self, message, nick, isact):
    self.message, self.nick, self.isact = message, nick, isact
    pass
  pass

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
    # human and lurker editing of this file will introduce a newline because
    # people are sane.  However, python with the join/split functions does not
    # expect this newline, and kindly makes a mess on the floor when it goes
    # to use this array.
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

def grepconvos(channel, regex):
  global convos
  global lastgrep
  matching = filter( \
    (lambda line: re.match(".*" + regex + ".*", line, re.IGNORECASE)), convos)
  random.shuffle(matching)
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

def convolast(senderf, channel, pattern, speaker):
  global lastseen

  match = re.match("^(.*?)(" + NICK + ")(.*?)$", pattern)
  if match:
    prefix, nick, suffix = match.groups()
    if nick.lower() in lastseen[channel].keys():
      last = lastseen[channel][nick.lower()]
      if last.isact:
        addconvo("* {0} {1}".format(last.nick, last.message), speaker)
        pass
      else:
        if prefix == suffix == "" :
          addconvo(last.message, speaker);
          pass
        else:
          addconvo("{0}{1}{2} {3}".format( \
              prefix, last.nick, suffix, last.message), speaker)
          pass
        pass
      senderf("NOW WE'RE HAVING A GOOD TIME RIGHT")
      pass
    else:
      senderf("Could not find nick '{0}'".format(nick))
      pass
  else:
    senderf("Invalid pattern: '{0}'".format(pattern))
    pass
  pass

def popconvo(senderf, speaker):
  global convos
  global oldconvos
  global lastconvo
  global lastconvoer

  if convos == []:
    senderf("YOU CANNOT KILL THAT IS ALREADY DEAD (no convos found)")
    pass
  elif lastconvo == None:
    senderf("No convo found since last reload")
    pass
  elif lastconvoer.lower() != speaker[0].lower():
    senderf("You weren't the last convoer, so you can't undo")
    pass
  else:
    convos = oldconvos
    writedb()
    senderf("Deleted: " + lastconvo)
    z = lastconvo
    lastconvo = None
    return z
  pass

def log(channel, nick, line, isact):
  global lastseen
  lastseen[channel][nick.lower()] = SeenLine(line, nick, isact)
  pass

def writedb():
  with open(convodb, 'w') as f:
    f.write('\n'.join(convos) + '\n')
    pass
  pass

def addconvo(convo, convoer):
  global convos
  global lastconvo
  global lastconvoer
  global oldconvos

  oldconvos = convos[:]
  convos.append(convo)
  lastconvo = convo
  lastconvoer = convoer
  with open(convodb, 'a') as f:
    f.write(convo + '\n')
    pass
  pass

def regmsg(channame, speaker, cmdstr, isact):
  log(channame, speaker[0], cmdstr, isact)
  pass

def cmdmsg(senderf, channel, speaker, cmd, isact):
  if isact:
    return False

  if cmd == "convo":
    senderf(getconvo())
    return True
  elif cmd.startswith("convo add "):
    addconvo(cmd.split(" ", 2)[2], speaker[0])
    senderf("NOW WE'RE HAVING A GOOD TIME RIGHT")
    return True
  elif cmd.startswith("convo grep "):
    senderf(grepconvos(channel, cmd.split(" ", 2)[2]))
    return True
  elif cmd == "convo next":
    senderf(nextgrep(channel))
    return True
  elif cmd.startswith("convo last "):
    convolast(senderf, channel, cmd.split(" ", 2)[2], speaker[0])
    return True
  elif cmd == "convo show":
    if lastconvo:
      senderf(lastconvo)
      pass
    else:
      senderf("No convo added since last reload")
      pass
    return True
  elif cmd == "convo undo":
    popconvo(senderf, speaker)
    return True
  elif cmd.startswith("convo fix"):
    args = cmd.split(" ")[2:]
    if len(args) > 3 or len(args) < 2:
      senderf("Bad fix string.")
      return True
    if len(args) == 3:
      try:
        ct = int(args[2])
        pass
      except:
        senderf("Bad replacement count.")
        pass
      pass
    popmsg = [""]
    def maybe_print(s):
      popmsg[0] = s
      pass
    last = popconvo(maybe_print, speaker) # gross hack!
    if last == None:
      senderf("Failed to pop convo:" + popmsg[0])
      return True
    else:
      if len(args) == 3:
        newconvo = last.replace(args[0], args[1], ct)
        pass
      else:
        newconvo = last.replace(args[0], args[1])
        pass
      addconvo(newconvo, speaker[0])
      senderf("Updated: " + newconvo)
      return True
    pass
  return False

def unload():
  writedb()
  pass

######

loaddb()
