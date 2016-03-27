import random
import re

from collections import defaultdict
from module import *
from ircutil import NICK

CONVO_MAX_LEN = 400

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

def maybe_pop(speaker):
  global convos
  global oldconvos
  global lastconvo
  global lastconvoer

  if convos == []:
    return 0
  elif lastconvo == None:
    return 1
  elif lastconvoer.lower() != speaker[0].lower():
    return 2

  convos = oldconvos
  writedb()
  z = lastconvo
  lastconvo = None
  return z

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

def convofix(cmd, speaker, senderf):
  def iseven(s):
    even = True
    for c in s[::-1]:
      if c != '\\':
        break
      even = not even
      pass
    return even

  cmd = cmd.split("/")

  if cmd[0] != "s":
    senderf("FUCKSTICK says what is that")
    return True

  while not iseven(cmd[1]):
    cmd[1] += '/' + cmd[2]
    del(cmd[2])
    pass
  while not iseven(cmd[2]):
    cmd[2] += '/' + cmd[3]
    del(cmd[3])
    pass

  option = False
  if len(cmd) != 4:
    senderf("FUCKSTICK says nuh-uh")
    return True
  if cmd[3] == 'g':
    option = True
    pass
  elif cmd[3] != '':
    senderf("FUCKSTICK says nice try")
    return True

  orig = cmd[1]
  subst = cmd[2]

  last = maybe_pop(speaker)
  if last in [0,1,2]:
    senderf("Failed to pop convo; were you the last speaker?")
    return True

  orig = orig.replace("\\/", "/")
  subst = subst.replace("\\/", "/")
  
  try:
    failure = False
    if option:
      newconvo = re.sub(orig, subst, last)
      pass
    else:
      newconvo = re.sub(orig, subst, last, count=1)
      pass
    pass
  except Exception as e:
    senderf("Regex badness: " + e.message)
    failure = True
    return True
  finally:
    if len(newconvo) > CONVO_MAX_LEN: # I picked a number fight me
      addconvo(last, speaker[0])
      senderf("FUCKSTICK was you all along")
      return True
    else:
      forbidden = ["\n", "\r", "\b", "\a", "\x7f", "\x00", "\xe2\x80\x8f"]
      for c in forbidden:
        if c in newconvo:
          senderf("FUCKSTICK is YOU")
          addconvo(last, speaker[0])
          return True
        pass
      pass      

    addconvo(newconvo, speaker[0])
    if not failure:
      senderf("Updated: " + newconvo)
      pass
    pass
  return True

def cmdmsg(senderf, channel, speaker, cmd, isact):
  if isact:
    return False

  if cmd == "convo":
    senderf(getconvo())
    return True
  elif cmd.startswith("convo add "):
    newconvo = cmd.split(" ", 2)[2]
    if len(newconvo) > CONVO_MAX_LEN:
      senderf("I'm afraid I can't do that: would truncate \"%s\"" % newconvo[400:])
      return True
    addconvo(newconvo, speaker[0])
    senderf("NOW WE'RE HAVING A GOOD TIME RIGHT")
    return True
  elif cmd.startswith("convo grep "):
    try:
      senderf(grepconvos(channel, cmd.split(" ", 2)[2]))
      pass
    except:
      senderf(speaker[0] + ": PYTHON REGEX DO YOU SPEAK IT")
      pass
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
    c = maybe_pop(speaker)
    if c == 0:
      senderf("YOU CANNOT KILL THAT IS ALREADY DEAD (no convos found)")
      pass
    elif c == 1:
      senderf("No convo found since last reload")
      pass
    elif c == 2:
      senderf("You weren't the last convoer, so you can't undo")
      pass
    else:
      senderf("Deleted: " + c)
      return c
    return True
  elif cmd.startswith("convo fix "):
    return convofix(cmd[len("convo fix "):], speaker, senderf)
  return False # main body

def unload():
  writedb()
  pass

######

loaddb()
