#!/usr/bin/env python
# vim: tw=0 ts=4 sw=4 sts=4 expandtab
# ----------------------------------------------------------------------
# Git Log Graph
#
# Author: Ryosuke SEKIDO <ryosuke@sekido.info>
# ----------------------------------------------------------------------
# License:
#
# The MIT License
#
# Copyright (c) 2008 Ryosuke SEKIDO
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ----------------------------------------------------------------------
# Usage:
#
# % git log --raw --pretty=raw | ./git-log-graph.py | dot -Tpng -o graph.png
#
# ----------------------------------------------------------------------
import sys
import re

# ----------------------------------------------------------------------
# Commit Object
#
class Commit:
    # constructor
    def __init__(self, hash):
        self.hash = hash[0:7]
        self.comment = ""
        self.blobs = []
        self.parents = []

    # append blob object
    def addBlob(self, blob):
        self.blobs.append(blob)

    # append parent commit object
    def addParent(self, commit):
        self.parents.append(commit)

# ----------------------------------------------------------------------
# Blob Object
#
class Blob:
    # constructor
    def __init__(self, name, hash, prev):
        self.name = name
        self.hash = hash.strip(".")
        self.prev = prev.strip(".")

# ----------------------------------------------------------------------
# Output as dot format
#
def output(head):
    # header
    print "digraph git {"

    # commit tree row
    h = head
    while len(h.parents) > 0:
        if h != head:
            print "->",
        print '"%s"' % h.hash,
        h = h.parents[0]
    print '-> "%s";' % h.hash

    # blob tree
    h = head
    while len(h.parents) > 0:
        print '"%s" [shape = box];' % h.hash
        for b in h.blobs:
            if not b.prev.startswith("00000"):
                print '"%s" -> "%s";' % (b.hash, b.prev)
        h = h.parents[0]
    print '"%s" [shape = box];' % h.hash

    # combine commit and blobs
    h = head
    while len(h.parents) > 0:
        print '{rank = same; "%s";' % (h.hash),
        for b in h.blobs:
            print '"%s";' % b.hash,
        print "}"
        h = h.parents[0]

    # footer
    print "}"

# ----------------------------------------------------------------------
# Parse input data
#
def parse(lines):
    # head
    head = None
    # hash of current parsing commit
    cur = ""
    # dictionary of commits
    commit = {}

    # parse each line
    for line in lines:
        # begining commit part
        if line.startswith('commit '):
            a, hash = line.strip().split(' ')
            cur = hash
            if head == None:
                c = Commit(cur)
                commit[cur] = c
                head = c
        # parent part
        elif line.startswith('parent '):
            a, hash = line.strip().split(' ')
            c = Commit(hash)
            commit[hash] = c
            commit[cur].addParent(c)
        # comment part
        elif line.startswith('    '):
            pass
        # blob part
        elif line.startswith(':'):
            a, b, prev, hash, mode, name = re.compile(r'\s').split(line.strip(), 6)
            blob = Blob(name, hash, prev)
            commit[cur].addBlob(blob)
    return head

# ----------------------------------------------------------------------
# Read data
#
def read_log():
    lines = sys.stdin.readlines()
    return lines

# ----------------------------------------------------------------------
# MAIN
#
def main():
    # read log data
    lines = read_log()
    # parse data and get head commit object
    head = parse(lines)
    # output as dot format
    output(head)

# trigger
if __name__ == "__main__":
    main()
