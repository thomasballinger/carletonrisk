from game import Game
from random import shuffle
import pickle
from google.appengine.ext import db

class LongString(db.Model):
    name = db.StringProperty()
    content = db.TextProperty()
    date    = db.DateTimeProperty(auto_now_add=True)

class Loader():
    def __init__(self, name = None):
        if not name:
            raise Exception, "loaders should be initialized with names"
        self.name = name
        
    def load(self):
        """Returns the game object"""
        if self.name:
            response = db.GqlQuery("SELECT * FROM LongString WHERE name = :1", self.name)
        else:
            response = db.GqlQuery("SELECT * FROM LongString ORDER BY date DESC LIMIT 1") 
        if not response:
            return False
#        print response
        #if type(response[0]) != type()
        #    raise Exception, "QqlQuery returned more than one match for game name"
        self.longString = response[0]
#        print self.longString
#        print self.longString.content[0:100]
        game = pickle.loads(str(self.longString.content))
        return game
        
    def save(self, game):
        if not self.longString:
            raise Exception, "Game can't be saved, not loaded in loader!"
        string = pickle.dumps(game)
        self.longString.content=db.Text(unicode(string))
        self.longString.put()
        return True

    def new(self, mapFile, playerList):

        import os
#        raise Exception, str(os.listdir('.'))
#        file = open(mapFile)
        file = open("maps/map4.txt")
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
#            print 'was interpreted in mode',mode
#            print line
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
                raise Exception, 'I do not know what to do with this line of text: '+line
                
        mapString = "".join(mapLines)
        shuffle(playerList)
        countries = list(nodeNetwork)
        shuffle(countries)
        
        for bonus in bonusesList:
            for country in bonus[0:-1]:
                if country not in countries:
                    raise Exception, "SPELL YOUR COUNTRIES CORRECTLY! (bonuses reference one I can't find:"+country+')'
        g = Game(nodeNetwork, playerList, bonusesList, mapString, cordinatesMap, mapFile, settingsMap)
        rules = g.rules
        i = 0
        for country in countries:
            rules.assignCountry(country,playerList[i%len(playerList)])
            if 'initialTroopsInCountries' in settingsMap:
                toAdd = int(settingsMap['initialTroopsInCountries'])-1
                if toAdd > 0:
                    rules.addUnits(country,toAdd)
            i+=1
        g._giveReinforcements()
        
        self.longString = LongString()
        string = pickle.dumps(g)
        self.longString.content = db.Text(string)
        self.longString.name = self.name
        self.longString.put()
