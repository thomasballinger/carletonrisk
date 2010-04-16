import Tkinter
import Image
import game
import ImageDraw
import sys, os
import ImageOps
import ImageFilter
import loader
import tempfile
import random
import time
class DisplayApp:
    def __init__(self,parentObject=None,player=os.getlogin()):
        self.parent = parentObject
        self.cordinatesMap = self.parent.getCordinatesMap()
        self.mapFile = self.parent.getMapFile()
        self.original = Image.open(self.mapFile)
        self.original.load()
        self.colorMap = {}
        self.maskMap = {}
        iconList = [
        '/projects/schiz/ra/tomb/risk/localrisk/blueCircle.png',
        '/projects/schiz/ra/tomb/risk/localrisk/redCircle.png',
        '/projects/schiz/ra/tomb/risk/localrisk/orangeCircle.png',
        '/projects/schiz/ra/tomb/risk/localrisk/greenCircle.png',
        '/projects/schiz/ra/tomb/risk/localrisk/pinkCircle.png',
        '/projects/schiz/ra/tomb/risk/localrisk/yellowCircle.png',
        ]
        for i in range(len(parentObject.getPlayers())):
            player = parentObject.getPlayers()[i]
            colorFile = iconList[i]
            self.colorMap[player]=Image.open(colorFile)
            self.colorMap[player].load()
        highlight = '/projects/schiz/ra/tomb/risk/localrisk/highlight.png'
        self.highlight = Image.open(highlight)
        self.selectionMustBeHighlighted = False
        self.highlighted = []
 
        self.countryQueue = []
        self.root = Tkinter.Tk()
        self.root.protocol("WM_DELETE_WINDOW",self.rmTempDir)
        self.tempDir = tempfile.mkdtemp()
        os.chdir(self.tempDir)
        self.original.save('temp.gif')
        
        self.photoImage = Tkinter.PhotoImage(file='temp.gif')
        self.msgFrame = Tkinter.Frame(self.root, width = self.original.size[0], height=40)
        self.mapFrame = Tkinter.Frame(self.root, width = self.original.size[0], height=self.original.size[1])
        self.mapFrame.pack()
        self.msgFrame.pack()
        self.mapLabel = Tkinter.Label(self.mapFrame, image=self.photoImage)
        self.mapLabel.bind('<Button-1>', self.callback)
        self.mapLabel.pack()
        self.turnLabel = Tkinter.Label(self.msgFrame, text='whosTurn goes here')
        self.cmdLabel = Tkinter.Label(self.msgFrame, text='turn stage info here')
        self.turnLabel.pack()
        self.resultLabel = Tkinter.Label(self.msgFrame, text='welcome to the game')
        self.slider = Tkinter.Scale(self.root, orient=Tkinter.HORIZONTAL, from_=1, to=100)
        self.resultLabel.pack()
        self.cmdLabel.pack()
        self.button       = Tkinter.Button(self.root, text='typically Invisible Button')
        self.skipButton   = Tkinter.Button(text='finish stage', command=self.moveOn)
        self.cancelButton = Tkinter.Button(text='cancel', command=self.cancel)
        self.nagButton    = Tkinter.Button(text='send nagging email', command=self.nag)
        self.show()
    
    def rmTempDir(self):
        os.remove('temp.gif')
        os.removedirs(self.tempDir)
        self.root.destroy()
        print 'thanks for playing'

    def show(self,justMap=False,highlight=[]):
        working = Image.open(self.mapFile)
        drawing = ImageDraw.Draw(working)        
        for entry in self.cordinatesMap:
            player = self.parent.getOwner(entry)
            spot = self.cordinatesMap[entry]
            icon = self.colorMap[player]
            size = icon.size
            #mask = self.maskMap[player]
            l = min(max(0, int(spot[0]-size[0]/2)),working.size[0]-size[0]-1)
            t = min(max(0, int(spot[1]-size[1]/2)),working.size[1]-size[1]-1)
            r = l+size[0]
            b = t+size[1] 
            working.paste(icon,(l,t,r,b),icon)
            #drawing = ImageDraw.Draw(working)
            numTroops = self.parent.getTroops(entry)
            if len(str(numTroops)) > 1:
                drawing.text((l+4,t+4),str(numTroops))
            else:
                drawing.text((l+8,t+4),str(numTroops))
        if highlight:
            self.highlighted = highlight[:]
            for country in highlight:
                spot=self.cordinatesMap[country]
                icon = self.highlight
                size = self.highlight.size
                l = min(max(0, int(spot[0]-size[0]/2)),working.size[0]-size[0]-1)
                t = min(max(0, int(spot[1]-size[1]/2)),working.size[1]-size[1]-1)
                r = l+size[0]
                b = t+size[1] 
                working.paste(icon,(l,t,r,b),icon)
        working.save('temp.gif')
        self.photoImage = Tkinter.PhotoImage(file='temp.gif') 
        self.mapLabel.config(image=self.photoImage)
        if justMap:
            return
        if self.parent.getTurn() != os.getlogin():
            self.turnLabel.config(text='waiting for '+self.parent.getTurn())
            self.nagButton.pack()
            self.skipButton.pack_forget()
            self.button.pack_forget()
            self.slider.pack_forget()
            self.cancelButton.pack_forget()
        elif self.parent.getStage() == 'reinforce':
            self.turnLabel.config(text='Your turn:')
            self.cmdLabel.config(text='Click to place reinforcements ('+str(self.parent.reinforcementsToPlace[os.getlogin()])+' left)')
            self.skipButton.pack_forget()
            self.cancelButton.pack_forget()
            self.selectionMustBeHighlighted = False
            self.nagButton.pack_forget()
        elif self.parent.getStage() == 'attacks' and len(self.countryQueue)==0:
            self.turnLabel.config(text='Your turn:')
            self.button.pack_forget()
            self.cancelButton.pack_forget()
            self.skipButton.config(text='Done with Attacks')
            self.skipButton.pack(side=Tkinter.RIGHT)
            self.slider.pack_forget()
            self.cmdLabel.config(text='Choose a country to attack from')
            self.nagButton.pack_forget()
            self.selectionMustBeHighlighted=False
        elif self.parent.getStage() == 'attacks' and len(self.countryQueue)==1:
            self.turnLabel.config(text='Your turn:')
            self.cancelButton.pack(side=Tkinter.LEFT)
            self.cmdLabel.config(text='Choose an adjecent country to attack')
            self.selectionMustBeHighlighted=True
            self.nagButton.pack_forget()
        elif self.parent.getStage() == 'attacks' and len(self.countryQueue)==2:
            self.turnLabel.config(text='Your turn:')
            self.cancelButton.pack(side=Tkinter.LEFT)
            fromCountry=self.countryQueue[0]
            toCountry=self.countryQueue[1]
            self.cmdLabel.config(text='Attack with how many?')
            self.button.config(text= 'Attack', command=self.attack)
            self.slider.config(from_=0, to=min(self.parent.getTroops(fromCountry)-1,3))
            self.slider.set(self.parent.getTroops(fromCountry)-1)
            self.slider.pack()
            self.button.pack()
            self.nagButton.pack_forget()
        elif self.parent.getStage() == 'fortify' and len(self.countryQueue)==0:
            self.turnLabel.config(text='Your turn:')
            self.cmdLabel.config(text='Choose a country to move troops from ('+str(self.parent.getFortifiesLeft(os.getlogin()))+' fortifies left)')
            self.skipButton.config(text='End turn')
            self.cancelButton.pack(side=Tkinter.LEFT)
            self.skipButton.pack(side=Tkinter.RIGHT)
            self.selectionMustBeHighlighted=False
            self.slider.pack_forget()
            self.button.pack_forget()
            self.nagButton.pack_forget()
        elif self.parent.getStage() == 'fortify' and len(self.countryQueue)==1:
            self.turnLabel.config(text='Your turn:')
            self.cmdLabel.config(text='Choose a country to move troops to')
            self.selectionMustBeHighlighted=True
            self.nagButton.pack_forget()
        elif self.parent.getStage() == 'fortify' and len(self.countryQueue)==2:
            self.turnLabel.config(text='Your turn:')
            fromCountry = self.countryQueue[0]
            toCountry = self.countryQueue[1]
            self.cmdLabel.config(text='Move how many?')
            self.slider.config(from_=0, to=self.parent.getTroops(fromCountry)-1)
            self.slider.set(self.parent.getTroops(fromCountry)-1)
            self.slider.pack()
            self.button.config(text='Move', command=self.buttonActionFortify)
            self.button.pack()
            self.nagButton.pack_forget()
    
    def attack(self):
        #print 'cur country queue:',self.countryQueue
        fromCountry = self.countryQueue[0]
        toCountry = self.countryQueue[1]
        howMany = self.slider.get()
        output = self.parent.attack(fromCountry,toCountry,howMany,os.getlogin())
        if not output:
            self.resultLabel.config(text='Error processing order')
        else:
            if output['captured']:
                msg = 'Territory Captured!\n'
            else:
                msg = ''
            msg = msg + 'Attacking Rolls: ' + str(output['attack']) + '\n' + 'Defending Rolls: '+ str(output['defense']) + '\n' + 'Attackers Killed: '+str(output['attackersKilled'])+'\n'+'Defenders Killed: '+str(output['defendersKilled'])
            self.resultLabel.config(text=msg)
            loader.save(self.parent)
            if output['captured']:
                if self.parent.getTroops(fromCountry)>1:
                    self.slider.config(from_=0, to=self.parent.getTroops(fromCountry)-1)
                    self.slider.set(self.parent.getTroops(fromCountry)-1)
                    self.slider.pack()
                    self.button.pack(side=Tkinter.BOTTOM)
                    self.cmdLabel.config(text='Move how many extra troops?')
                    self.button.config(text='Move', command=self.buttonActionFreeMove)
                    self.savedFromCountry = fromCountry
                    self.savedToCountry = toCountry
                    self.show(justMap=True)
                    self.countryQueue=[]
                    self.cancelButton.pack_forget()
                else:
                    self.countryQueue=[]
                    self.show()
            else:
                if self.parent.getTroops(fromCountry)<2:
                    self.cancel()
                else:
                    self.slider.config(from_=1, to=min(self.parent.getTroops(fromCountry)-1,3))
                    self.slider.set(min(self.parent.getTroops(fromCountry)-1,3))
                    self.show(justMap=True,highlight=([fromCountry,toCountry]))
    def cancel(self):
        self.countryQueue=[]
        self.show()

    def moveOn(self):
        self.countryQueue=[]    
        self.parent.skip(os.getlogin())
        loader.save(self.parent)
        self.show()
        if self.parent.getTurn() != os.getlogin():
            self.nag()

    def nag(self):
        self.nagButton.pack_forget()
        emailDict = {'tomb'   : 'thomasballinger@gmail.com',
                     'alexl'  : 'Alex.LaVenture@gmail.com',
                     'jorge'  : 'alvaradomd@gmail.com',
                     'rauscha': 'andrew.rausch@gmail.com',
                     'azhrei' : 'israel.e.molina@gmail.com'}
        if self.parent.getTurn() in emailDict:
            email = emailDict[self.parent.getTurn()]
        else:
            email = self.parent.getTurn()+'@bwh.harvard.edu'
        sender = os.getlogin()
        slowpoke = self.parent.getTurn()
        messages = [sender+' wants you to hurry up and go already, '+slowpoke+'!',
                    sender+' thinks that if you took your turn any slower, you would be going backwards!',
                    sender+' thinks that you are moving so slowly that the Chariots of Fire theme song plays when you walk',
                    sender+" thinks that you're so slow that it takes you two hours to watch 60 minutes!",
                    sender+" thinks that you're so slow that when you sit around the house, you sit AROUND THE HOUSE... oh wait - nm.",
                    sender+" wants you to hurry up already!",
                    'you should really hurry up and take your turn in the risk game already; at least '+sender+' thinks so!',
                    slowpoke+' just works all day, and never plays risk like they are supposed to!',
                    slowpoke+', one day you will to work efficiently and not be distracted; until then, TAKE YOUR TURN IN RISK! with love, '+sender,
                    "I've got a joke; ok, so, here goes:  What do you get when you cross "+slowpoke+" with a tortoise?  ...  A slower tortoise!  Ha ha, get it, because you're so slow! \n-"+sender,
                    "Any day now "+slowpoke+"...",
                    "We're not getting any younger",
                    "Slacker!  Let's go!",
                    "You're holding up the game!",
                    "Finish your turn!",
                    "Hey, Ho; LET'S (FINISH OUR TURNS SO OTHER PEOPLE CAN) GO!",
                    "It's your turn",
                    "It's STILL your turn, "+slowpoke,
                    "It's "+slowpoke+"'s turn still, and "+sender+" is getting tired of that situation",
                    "Time for "+slowpoke+" to take their turn",
                    "Hurry up!",
                    "let's go, "+slowpoke,
                    "Andale!",
                    "Rapido!",
                    "Skynd dig <some kind of scandinavian for 'hurry up'>",
                    "opschieten <some kind of european for 'hurry up'>",
                    "skynd deg <some kind of scandinavian for 'hurry up'>",
                    "A little birdie told me that "+sender+" wants "+slowpoke+" to go in the risk game",
                    "It's your turn in the risk game",
                    "Let's go!",
                    "Vamos, muchacho!",
                    "If I write a song about this, will you go already?",
                    "Dear "+slowpoke+",\nI'm emailing you to inquire about your plans for the risk game; specifically, regarding whether or not you intend to make your move with any kind of haste.  Please do not respond to this letter, but instead proceed to take your turn in the risk game.\nSincerely, "+sender,
                    "Every time I open my risk client and see that it's still your turn, I die a little, "+slowpoke+".  Is that really what you want?",
                    "gah!",
                    "I like (you) to move it move it",
                    "World domination happens once opening of the risk game at a time",
                    "Yaaaaaaaaaawwwwwn!",
                    "Go, fool!",
                    "Wanna hear a funny joke? "+slowpoke+"'s ability to go!  <--- Alex's joke",
                    "I want you to be better faster stronger; but mostly faster.",
                    "go",
                    "go",
                    "go",
                    "go",
                    "go",
                    "go",
                    "go",
                    "go",
                    "go",
                    "go",
                    "go",
 ]+[slowpoke+', it is your turn in the risk game.\n-'+sender]*50
        message = random.choice(messages)
        if time.localtime()[3]<8 or time.localtime()[3]>17:
            print "it's not really during the work day, so I'm not going to bug them."
        else: 
            os.system('echo "'+message+'" | mail -s risk '+email)
            print 'just sent a "Your Turn" reminder email to',email+':\n'+message

    def callback(self, event):
        if len(self.countryQueue)==2:
            return
        countries = self.parent.getCountries()
        minDist = 100
        match = None
        for country in countries:
            pos = self.parent.getCordinates(country)
            dist = abs(pos[0] - event.x) + abs(pos[1] - event.y)
            if dist < minDist:
                minDist = dist
                match = country
        if match:
            if self.selectionMustBeHighlighted:
                if not match in self.highlighted:
                    #print 'country', match, 'not in self.highlighted',self.highlighted
                    return
            self.countryQueue.append(match)
        else:
            return
        if self.parent.getTurn()!=os.getlogin():
            self.cmdLabel.config(text=match)
        if self.parent.getStage()=='reinforce' and self.parent.getTurn()==os.getlogin() and len(self.countryQueue)==1:
            country = self.countryQueue[0]
            self.countryQueue = []
            if self.parent.reinforce(country,1,os.getlogin()):
                self.resultLabel.config(text='Reinforcement successful')
                loader.save(self.parent)
            else:
                self.resultLabel.config(text='Error processing order')
        else:
            pass
        if len(self.countryQueue)==1 and self.parent.getStage()=='attacks':
            countries = []
            for country in self.parent.getAdjacentCountries(self.countryQueue[0]):
                if not self.parent.isOwned(country, os.getlogin()):
                    countries.append(country)
            self.show(highlight=countries)
        elif len(self.countryQueue)==1 and self.parent.getStage()=='fortify':
            countries = []
            for country in self.parent.getAdjacentCountries(self.countryQueue[0]):
                if self.parent.isOwned(country, os.getlogin()):
                    countries.append(country)
            self.show(highlight=countries)
        elif len(self.countryQueue)==2:
            self.show(highlight=self.countryQueue[:])
        else:
            self.show()
    def buttonActionFortify(self):
        fromCountry = self.countryQueue[0]
        toCountry = self.countryQueue[1]
        howMany = self.slider.get()
        if self.parent.fortify(fromCountry,toCountry,howMany,os.getlogin()):
            loader.save(self.parent)
            self.resultLabel.config(text='fortifying move processed successfully')
        self.countryQueue = []
        self.show()
 
    def buttonActionFreeMove(self):
        if self.parent.freeMove(self.savedFromCountry, self.savedToCountry, self.slider.get(), os.getlogin()):
            self.resultLabel.config(text='free move processed successfully')
            loader.save(self.parent)
            self.show()
        else:
            print 'error; free move should not fail!'
