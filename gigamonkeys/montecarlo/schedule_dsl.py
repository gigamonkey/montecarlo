#!/usr/bin/env python

from dataclasses import dataclass
from typing import List


@dataclass
class Node:
    name: str


@dataclass
class Leaf(Node):
    low: int
    high: int

    def dump(self, indent, op):
        print(f"{' ' * indent * 2}{op} {self.name}: {self.low}-{self.high}\n")

    def map(self, f):
        return f(self, None)


@dataclass
class Tree(Node):
    children: List[Node]

    @classmethod
    def fromOp(cls, op):
        return Plus if op == "+" else Pipe

    def dump(self, indent, op):
        if self.name:
            print(f"{' ' * indent * 2}{op} {self.name}\n")
        for c in self.children:
            c.dump(indent + 1, self.op)

    def map(self, f):
        return f(self, [c.map(f) for c in self.children])


@dataclass
class Plus(Tree):
    op: str = "+"


@dataclass
class Pipe(Tree):
    op: str = "|"


def parse(lines):
    return to_schedule(None, grouped(strip(lines)))


def strip(lines):
    def keep(s):
        return s and s[0] != "#"

    return [line.rstrip() for line in lines if keep(line.strip())]


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
    for i in range(len(s)):
        if s[i] != " ":
            return i
    # Technically this can't actually happen since we've already
    # removed blank lines.
    return len(s)


def to_schedule(name, group):
    children = [node(x) for x in group]
    if not children:
        try:
            name, estimate = name.split(":")
        except Exception:
            raise Exception(f"Need estimate in leaf {name}")
        low, high = map(int, estimate.strip().split("-"))
        return Leaf(name, low, high)
    else:
        op = group[0][0][0]
        return Tree.fromOp(op)(name, children)


def node(x):
    name, children = x
    return to_schedule(name[2:], children)


if __name__ == "__main__":

    with open("foo.txt") as f:
        parse(f).dump(-1, None)
