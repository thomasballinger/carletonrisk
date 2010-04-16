#!/usr/bin/env python
import game
import loader
import sys
import os
from asciiArt import shout

# eventually allow syntax like
# attack Netherlands from Germany with 6
# attack Netherlands 

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
    howMany = min(3,(g.getTroops(fromCountry))-1)
    print 'attacking',toCountry,'from',fromCountry,'with',howMany
elif len(args) == 4:
    fromCountry = args[1]
    toCountry = args[2]
    howMany = int(args[3])
else:
    print "logic error; shouldn't be here"
output=g.attack(fromCountry,toCountry,howMany,player)
if output:
    print 'Attacking',output['to'],'from',output['from']+'...'
    print 'attacker rolls:',output['attack']
    print 'defender rolls:',output['defense']
    print 'attackers lost:',output['attackersKilled']
    print 'defenders lost:',output['defendersKilled']
    if output["captured"]:
        print "Territory Captured!"
    loader.save(g)
    print 
    if g.getTroops(fromCountry)>1 and output['captured']:
        while True:
            howMany = int(raw_input('Move how many additional troops? ('+str(0)+'-'+str(g.getTroops(fromCountry)-1)+') '))
            if g.freeMove(fromCountry, toCountry, howMany, player):
                loader.save(g)
                break
else:
    print 'error processing order'
