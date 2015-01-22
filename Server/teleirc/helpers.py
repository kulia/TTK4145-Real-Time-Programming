#!/usr/bin/python

def set_reflex(fun):
    """Method decorator. Creates a field with that name, and runs the function on set."""
    fun.value = None
    def fget(self):
        return fun.value
    def fset(self, value):
        fun.value = value
        fun(self, value)
    return property(fget, fset, doc=fun.__doc__)

