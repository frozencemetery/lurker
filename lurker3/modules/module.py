# default functions for modules to import
# e.g.,
#   from module import *
# then override the relevant functions

def cmdmsg(senderf, channame, speaker, cmdstr, isact):
  return False

def regmsg(channame, speaker, cmdstr, isact):
  return

def userjoin(channame, joiner):
  return

def userpart(channame, parter):
  return

def botjoin(channame):
  return

def botpart(channame):
  return

def unload():
  return
