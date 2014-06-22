from module import *

S="ssssssssssssSSSSSSSSSSSSHHHHHHHHHHHHHHHHHHHHHHHHHHHHHhsssssssssssssssssssss"

def cmdmsg(senderf, channel, speaker, cmd, isact):
    if isact:
        return False
    if cmd == "static":
        senderf(S)
        return True
    return False

def unload():
    pass
