# coding=utf8

import random
import math
from module import *

class DiceError(Exception):
  def  __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

def roll(t):
  testa = t[1].split("+", 1) #
  testb = t[1].split("-", 1) #
  if len(testa[0]) > len(testb[0]):
    numtoroll = int(t[0])
    sidenum = int(testb[0])
    bonus = -int(testb[1])
    pass
  elif len(testa[0]) < len(testb[0]): #testa's split is better
    numtoroll = int(t[0])
    sidenum = int(testa[0])
    bonus = int(testa[1])
    pass
  else: # the two were equal; in other words, no bonus
    numtoroll = int(t[0])
    sidenum = int(testa[0])
    bonus = 0
    pass
  if numtoroll < 0:
    raise DiceError("I can't roll a negative number of dice.")
  if sidenum < 1:
    raise DiceError("I can't roll a die with fewer than 1 side.")
  if sidenum == 1:
    return numtoroll + bonus
  if numtoroll <= 1000:
    res = bonus
    for i in xrange(numtoroll):
      res += random.randint(1, sidenum)
      pass
    return res
  # lots of dice: approximate with Gaussian
  return bonus + int(round(random.gauss(
        numtoroll*(sidenum+1)/2.0,
        math.sqrt(numtoroll*(sidenum**2 - 1)/12.0))))

def cmdmsg(senderf, channel, speaker, cmd, isact):
  if isact:
    return False
  if not cmd.startswith("roll "):
    return False
  try:
    s = cmd.split(" ", 1)
    t = s[1].split("d", 1)
    counter = roll(t)
    pass
  except DiceError as e:
    senderf(e.value)
    pass
  except:
    senderf("Syntax is: \"roll xdy[±z]\".")
    pass
  else:
    senderf("I rolled " + str(counter) + " for " + speaker[0] + ".")
    pass
  return True

def unload():
  pass
