import random
import re

from collections import defaultdict
from module import *
from ircutil import NICK

CONVO_MAX_LEN = 400
CONVODB = "modules/rsrc/convo.db"

convos = []
lastgrep = {} # remaining convos, associated by location
lastseen = defaultdict(dict) # last lines, by channel, then user
lastconvo = None # last convo made
lastconvoer = None # last person who convod, to avoid undoing the wrong one
oldconvos = None # convo before last add operation

def writedb():
    return open(CONVODB, 'w').write('\n'.join(convos) + '\n')

def loaddb():
    global convos

    try:
        convos = open(CONVODB, 'r').read().split('\n')
        pass
    except:
        print "Failed to load convo.db; corruption possible!"
        return
    finally:
        convos = [] if convos is None else convos
        pass

    # trailing newline from editors.  Thrashes slightly, but hey.
    if convos[-1] == "":
        del(convos[-1])
        writedb()
        pass
    print "loaded okay"
    return

def convo(senderf):
    try:
        senderf(random.choice(convos))
        pass
    except:
        senderf("CONVO.DB EMPTY; WORST PARTY EVER")
        pass
    return True

def convonext(senderf, channel):
    global lastgrep

    if not channel in lastgrep.keys() :
        senderf("No extant queries")
        return True
    if len(lastgrep[channel]) == 0 :
        senderf("No (more) matches found.")
        return True
    fst, lastgrep[channel] = lastgrep[channel][0], lastgrep[channel][1:]
    senderf(fst + (" {1}[+{0}]{1}".format(len(lastgrep[channel]), chr(2))))
    return True

def convogrep(senderf, channel, regex):
    global lastgrep

    try:
        insence = re.IGNORECASE
        rl = list(regex)
        i = 0
        while i < len(rl):
            if rl[i] == '\\':
                i += 2
                continue
            elif rl[i].isupper():
                insence = 0
                break
            i += 1
            pass
        matching = [line for line in convos
                    if re.match(".*" + regex + ".*", line, insence)]
        random.shuffle(matching)
        lastgrep[channel] = matching
        return convonext(senderf, channel)
    except:
        senderf(speaker + ": PYTHON REGEX DO YOU SPEAK IT")
        pass
    return True

def convolast(senderf, channel, pattern, speaker):
    match = re.match("^<?([@~%+ ]?)(" + NICK + ").*$", pattern)
    if not match:
        senderf("Invalid pattern: '%s'" % pattern)
        return True

    prefix, nick = match.groups()
    if nick.lower() not in lastseen[channel].keys():
        senderf("Could not find nick '%s'" % nick)
        return True

    last = lastseen[channel][nick.lower()]
    if last["isact"]:
        return convoadd(senderf, speaker,
                        "* %s %s" % (last["nick"], last["line"]))

    if prefix == "" :
        return convoadd(senderf, speaker, last["line"]);

    return convoadd(senderf, speaker,
                    "<%s%s> %s" % (prefix, last["nick"], last["line"]))

def maybe_pop(speaker):
    global convos
    global lastconvo
    global lastconvoer

    if convos == []:
        return 0
    elif lastconvo == None:
        return 1
    elif lastconvoer.lower() != speaker.lower():
        return 2

    convos = oldconvos
    writedb()
    z = lastconvo
    lastconvo = None
    return z

# The all new iSeven, from Apple.
def iseven(s):
    even = True
    for c in s[::-1]:
        if c != '\\':
            break
        even = not even
        pass
    return even

def convofix(cmd, speaker, senderf):
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
        if option:
            newconvo = re.sub(orig, subst, last)
            pass
        else:
            newconvo = re.sub(orig, subst, last, count=1)
            pass
        pass
    except Exception as e:
        senderf("Regex badness: " + e.message)
        insert_convo(senderf, last)
        return True

    if not convoadd(senderf, speaker, newconvo):
        insert_convo(senderf, last)
        return True

    return True

# False with yelling on failure
def insert_convo(senderf, newconvo):
    global oldconvos

    if not newconvo:
        senderf("Empty convo, ignoring")
        return False
    elif len(newconvo) > CONVO_MAX_LEN:
        senderf("I'm afraid I can't do that: would truncate \"%s\"" \
                % newconvo[400:])
        return False

    forbidden = ["\n", "\r", "\b", "\a", "\x7f", "\x00", "\x03",
                 "\xe2\x80\x8f"]
    for c in forbidden:
        if c in newconvo:
            senderf("FUCKSTICK is YOU")
            return False
        pass

    oldconvos = convos[:]
    convos.append(convo)
    open(CONVODB, 'a').write(newconvo + '\n')
    return True

def convoadd(senderf, speaker, newconvo):
    global lastconvo
    global lastconvoer

    if not insert_convo(senderf, newconvo):
        return True

    lastconvo = newconvo
    lastconvoer = speaker

    senderf("NOW WE'RE HAVING A GOOD TIME RIGHT")
    return True

def convoundo(senderf, speaker):
    c = maybe_pop(speaker)
    if c == 0:
        senderf("YOU CANNOT KILL THAT IS ALREADY DEAD (no convos found)")
        return True
    elif c == 1:
        senderf("No convo found since last reload")
        return True
    elif c == 2:
        senderf("You weren't the last convoer, so you can't undo")
        return True
    senderf("Deleted: " + c)
    return True

def convoshow(senderf):
    if lastconvo:
        senderf(lastconvo)
        pass
    else:
        senderf("No convo added since last reload")
        pass
    return True

def cmdmsg(senderf, channel, speaker, cmd, isact):
    if isact:
        return False

    if cmd == "convo":
        return convo(senderf)
    elif cmd.startswith("convo add "):
        return convoadd(senderf, speaker[0], cmd.split(" ", 2)[2])
    elif cmd.startswith("convo grep "):
        return convogrep(senderf, channel, cmd.split(" ", 2)[2])
    elif cmd == "convo next":
        return convonext(senderf, channel)
    elif cmd.startswith("convo last "):
        return convolast(senderf, channel, cmd.split(" ", 2)[2], speaker[0])
    elif cmd == "convo show":
        return convoshow(senderf)
    elif cmd == "convo undo":
        return convoundo(senderf, speaker[0])
    elif cmd.startswith("convo fix "):
        return convofix(cmd.split(" ", 2)[2], speaker[0], senderf)
    return False

def regmsg(channel, nick, line, isact):
    global lastseen

    lastseen[channel][nick[0].lower()] = {
        "line": line, "nick": nick, "isact": isact
    }
    pass

def unload():
  writedb()
  pass

######

loaddb()
