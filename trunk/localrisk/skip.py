#!/usr/bin/env python
import game
import loader
import sys
import os
from asciiArt import shout

player = os.getlogin()
fromCountry = None
toCountry = None
howMany = 0

args = sys.argv
if len(args)>1:
    print 'do you need a usage statement?  Try this command with no args'
    sys.exit()

g=loader.load()
if g.skip(player):
    loader.save(g)
else:
    print 'error processing order'

