import game
import pickle
gameFilename = '/projects/schiz/ra/tomb/game.game'
def load(filename = gameFilename):
    file = open(filename)
    unpickler = pickle.Unpickler(file)
    return unpickler.load()
def save(game, filename = gameFilename):
    file = open(filename,'w')
    pickler = pickle.Pickler(file)
    pickler.dump(game)
    file.close()
