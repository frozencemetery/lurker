def register(verb, action, *args):
    print verb, "==>", action, "but only when", args
    return

def get(key):
    print "Tried to get", key, "but no kv store"
    return

def put(key, value):
    print "Tried to put", key, "==>", value, "but no kv store"
    return

