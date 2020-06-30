#!/usr/bin/env python

import sys
import importlib

class C: pass

class_type = type(C)

TO_STRIP = "gigamonkeys.montecarlo"


def load_classes(modules):
    classes = []

    for module in modules:
        module = importlib.import_module(module)

        for attr in dir(module):
            what = getattr(module, attr)
            if type(what) == class_type:
                classes.append(what)

    return classes


def name(c):
    module = c.__module__
    name = c.__name__

    if module == TO_STRIP:
        return f'"{name}"'
    else:
        if module.startswith(TO_STRIP + "."):
            module = module[len(TO_STRIP + ".") :]
        return f'"{module}.{name}"'


def graph(classes, pathfn):

    print("digraph G {")
    print('  rankdir="BT";')
    print('  concentrate="true";')
    for c in classes:
        path = pathfn(c)
        print("  " + " -> ".join(name(p) for p in path) + ";")
    print("}")


if __name__ == "__main__":


    classes = load_classes([
        "gigamonkeys.montecarlo",
        "gigamonkeys.montecarlo.calendar",
        "gigamonkeys.montecarlo.deadline",
    ])


    if sys.argv[1] == "super":
        graph(classes, lambda c: (c,) + c.__bases__)
    elif sys.argv[1] == "mro":
        graph(classes, lambda c: c.__mro__)
    else:
        exit(f"Unrecognized output: {sys.argv[1]}")
