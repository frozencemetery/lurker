import json as J

from module import *

unhugged = []

nohugs_file = "modules/rsrc/nohugs.db"

def loaddb():
    global unhugged

    try:
        with open(nohugs_file, 'r') as f:
            unhugged = J.load(f)
            pass
        pass
    except:
        print "Failed to load nohugs.db; corruption possible!"
        pass
    return

def writedb():
    global unhugged

    try:
        with open(nohugs_file, 'w') as f:
            J.dump(unhugged, f)
            pass
        pass
    except:
        print "Failed to dump nohugs.db; hugs for everyone!"
        pass
    return

def cmdmsg(senderf, channel, speaker, cmd, isact):
    global unhugged

    if cmd == "hug me never":
        if speaker[0] in unhugged:
            senderf(speaker[0] + ": psh, like I'd forget a thing like that")
            return True

        unhugged.append(speaker[0])
        writedb()
        senderf(speaker[0] + ": I will remember that")
        return True
    elif cmd.startswith("hug "):
        name = cmd.split(" ", 1)[1]
        if name.strip() == "me":
            name = speaker[0]
            pass
        if name in unhugged:
            senderf("refuses to violate " + name, isact=True)
            return True
        senderf("hugs " + name, isact=True)
        return True
    return False

def unload():
    writedb()
    return

######

loaddb()
