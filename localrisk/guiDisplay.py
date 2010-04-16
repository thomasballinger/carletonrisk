import Tkinter
import Image
import game
import ImageDraw
import sys, os
import ImageOps
import ImageFilter
class Display:
    def __init__(self,parentObject,mapString=None,mapImage=None,cordinateMap=None):
        if not mapImage:
            print 'need a map image!'
            sys.exit()
        else:
            self.mapImageFilename = mapImage
        self.parent = parentObject
        if not cordinateMap:
            self.cordinateMap = {}
        else:
            self.cordinateMap = cordinateMap
        self.original = Image.open(self.mapImageFilename)
        self.original.load()
        self.colorMap = {}
        self.maskMap = {}
        iconList = [
        '/projects/schiz/ra/tomb/risk/blueCircle.png',
        '/projects/schiz/ra/tomb/risk/redCircle.png',
        '/projects/schiz/ra/tomb/risk/yellowCircle.png',
        '/projects/schiz/ra/tomb/risk/orangeCircle.png',
        '/projects/schiz/ra/tomb/risk/greenCircle.png',
        '/projects/schiz/ra/tomb/risk/pinkCircle.png'
        ]
        for i in range(len(parentObject.getPlayers())):
            player = parentObject.getPlayers()[i]
            colorFile = iconList[i]
            self.colorMap[player]=Image.open(colorFile)
            self.colorMap[player].load()
            #self.maskMap[player] = Image.eval(self.colorMap[player], lambda p: 1)#p: 255 * (int(p != 0)))
            #colorMaskFile = colorFile[0:-4]+'_mask'+colorFile[-4:len(colorFile)]
            #self.maskMap[player]=Image.open(colorFile)
            #self.maskMap[player].load()

    def show(self):
        working = Image.open(self.mapImageFilename)
        spotSize = ()
        for entry in self.cordinateMap:
            player = self.parent.getOwner(entry)
            spot = self.cordinateMap[entry]
            icon = self.colorMap[player]
            size = icon.size
            #mask = self.maskMap[player]
            working.paste(icon,(spot[0],spot[1],spot[0]+size[0],spot[1]+size[1]),icon)
            drawing = ImageDraw.Draw(working)
            numTroops = self.parent.getTroops(entry)
            if len(str(numTroops)) > 1:
                drawing.text((spot[0]+4,spot[1]+4),str(numTroops))
            else:
                drawing.text((spot[0]+8,spot[1]+4),str(numTroops))
        working.show()

if __name__=='__main__':
    class fakeObject:
        states = {'USA':['Alex',142],'England':['Thomas',4]}
        def getTroops(self,country):
            return self.states[country][1]
        def getStates(self):
            return self.states
        def getPlayers(self):
            return ['Thomas', 'Alex']
        def getOwner(self,country):
            return self.states[country][0]
    parentObject = fakeObject()
    d = Display(parentObject, mapImage='/projects/schiz/ra/tomb/risk/intel.png', cordinateMap={"USA":(100,100),"England":(120,30)})
    d.show()
