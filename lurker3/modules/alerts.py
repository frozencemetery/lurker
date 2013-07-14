import time
import cPickle

from module import *

alertsdb = "rsrc/alerts.dict"

lookupt = {}

f = open(alertsdb, 'r')
lookupt = cPickle.load(f)
f.close()

def lookup(self, name):
  try:
    val = lookupt[name]
    return (True, val)
  except:
    return (False, [])
  pass

