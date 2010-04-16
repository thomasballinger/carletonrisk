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
if len(args)<3:
    print 'you need at least from where and to where'
    sys.exit()
if len(args)>4:
    print 'do you need a usage statement?  Try this command with no args'
    sys.exit()

g=loader.load()
if len(args) == 3:
    fromCountry = args[1]
    toCountry = args[2]
    if not g.isCountry(fromCountry):
        print 'error processing order'
        sys.exit()
    howMany = (g.getTroops(fromCountry)-1)
    print 'Fortifying from',fromCountry,'to',toCountry,'with',howMany,'troops'
elif len(args) == 4:
    fromCountry = args[1]
    toCountry = args[2]
    howMany = int(args[3])
else:
    print "logic error; shouldn't be here"
if g.fortify(fromCountry, toCountry, howMany, player):
    loader.save(g)
else:
    print 'error processing order'

