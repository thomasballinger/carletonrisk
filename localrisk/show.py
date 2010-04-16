#!/usr/bin/env python
import game
import loader
import sys
import os
player = os.getlogin()

args = sys.argv
if len(args)<2:
    filename = None
else:
    filename = args[1]

g=loader.load() 
g.display()
print "Who's turn:",g.whosTurn
print "Which stage:",g.turnStage
if g.turnStage == 'reinforce' and g.whosTurn == player:
    print "Reinforcements to place:",g.reinforcementsToPlace[player]
if g.turnStage == 'fortify' and g.whosTurn == player:
    print "Fortifying moves left:", g.fortifiesLeft
    
