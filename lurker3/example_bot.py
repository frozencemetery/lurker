import irc.irclib as irclib
from irc.irclib import debug, warn, verbose, prnt
from irc.irclib import BasicBehavior, SocketManager
from irc.irclib import IrcConnection, IrcListener

class ExampleBot(IrcListener) :
  def __init__(self) :
    self.conn = IrcConnection("irc.foonetic.net",6667,nick="lurker3",user="lurker3")
    bb = BasicBehavior(["#lurkertest"])
    self.conn.add_listener(bb)
    self.conn.add_listener(self)
    pass

  def start(self) :
    self.conn.connect()
    pass

  def stop(self) :
    self.conn.disconnect()
    pass

  def on_chan_msg(self, owner, sender, channel, message) :
    owner.send.privmsg(channel, message)
    pass

  def send(self, msg) :
    self.conn.send.privmsg("#lurkertest",msg)
    pass
  pass

def main():
  irclib.set_silent(False)
  irclib.set_warn(True)
  irclib.set_debug(True)
  b = ExampleBot()
  b.start()
  s = ""
  while s != "X" :
    s = raw_input()
    b.send(s)
    pass
  b.stop()
  SocketManager.exit()
  pass

if __name__ == "__main__":
  main()
