from loader import *
from game import Game
from google.appengine.api import users
def parseInput(input, game):
    """Returns a game if succesfully modified, False otherwise"""
    user = users.get_current_user()
    if not user:
        raise Exception, "no current user for command"
    if input.find('place')!=-1:
        words = input.split()
        if len(words) == 2:
            result = game.reinforce(words[1], 1, user.email())
        elif len(words) == 3:
            howMany = 1
            country = None
            for word in words:
                try:
                    howMany = int(word)
                except:
                    country = word
            if not howMany or not country:
                return False
            result = game.reinforce(country, howMany, user.email())
        else:
            return False
        if result:
            return result
        else:
            return False
    elif input.find('attack')!=-1:
        words = input.split()
        fromCountry = words[1]
        toCountry = words[2]
        if not game.isCountry(fromCountry):
            return False
        try:
            howMany = int(words[3])
        except:
            howMany = min(3,(game.getTroops(fromCountry))-1)
        result = game.attack(fromCountry, toCountry, howMany, user.email())
        if result:
            return result
        else:
            return False
    elif input.find('move')!=-1:
        words = input.split()
        if len(words) == 3:
            countries = [words[1], words[2]]
            howMany = game.getTroops(countries[0])-1
        elif len(words) == 4:
            countries = []
            for word in words:
                try:
                    howMany = int(word)
                except:
                    countries.append(word)
        else:
            return False
        result = game.fortify(countries[0], countries[1], howMany, user.email())
        if result:
            return result
        else:
            return False
    elif input.find('free move') != -1:
        words = input.split()
        howMany = 'yuck'
        countries = []
        for word in words[2:]:
            try:
                howMany = int(word)
            except:
                countries.append(word)
        if type(howMany) == type(1) and len(countries) > 1:
            result = game.freeMove(countries[0], countries[1], howMany, user.email())
            if result:
                return result
            else:
                return False
    elif input.find('pass') != -1 or input.find('skip') != -1:
        result = game.skip(user.email())
        if result:
            return result
        else:
            return False
    return None
    