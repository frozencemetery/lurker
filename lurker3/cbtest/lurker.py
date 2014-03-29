import module
from collections import defaultdict

def nop(*args, **kwargs):
    return

cmds = defaultdict(lambda : nop)
vals = defaultdict(dict)

def registergen(module):
    def register_(verb, action):
        cmds[verb] = action
    return register_

def putgen(module):
    def put_(key, value):
        vals[module][key] = value
    return put_

if __name__ == "__main__":
    module.register = registergen(module)
    module.put = putgen(module)
    module.run()

    cmds["convo"]("elision", "convo", "add wangs")
    print cmds["convo"], vals[module]
    pass
