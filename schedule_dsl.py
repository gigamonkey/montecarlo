#!/usr/bin/env python

from schedule import *


class Plus:
    def __init__(self, name, children):
        self.name = name
        self.children = children

    def dump(self, indent=-1, op=None):
        if self.name:
            print(f"{' ' * indent * 2}{op} {self.name}\n")
        for c in self.children:
            c.dump(indent + 1, "+")

    def __repr__(self):
        return ["PLUS", self.name, self.children].__repr__()


class Pipe:
    def __init__(self, name, children):
        self.name = name
        self.children = children

    def dump(self, indent=-1, op=None):
        if self.name:
            print(f"{' ' * indent * 2}{op} {self.name}\n")
        for c in self.children:
            c.dump(indent + 1, "|")

    def __repr__(self):
        return ["PIPE", self.name, self.children].__repr__()


class Leaf:
    def __init__(self, name, low, high):
        self.name = name
        self.low = low
        self.high = high

    def dump(self, indent=-1, op=None):
        print(f"{' ' * indent * 2}{op} {self.name}: {self.low}-{self.high}\n")

    def __repr__(self):
        return ["LEAF", self.name].__repr__()


def parse(lines):
    return to_schedule(None, grouped(strip(lines)))


def strip(lines):
    def keep(s):
        stripped = s.strip()
        return stripped and stripped[0] != "#"

    return [line for line in lines if keep(line)]


def grouped(lines):
    groups = []
    s = 0
    while s < len(lines):
        line = lines[s]
        end = end_of_group(lines, s)
        groups.append((line.strip(), grouped(lines[s + 1 : end])))
        s = end
    return groups


def end_of_group(lines, s):
    indent = indentation(lines[s])
    s += 1
    while s < len(lines) and indentation(lines[s]) > indent:
        s += 1
    return s


def indentation(s):
    i = 0
    while i < len(s) and s[i] == " ":
        i += 1
    return i


def to_schedule(name, group):
    children = [node(x) for x in group]
    if not children:
        try:
            name, estimate = name.split(":")
        except:
            raise Exception(f"Need estimate in leaf {name}")
        low, high = map(int, estimate.strip().split("-"))
        return Leaf(name, low, high)
    else:
        op = group[0][0][0]
        if op == "+":
            return Plus(name, children)
        elif op == "|":
            return Pipe(name, children)
        else:
            raise Exception(f"Bad op: {op}")


def node(x):
    name, children = x
    return to_schedule(name[2:], children)





if __name__ == "__main__":

    with open("foo.txt") as f:
        lines = [line[:-1] for line in f]

    t = parse(lines)

    # print(t)
    t.dump()
