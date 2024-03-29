import game
import loader
import sys
from random import shuffle
args = sys.argv
if len(args) == 1:
    args = ['scriptname', 'worldmap.txt', 'tomb', 'alexl']
if len(args)==1:
    loader.save(game.startingPos())
if len(args)>3:
    players = []
    for arg in args[2:len(args)+1]:
        players.append(arg)

    file = open(args[1])
    lines = file.readlines()
    giantString = "".join(lines)

    bonusesList = []
    nodeNetwork = {}
    mapLines = []
    mapString = ''
    mapFile = ''
    cordinatesMap = {}
    settingsMap = {}
    
    mode = 'comment'
    for line in lines:
        print 'was interpreted in mode',mode
        print line
        if line.find('<end')!=-1:
            mode = 'comment'
            continue
        if line.find('<start-map>')!=-1:
            mode = 'map'
            continue
        if line.find('<start-nodeNetwork>')!=-1:
            mode = 'network'
            continue
        if line.find('<start-bonuses>')!=-1:
            mode = 'bonus'
            continue
        if line.find('<start-cordinates>')!=-1:
            mode = 'cordinates'
            continue
        if line.find('<start-mapFile>')!=-1:
            mode = 'mapFile'
            continue
        if line.find('<start-settings>')!=-1:
            mode = 'settings'
            continue
        if mode == 'settings':
            inputs = line.split()
            settingsMap[inputs[0]]=inputs[1]
            continue
        if mode == 'comment':
            continue
        if mode == 'cordinates':
            inputs = line.split()
            cordinatesMap[inputs[0]]=(int(inputs[1]),int(inputs[2]))
            continue
        if mode == 'mapFile':
            mapFile = line.split()[0]
            nodeNetwork[countries[0]]=countries[1:len(countries)]
            continue
        if mode == 'network':
            countries = line.split()
            nodeNetwork[countries[0]]=countries[1:len(countries)]
            continue
        if mode == 'bonus':
            bonusesList.append(line.split())
            continue
        if mode == 'map':
            mapLines.append(line)
            continue
        else:
            print 'logic error'
            sys.exit

    mapString = "".join(mapLines)
    shuffle(players)
    countries = list(nodeNetwork)
    shuffle(countries)
    
#    print 'starting new map with these characteristics:'
#    print 'nodeNetwork',nodeNetwork
#    print 'bonuses',bonusesList       
#    print 'players',players
#    print 'map'
    print mapString 

    for bonus in bonusesList:
        for country in bonus[0:-1]:
            if country not in countries:
                print "SPELL YOUR COUNTRIES CORRECTLY!!!"
                print "(bonuses reference one I can't find:",country,')'
                sys.exit()

    g = game.Game(nodeNetwork, players, bonusesList, mapString, cordinatesMap, mapFile, settingsMap)
    print 'finished making game!'
    rules = g.rules
    i = 0
    for country in countries:
        rules.assignCountry(country,players[i%len(players)])
        if 'initialTroopsInCountries' in settingsMap:
            toAdd = int(settingsMap['initialTroopsInCountries'])-1
            if toAdd > 0:
                rules.addUnits(country,toAdd)
        i+=1
    g.giveReinforcements()
    print 'turn order:',players
    loader.save(g)
