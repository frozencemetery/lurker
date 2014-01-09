from module import *

def cmdmsg(senderf, channel, speaker, cmd, isact):
    if isact:
        return False
    if cmd == "static":
        senderf("ssssssssssssSSSSSSSSSSSSHHHHHHHHHHHHHHHHHHHHHHHHHHHHHhsssssssssssssssssssss")
        return True
    return False

def unload():
    pass
