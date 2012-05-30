ALPHA = r"[a-zA-Z]"
NUM = "[0-9]"
SPACE = r" +"
SPECIAL = r"[-\[\]\\`^\{\}]"

ALPHANUM = "(?:" + ALPHA + "|" + NUM + ")"
ALPHANUMDASH = "(?:" + ALPHA + "|" + NUM + "|-)"
CRLF = r"\r\n"
NICKCH = "(?:"+ ALPHA + "|" + NUM + "|" + SPECIAL + ")"

HOST = ALPHA + "(?:" + ALPHANUMDASH + "+\.)+" + ALPHANUMDASH + "*" +\
       ALPHANUM
SERVERNAME = HOST
USER = r"[^ @]+"
COMMAND = "(?:" + ALPHA + "+|" + NUM * 3 + ")"
MIDDLE = r"[^\r\n: ][^\r\n ]*"
NICK = ALPHA + "+" + NICKCH + "*"
PREFIX = "(?:" + SERVERNAME + ")|(?:" + NICK + \
          "(?:!" + USER + "@" + HOST + ")?)"
TRAILING = r"[^\r\n]*"

PARAMS = SPACE + "(?:" + MIDDLE + SPACE + ")*" + "(?::" + TRAILING + ")?"

MESSAGE = "(?::" + "(" + PREFIX + ")" + SPACE + ")?" +\
          "(" + COMMAND + ")" +\
          "(" + PARAMS + ")" + CRLF


class UncasedDict :
    def __init__(self) :
        self.keyvals = []

    def __getitem__(self, key) :
        assert(isinstance(key,str))
        for keyval in self.keyvals :
            if keyval[0].lower() == key.lower() :
                return keyval[1]
        raise KeyError(key)

    def __setitem__(self, key, val) :
        assert(isinstance(key,str))
        for keyval in self.keyvals :
            if keyval[0].lower() == key.lower() :
                self.keyvals.remove(keyval)
        self.keyvals.append((key,val))

    def keys(self) :
        return [keyval[0] for keyval in self.keyvals]
