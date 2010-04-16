from rules import Rules
from textDisplay import Display
# turn stages go:

class Game:
    """Represents the current state of a risk game

    Includes full specification of the map, rules, players and current game state.  Includes the NAME ONLY of the graphical map file, along with cordinates of territories on this map."""
    def __init__(self,nodeNetwork=None, players={}, bonuses=[], mapString=None, cordinates=None, mapFile=None, settingsMap={}):
        self.mapFile = mapFile
        self.cordinates = cordinates
        self.rules = Rules(map=nodeNetwork,players=players)
        self.whosTurn = self.rules.players[0]
        self.turnStage = 'reinforce'
        self.reinforcementsToPlace = {}
        self.lastAttack = None
        self.fortifies = 1
        if 'fortifies' in settingsMap:
            self.fortifies = int(settingsMap['fortifies'])        
        self.fortifiesLeft = self.fortifies
        self.bonuses=bonuses
        for player in self.rules.players:
            self.reinforcementsToPlace[player]=0
        self.reinforced = False
        if not mapString and not (cordinates and mapFile):
            print "this game has no pretty visualization available"
        self.mapString = mapString
        self.settingsMap = settingsMap
        self.fog = False
        if 'fog' in self.settingsMap:
            self.fog = self.settingsMap['fog']
        self.selectionList=[]
 
    def _giveReinforcements(self):
        if self.reinforced == True:
            return False
        else:
            self.reinforced = True
            self.reinforcementsToPlace[self.whosTurn]=self.getDeservedReinforcements(self.whosTurn)

    def getFortifiesLeft(self,player):
        """Returns 0 if not the current players turn, otherwise the number of fortifying moves left in the turn"""
        if self.whosTurn != player:
            return 0
        else:
            return self.fortifiesLeft

    def getLastAttack(self,player):
        if self.whosTurn != player:
            return False
        else:
            return self.lastAttack

    def getWhosTurn(self):
        """Returns player string of whos turn it is"""
        return self.whosTurn

    def getReinforcements(self,player):
        """Returns how many reinforcements the player has yet to place"""
        return self.reinforcementsToPlace[player]

    def updateTurn(self):
        if len(self.getPlayersAlive()) == 1:
            self.turnStage = 'reinforce'
            self.reinforcementsToPlace[self.whosTurn] = 1
        elif self.turnStage == 'reinforce':
            if self.whosTurn not in self.getPlayersAlive():
                self.reinforcementsToPlace[self.whosTurn] = 0
                self.updateTurn()
            elif self.reinforcementsToPlace[self.whosTurn]==0:
                self.turnStage = 'attacks'
        elif (self.turnStage == 'fortify' and self.fortifiesLeft == 0) or self.whosTurn not in self.getPlayersAlive():
            players = self.getPlayers()
            for i in range(len(players)):
                if self.whosTurn == players[i]:
                    self.whosTurn = players[(i+1)%len(players)]
                    self.reinforcementsToPlace[self.whosTurn] = self.getDeservedReinforcements(self.whosTurn)
                    self.fortifiesLeft = self.fortifies
                    self.turnStage = 'reinforce'
                    break

    def getDeservedReinforcements(self,player):
        count = 0
        countriesPerTroop = 3
        if 'countriesPerTroop' in self.settingsMap:
            countriesPerTroop = int(self.settingsMap['countriesPerTroop']) 
        countries = self.getCountries()
        for country in countries:
            if self.isOwned(country, player):
                count +=1
        for bonus in self.bonuses:
            deserveBonus = True
            for country in bonus[0:-1]:
                if not self.isOwned(country,player):
                    deserveBonus = False
            if deserveBonus:
                count+=(countriesPerTroop*int(bonus[-1]))
        return max(int(count/countriesPerTroop),3)


    def reinforce(self,country,howMany,player):
        pass
        # check for correct turn, right time, have reinforcements, etc.
        if type(player) != type('string'):
            return False
        if self.whosTurn != player:
            return False
        if self.turnStage != 'reinforce':
            return False
        if self.reinforcementsToPlace[player]<=0:
            return False
        if type(country) != type('string'):
            return False
        if country not in self.getCountries():
            return False
        if not self.isOwned(country, player):
            return False
        if type(howMany) != type(1):
            return False
        if howMany>self.reinforcementsToPlace[player]:
            return False
        if howMany < 0:
            return False
        if self.rules.addUnits(country, howMany):
            self.reinforcementsToPlace[player]=self.reinforcementsToPlace[player]-howMany
            self.updateTurn()
            return True
        else:
            return False
    
    def attack(self,fromCountry,toCountry,howMany,player):
        if self.whosTurn != player:
            return False
        if self.turnStage != 'attacks':
            return False
        if type(fromCountry)!=type('string'):
            print 'fromCountry',fromCountry
            return False
        if type(toCountry)!=type('string'):
            return False
        if type(player)!=type('string'):
            return False
        if type(howMany)!=type(1):
            return False
        if not fromCountry in self.getCountries():
            return False
        if not toCountry in self.getCountries():
            return False
        if not player in self.getPlayers():
            return False
        if not self.isTouching(fromCountry, toCountry):
            return False
        if not self.isOwned(fromCountry, player):
            return False
        if self.isOwned(toCountry, player):
            return False
        if self.getTroops(fromCountry) < howMany+1:
            return False
        if howMany < 1:
            return False
        output = self.rules.attack(fromCountry,toCountry,howMany)
        if not output:
            return False
        else:
            self.lastAttack = output
            # FINISH PROCESSING ATTACK!  ? is there anythin left to do?
            self.updateTurn()
            return output

    def freeMove(self,fromCountry,toCountry,howMany,player):
        if type(player)!=type('string'):
            return False
        if self.whosTurn != player:
            return False
        if self.turnStage != 'attacks':
            return False
        if type(fromCountry)!=type('string'):
            return False
        if type(toCountry)!=type('string'):
            return False
        if type(howMany)!=type(1):
            return False
        if not self.lastAttack['captured']:
            return False
        if fromCountry != self.lastAttack['from']:
            return False
        if toCountry != self.lastAttack['to']:
            return False
        if not player in self.getPlayers():
            return False
        if not self.isTouching(fromCountry, toCountry):
            return False
        if not self.isOwned(fromCountry, player):
            return False
        if not self.isOwned(toCountry, player):
            return False
        if self.getTroops(fromCountry) < howMany+1:
            return False
        if self.rules.moveUnits(fromCountry, toCountry, howMany):
            self.updateTurn()
            return True
        else:
            return False

    def fortify(self,fromCountry,toCountry,howMany,player):
        if type(player)!=type('string'):
            return False
        if self.whosTurn != player:
            return False
        if self.turnStage != 'fortify' and self.turnStage != 'attack':
            return False
        if self.fortifiesLeft <1:
            return False
        if type(fromCountry)!=type('string'):
            return False
        if type(toCountry)!=type('string'):
            return False
        if type(howMany)!=type(1):
            return False
        if not self.isTouching(fromCountry, toCountry):
            return False
        if not self.isOwned(fromCountry, player):
            return False
        if not self.isOwned(toCountry, player):
            return False
        if self.getTroops(fromCountry) < howMany+1:
            return False
        if self.rules.moveUnits(fromCountry, toCountry, howMany):
            self.turnStage = 'fortify'
            self.fortifiesLeft -=1
            self.updateTurn()
            return True
        else:
            return False

    def skip(self, player):
        if self.whosTurn != player:
            return False
        else:
            if self.turnStage == 'reinforce':
                if self.reinforcementsToPlace[self.whosTurn] <= 0:
                    self.updateTurn()
                else:
                    return False
            elif self.turnStage == 'attacks':
                self.turnStage = 'fortify'
                self.updateTurn()
                return True
            elif self.turnStage == 'fortify':
                self.fortifiesLeft = 0
                self.updateTurn()
                return True
            else:
                return False

    def getCordinates(self, country):
        return self.cordinates[country]

    def getAdjacentAttacks(self, country):
        possibleAttacks = []
        player = self.getOwner(country)
        for adjCountry in self.getAdjacentCountries(country):
            if self.getOwner(adjCountry) != player:
                possibleAttacks.append(adjCountry)
        return possibleAttacks
   
    def getFortifies(self):
        return self.fortifies
    
    def isCountry(self,country):
        return country in self.getCountries()
         
    def getCountries(self):
        return self.rules.board.getCountries()

    def getOwner(self, country):
        return self.rules.getOwner(country)

    def getTroops(self, country):
        return self.rules.getTroops(country)
    
    def getPlayers(self):
        return self.rules.players

    def getPlayersAlive(self):
        return self.rules.getPlayersAlive()

    def getAdjacentCountries(self,country):
        return self.rules.getAdjacentCountries(country)

    def isTouching(self, country1, country2):
        return self.rules.isTouching(country1, country2)

    def isOwned(self, country, player):
        return self.rules.isOwned(country, player)

    def allOwned(countryList, player):
        return self.rules.isOwned(country, player)

    def getStates(self):
        return self.rules.board.getCountryStates()

    def getTurn(self):
        return self.whosTurn
    
    def setSelection(self, list):
        self.selectionList = list

    def getSelection(self, list):
        return self.selectionList

    def getResult(self):
        return False

    def getStage(self):
        return self.turnStage

    def getMapString(self):
        return self.mapString

    def getCordinatesMap(self):
        return self.cordinates

    def getMapFile(self):
        return self.mapFile

    def display(self):
        print 'use the command "risk" instead, even if you just want to look'
        print 'at the map and keep using the command line interface'

