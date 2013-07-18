# this loads a lurker interp with CLI interface provided by a backend
# this backend is a separate module, which is reloadable

import sys

import irc.irclib as irclib

from irc.irclib import debug, warn, verbose, prnt
from irc.irclib import BasicBehavior, SocketManager
from irc.irclib import IrcConnection, IrcListener

moddict = {}

def load(modname):
  if modname in moddict.keys():
    pass
  else:
    # try to load from modules/${modname}.py
    import modules.cmd
    exec("import modules." + modname + ' as ' + modname)
    moddict[modname] = locals()[modname]
    pass
  pass

def unload(modname):
  if modname not in moddict.keys():
    pass
  else:
    moddict[modname].unload(moddict[modname])
    del moddict[modname]
    pass
  pass

def reload(modname):
  unload(modname)
  load(modname)
  pass

# autoload modules
autoloadf = "modules/autoload"
for module in open(autoloadf, 'r').read():
  try:
    load(module)
    pass
  except:
    print("module '" + modname + "' failed to autoload")
    pass
  pass

def onMsg(channel, channame, speaker, msg):
  commandchar = '!'
  if msg[:1] == commandchar:
    executed = false
    for modname in moddict.keys():
      curmod = moddict[modname]
      e = curmod.cmdmsg(curmod, 
                        channel, channame, speaker, msg[1:])
      executed = executed or e
      pass
    if not executed:
      act(channel, "doesn't know how to " + msg[:1])
      pass
    pass
  else:
    for modname in moddict.keys():
      moddict[modname].regmsg(moddict[modname],
                              channame, speaker, msg)
      pass
    pass

def onAct(channel, channame, speaker, msg):
  for modname in moddict.keys():
    moddict[modname].action(moddict[modname],
                            channame, speaker, msg)
    pass
  pass

class Lurker(IrcListener):
  def __init__(self):
    self.conn = IrcConnection("irc.foonetic.net", 6667,
                              nick="lurker3", user="lurker3")
    bb = BasicBehavior(["#lurkertest"])
    self.conn.add_listener(bb)
    self.conn.add_listener(self)
    pass

  def start(self):
    self.conn.connect()
    pass

  def stop(self):
    self.conn.disconnect()
    pass

  def on_chan_msg(self, owner, sender, channel, message):
    owner.send(channel, message)
    pass

  def send(self, msg):
    self.conn.send.privmsg("#lurkertest", msg)
    pass
  pass

def main():
  irclib.set_silent(False)
  irclib.set_warn(True)
  irclib.set_debug(True)
  b = Lurker()
  b.start()
  s = ""
  try:
    while True:
      s = raw_input()
      b.send(s)
      pass
    pass
  except (KeyboardInterrupt, EOFError):
    b.stop()
    SocketManager.exit()
    pass
  pass

if __name__ == "__main__":
  main()
