#!/usr/bin/env python

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
