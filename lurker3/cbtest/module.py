from interf import *

def convo(dude, arg0, argv):
    put("lastconvoer", dude)
    return
    
def run():
    register("convo", convo)
    return