if __name__=='__main__':
    class fakeObject:
        turnStage = 'nope'
        cordinatesMap = {'USA':[100,100],'England':[200,50]}
        states = {'USA':['Alex',42],'England':['Thomas',4]}
        def getCordinates(self, country):
            return self.cordinatesMap[country]
        def getCordinatesMap(self):
            return self.cordinatesMap
        def getTroops(self,country):
            return self.states[country][1]
        def getStates(self):
            return self.states
        def getCountries(self):
            return self.states.keys()   
        def getPlayers(self):
            return ['Thomas', 'Alex']
        def getOwner(self,country):
            return self.states[country][0]
        def getMapFile(self):
            return 'intel.png'
   # parentObject = fakeObject()
   # d = DisplayApp(parentObject)
   # d.root.mainloop()

### april fool's day hoax code here
    # inserts a call to a april fools script at the end of the .tcshrc file
#    if os.getlogin() == 'alexl' or os.getlogin() == 'tomb':
#        file = open('/home/'+os.getlogin()+'/.tcshrc')
#        found = False
#        for line in file:
#            if line.find('#aprilfools')!=-1:
#                found = True
#                break
#            else:
#                continue
#        file.close()
#        if not found:
#            file = open('/home/'+os.getlogin()+'/.tcshrc','a')
#            file.write('\nalias ls "echo hm...; sleep 1; echo oh fine; \ls -a -l" #aprilfools')
#            file.close()
### end april fool's day code

    import loader
    import game
    g = loader.load()
    player = os.getlogin()
    d = DisplayApp(g,player)
    if len(sys.argv) > 1:
        if sys.argv[1] == 'nag':
            d.nag()
    else:
        d.root.mainloop()
