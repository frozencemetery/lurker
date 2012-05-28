# this loads a lurker interp with CLI interface provided by a backend
# this backend is a separate module, which is reloadable

import sys

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
    print("module '" modname + "' failed to autoload")
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
