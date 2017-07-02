#!/usr/bin/python

# this loads a lurker interp with CLI interface provided by a backend

import cmd
import readline
import sys

import irc.irclib as irclib

from irc.irclib import debug, warn, verbose, prnt
from irc.irclib import BasicBehavior, SocketManager
from irc.irclib import IrcConnection, IrcListener

def frob_sender(owner, sender):
  privlam = lambda message, isact=False: \
      owner.send.privmsg(sender[0], message) if not isact \
      else owner.send.action(sender[0], message)
  new = list(sender)
  new.append(privlam)
  new = tuple(new)
  return new

class Lurker(IrcListener, cmd.Cmd):
  moddict = None
  autoloadf = "modules/autoload"
  prompt = "=||> "

  def postcmd(self, stop, line):
    if stop or line == "EOF" or line == "exit":
      return True
    return False

  def do_exit(self, line):
    print "Exiting..."
    return

  def do_EOF(self, line):
    return self.do_exit(line)

  def do_load(self, modname):
    if modname in self.moddict.keys():
      pass
    else:
      # try to load from modules/${modname}.py
      # from http://docs.python.org/2/library/functions.html#__import__:
      #
      #   When the name variable is of the form package.module, normally, the
      #   top-level package (the name up till the first dot) is returned, not
      #   the module named by name. However, when a non-empty fromlist
      #   argument is given, the module named by name is returned.

      self.moddict[modname] = \
          __import__("modules." + modname, fromlist = ["_"])
      pass
    pass

  def do_unload(self, modname):
    if modname not in self.moddict.keys():
      pass
    else:
      self.moddict[modname].unload()
      del self.moddict[modname]
      pass
    pass

  def do_reload(self, modname):
    self.do_load(modname) # prevents explosion; nop if loaded
    reload(self.moddict[modname])
    pass

  def __init__(self):
    # Python's multiple inheritance doesn't understand what's going on here,
    # so we need to be explicit
    cmd.Cmd.__init__(self) # initialize cmd stuff
    pass

  def start(self, server, port, nick, user, channels, ssl):
    self.conn = IrcConnection(server, int(port),
                              nick, user, use_ssl=ssl)
    bb = BasicBehavior(channels)
    self.conn.add_listener(bb)
    self.conn.add_listener(self)

    # autoload modules
    self.moddict = {}
    with open(self.autoloadf, 'r') as f:
      for module in f.read().split("\n"):
        if module == "":
          continue

        try:
          self.do_load(module)
          print("autoloaded module: " + module)
          pass
        except Exception as e:
          print("module '" + module + "' failed to autoload: " + str(e))
          pass
        pass
      pass

    self.conn.connect()
    pass

  def stop(self):
    self.conn.disconnect()
    pass

  # IrcListener stuff

  def on_chan_msg(self, owner, sender, channel, message, isact):
    sender = frob_sender(owner, sender)
    if message[0] == '!':
      # The module earlier in the alphabet gets priority.  I don't like this
      # and neither do you.  We do need to enforce the constraint that only
      # one gets to speak each time something is said.  Don't load modules
      # that conflict.

      # http://achewood.com/index.php?date=03042004

      message = message[1:] # del(message[0])
      msglam = lambda message, isact=False: \
          owner.send.privmsg(channel, message) if not isact \
          else owner.send.action(channel, message)
      acted = False
      for mod in self.moddict.values():
        acted = mod.cmdmsg(msglam, channel, sender, message, isact)
        if acted:
          break
        pass
      if not acted:
        msglam("HELP I DON'T KNOW HOW TO %s!" % message.upper())
        pass
      pass

    else:
      for mod in self.moddict.values():
        mod.regmsg(channel, sender, message, isact)
        pass
      pass
    pass

  def on_priv_msg(self, owner, sender, message, isact):
    sender = frob_sender(owner, sender)
    if message[0] == '!':
      message = message[1:] # del(message[0])
      msglam = sender[-1]
      acted = False
      for mod in self.moddict.values():
        acted = mod.cmdmsg(msglam, sender[0], sender, message, isact)
        if acted:
          break
        pass
      if not acted:
        msglam("HELP I DON'T KNOW HOW TO %s!" % message.upper())
        pass
      pass
    else:
      for mod in self.moddict.values():
        mod.regmsg(sender[0], sender, message, isact)
        pass
      pass
    pass

  def on_join(self, owner, sender, channel):
    sender = frob_sender(owner, sender)
    if sender[0] == owner.nick:
      for mod in self.moddict.values():
        mod.botjoin(channel)
        pass
      return

    for mod in self.moddict.values():
      mod.userjoin(channel, sender)
      pass
    return

  def on_part(self, owner, sender, channel, message):
    sender = frob_sender(owner, sender)
    if sender[0] == owner.nick:
      for mod in self.moddict.values():
        mod.botpart(channel)
        pass
      return

    for mod in self.moddict.values():
      mod.userpart(channel, sender, message)
      pass
    return
  pass

def main(argv):
  irclib.set_silent(False)
  irclib.set_warn(True)
  irclib.set_debug(False)

  while True:
    if argv[1] == "-s":
      irclib.set_silent(True)
      del(argv[1])
      pass
    elif argv[1] is "-w":
      irclib.set_warn(False)
      del(argv[1])
      pass
    elif argv[1] == "-d":
      irclib.set_debug(True)
      del(argv[1])
      pass
    else:
      break
    pass

  if len(argv) < 6:
    print "./lurker.py [args] server port nick user [channel...]"
    print "args: -s :: make lurker silent (no output)"
    print "args: -w :: disable warnings (superseded by -s)"
    print "args: -d :: enable debug spew (default off)"
    return 1

  b = Lurker()
  b.start(argv[1], argv[2], argv[3], argv[4], argv[5:], True)

  try:
    b.cmdloop()
    pass
  except:
    print "Exiting"
    pass
  b.stop()
  SocketManager.exit()
  pass

if __name__ == "__main__":
  main(sys.argv)
  pass
