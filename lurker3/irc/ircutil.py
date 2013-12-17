import sys

global __DEBUG, __VERBOSE, __SILENT, __WARN, __FILE

__DEBUG = False
__VERBOSE = False
__SILENT = False
__WARN = False
__FILE = sys.stdout

ACTION = chr(7) + "ACTION" + chr(7)

# character classes expressions
ALPHA = r"[a-zA-Z]"
NUM = "[0-9]"
SPACE = r" +"
SPECIAL = r"[\[\]\\`^\{\}_\|]"
CRLF = r"\r\n"

# unions of above
ALPHANUM = "(?:" + ALPHA + "|" + NUM + ")"
ALPHANUMDASH = "(?:" + ALPHA + "|" + NUM + "|-)"
NICKCH = "(?:"+ ALPHA + "|" + NUM + "|" + SPECIAL + "|" + "[-]" + ")"
INITNICKCH = "(?:"+ ALPHA + "|" + SPECIAL + ")"

# first order tokens
HOST =\
    ALPHA + "(?:" + ALPHANUMDASH + "+\.)+" + ALPHANUMDASH + "*" + ALPHANUM
SERVERNAME = HOST
USER = r"[^ @]+"
COMMAND = "(?:" + ALPHA + "+|" + NUM * 3 + ")"
MIDDLE = r"[^\r\n: ][^\r\n ]*"
NICK = INITNICKCH + "+" + NICKCH + "*"
TRAILING = r"[^\r\n]*"

# second order tokens
PREFIX =\
    "(?:" + SERVERNAME + ")|(?:" + NICK + "(?:!" + USER + "@" + HOST + ")?)"

PARAMS = SPACE + "(?:" + MIDDLE + SPACE + ")*" + "(?::" + TRAILING + ")?"

MESSAGE = "(?::" + "(" + PREFIX + ")" + SPACE + ")?" +\
          "(" + COMMAND + ")" +\
          "(" + PARAMS + ")" + CRLF
PARAMGRP =\
    SPACE + "((?:" + MIDDLE + SPACE + ")*)" + "(?::(" + TRAILING + "))?"
PREFIXGRP = "(" + SERVERNAME + ")|(?:(" + NICK + \
             ")(?:!(" + USER + ")@(" + HOST + "))?)"

# dictionary that stores keys in a case-insensitive manner
class UncasedDict:
  def __init__(self):
    self.keyvals = []
    pass

  def __getitem__(self, key):
    assert(isinstance(key,str))
    for keyval in self.keyvals:
      if keyval[0].lower() == key.lower():
        return keyval[1]
      pass
    raise KeyError(key)

  def __setitem__(self, key, val):
    assert(isinstance(key,str))
    for keyval in self.keyvals:
      if keyval[0].lower() == key.lower():
        self.keyvals.remove(keyval)
        pass
      pass
    self.keyvals.append((key,val))
    pass

  def keys(self) :
    return [keyval[0] for keyval in self.keyvals]
  pass

# class for any kind of error we might run across
class IrcError(Exception):
  def __init__(self, value):
    self.value = value
    pass

  def __str__(self):
    if issubclass(type(self.value),Exception):
      return type(self.value).__name__+": " + str(self.value)
    else:
      return str(self.value)
    pass
  pass

# nearly-empty class whose only purpose is to hold lambdas
# TODO: consider metaclassing
class IrcSender(object):
  def __init__(self, owner):
    self.owner = owner
    pass
  pass

def output_to_stdout():
  __FILE = sys.stdout
  pass

def debug(*args):
  if __DEBUG and not(__SILENT):
    __FILE.write( "[D] " + " ".join([str(arg) for arg in args]))
    __FILE.write( "\n")
    pass
  pass

def warn(*args):
  if __WARN and not (__SILENT):
    __FILE.write( "[W] " + " ".join([str(arg) for arg in args]))
    __FILE.write( "\n")
    pass
  pass

def verbose(*args):
  if __VERBOSE and not(__SILENT):
    __FILE.write( "[V] " + " ".join([str(arg) for arg in args]))
    __FILE.write( "\n")
    pass
  pass

def prnt(*args):
  if not(__SILENT):
    __FILE.write( "[N] " + " ".join([str(arg) for arg in args]))
    __FILE.write( "\n")
    pass
  pass

def wrap(fun, *args, **kwargs):
  try:
    fun(*args,**kwargs)
    pass
  except Exception as e:
    debug("Error in listener:",e)
    pass
  pass
