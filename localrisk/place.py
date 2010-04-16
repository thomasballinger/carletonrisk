#!/usr/bin/env python
import game
import loader
import sys
import os
from asciiArt import shout

#sys.argv = ['place.py','USA','1']

player = os.getlogin()
country = None
howMany = 0

args = sys.argv
if len(args)<2:
    print 'you need to specify where'
    sys.exit()
elif len(args) == 2:
    country = args[1]
    howMany = 1 
elif len(args) == 3:
    country = args[1]
    howMany = int(args[2])
else:
    print 'usage: <Command> Country [howMany]'

g=loader.load()
if g.reinforce(country,howMany,player):
    loader.save(g)
    if g.reinforcementsToPlace[player]>0:
        print 'Reinforcements yet to place:',g.reinforcementsToPlace[player]
else:
    print 'error processing order'

