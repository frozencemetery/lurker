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
