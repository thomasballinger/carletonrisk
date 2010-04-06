from google.appengine.ext import db
import cgi

class Node(db.Model):
    name        = db.StringProperty()
    game        = db.StringProperty()
    links       = db.StringListProperty()
    number      = db.IntegerProperty()

class GameState(db.Model):
    # Represents a game
    name            = db.StringProperty()
    turnStage       = db.StringProperty()
    whosTurn        = db.StringProperty()
    bonuses         = db.ListProperty()

def getAllCountries():
    return db.GqlQuery("SELECT * FROM Node")

def getCountry(name):
    return db.GqlQuery("SELECT * FROM Node")

def setCountry()
