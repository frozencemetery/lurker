import random

from module import *

convodb = "rsrc/convo.db"

convos = []

f = open(convodb, 'r')
for line in f:
  convos.append(line)
  pass
f.close()

def getconvo(self):
  ind = random.randint(0, len(self.convos) - 1)
  return self.convos[ind]

def addconvo(self, convo):
  self.convos.append(convo)
  f = open(convodb, 'a')
  f.write(convo + '\n')
  f.close()
  pass

def cmdmsg(self, channel, channame, speaker, cmd):
  if cmd == "convo":
    channel.msg(getconvo(self))
    return True
  elif cmd[:10] == "convo add ":
    addconvo(self, cmd.split(" ", 2)[2])
    channel.msg("NOW WE'RE HAVING A GOOD TIME RIGHT")
    return True
  else:
    return False
  pass