# debugging tools
mymap = {'USA':['Canada','Mexico'],'Canada':['USA','Greenland'],'Mexico':['USA','Cuba','England'],'Cuba':['Mexico'],'Greenland':['Canada','Iceland'],'Iceland':['England','Greenland'],'England':['Mexico','Iceland'],'Alaska':['Canada']}

if __name__=='__main__':
    
    game = Game(nodeNetwork=mymap, players=['tom', 'alex'],mapString="".join((open('worldmap.txt').readlines()[32:51])))
    game.display()
    
    rules = game.rules
    print 'assign usa to tom',rules.assignCountry('USA','tom')
    print 'assign canada to tom',rules.assignCountry('Canada','tom')
    print 'assign mexico to alex',rules.assignCountry('Mexico','alex')
    print 'assign cuba to alex',rules.assignCountry('Cuba','alex')
    game.display()
    print 'add units to usa',rules.addUnits('USA',3)
    print 'add unites to canada',rules.addUnits('Canada',4)
    print 'move unite from canada to usa',rules.moveUnits('Canada','USA',1)
    game.display()
    print game.whosTurn
    print game.turnStage
    game.reinforcementsToPlace['tom']=3
    print 'reinforce usa with 3 for tom:',
    print game.reinforce('USA',3,'tom')
    game.display()
    print 'attack mexico with 2 for tom:',
    print game.attack('USA','Mexico',2,'tom')    
    game.display()
    print 'freemove from usa to mexico with 1 for tom:',
    print game.freeMove('USA','Mexico',1,'tom')
    game.display()
    print 'skip:',
    print game.skip('tom')
    print 'fortify usa from canada with 1:',
    print game.fortify('Canada','USA',1,'tom')
    game.display()
    print 'reinforce cuba once',game.reinforce('Cuba',1,'alex')
    print 'reinforce cuba twice',game.reinforce('Cuba',2,'alex')
    game.display()

    print 'whosTurn',game.whosTurn
    print 'turnStage',game.turnStage
    print 'toReinforce',game.reinforcementsToPlace
    

    print game.getStates()

