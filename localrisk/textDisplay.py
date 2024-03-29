# plan: second country name string is replaces with as much space
#  (and at least 6 chars) showing name in three letters and num
#
#  USA    ->  USA
#  USA*** ->  tom 17
#

class Display:
    def __init__(self,parentObject,mapString=None,mapImage=None):
        if not mapString:
            self.origString = "".join(open('worldmap.txt').readlines())
        else:
            self.origString = mapString
        self.parent = parentObject
    
    def show(self):        
        newString = self.origString
        countryStates = self.parent.getStates()
        countries = countryStates.keys()
        for country in countries:
            firstFind = newString.find(country)
            if firstFind == -1:
                print country,'not found in map'
                return False
            dataFind = newString.find(country,firstFind+6)
            if dataFind == -1:
                print country,'not found in map second time'
                return False
            if countryStates[country][0]:
                state = countryStates[country]
            else:
                state = ['N/A',0]
                
            newString = newString[0:dataFind]+state[0][0:3]+' '*(3-len(str(state[1])))+str(state[1])+' '*(len(country)-6)+newString[dataFind+max(len(country),6):len(newString)]
        print '\n\n\n\n\n'
        print newString

class FakeParent:
    def getStates(self):
        return {'USA':['Thomas',42],'England':['Thomas',42]}

if __name__ == '__main__':
    fakeparent = FakeParent()
    x=Display(fakeparent)
    print x.origString
    x.show()
