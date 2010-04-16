import os, sys
import cgi
from parse import parseInput
from loader import *
from game import Game
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class PlayRisk(webapp.RequestHandler):
    def get(self, name):
        user = users.get_current_user()
        email = user.email()
        loader = Loader(name)
        try:
            game = loader.load()
        except:
            raise Exception, 'Could not find game: '+name
        self.response.out.write("<html>")
        self.response.out.write('''
            <style type="text/css">
                a.test { font-weight: bold; }
            </style>
        ''')
        self.response.out.write('''
            <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.3/jquery.min.js"></script>
        ''')
        self.response.out.write('''
            <script type="text/javascript">
            $(document).ready(function(){
                $("a").click(function(event){
                    $(this).addClass("test");
                    $(this).hide("slow");
                });
            });
            </script>
        ''')
        self.response.out.write('<body> \n')

        # Instructions, information about the game
        self.response.out.write('\n '+name+'<br>')
        self.response.out.write('\n <a href="http://code.google.com/p/carletonrisk/issues/entry">Report Bug or Request Feature <br></a>')
        if game.whosTurn == email:
            self.response.out.write('Your turn<br>')
            if game.turnStage == 'reinforce':
                self.response.out.write('Place reinforcements: '+str(game.reinforcementsToPlace[email])+' left to place<br>')
            elif game.turnStage == 'attacks':
                self.response.out.write('Attack adjacent territories<br>')
            elif game.turnStage == 'fortify':
                self.response.out.write('Move troops: '+str(game.fortifiesLeft)+' fortifying moves left<br>')
        elif not email in game.getPlayers():
            self.response.out.write('You are not a participant of this game.<br>')
        elif not email in game.getPlayersAlive():
            self.response.out.write('You have been elimintated from this game.<br>')
        else:
            self.response.out.write('Waiting for '+game.whosTurn+'<br>')

        # Links for actions        
        if game.getWhosTurn() != email:
            pass
        elif game.getStage() == 'attacks' and len(game.getSelection()) == 2:
            fromCountry = game.getSelection()[0]
            toCountry = game.getSelection()[1]
            if game.lastAttack and game.lastAttack['captured'] and not game.justMadeFreeMove:
                if game.getTroops(fromCountry)>1:
                    self.response.out.write('\nMove how many additional troops?')
                    for i in range(0,game.getTroops(fromCountry),1):
                        self.response.out.write('\n <a href="/games/'+name+'/freemove/'+fromCountry+'/'+toCountry+'/'+str(i)+'">'+str(i)+'</a>')
                    self.response.out.write('<br>')
            else:
                if game.getTroops(fromCountry)>=2:
                    self.response.out.write('\n <a href="/games/'+name+'/attack/'+fromCountry+'/'+toCountry+'/1">Attack with 1<br></a>')
                if game.getTroops(fromCountry)>=3:
                    self.response.out.write('\n <a href="/games/'+name+'/attack/'+fromCountry+'/'+toCountry+'/2">Attack with 2<br></a>')
                if game.getTroops(fromCountry)>=4:
                    self.response.out.write('\n <a href="/games/'+name+'/attack/'+fromCountry+'/'+toCountry+'/3">Attack with 3<br></a>')
                self.response.out.write('\n <a href="/games/'+name+'/select">cancel<br></a>')
            self.response.out.write('\n <a href="/games/'+name+'/skip">done attacking<br></a>')
        
        elif game.getStage() == 'attacks' and len(game.getSelection()) == 1:
            self.response.out.write('\n <a href="/games/'+name+'/select">cancel<br></a>')
            self.response.out.write('\n <a href="/games/'+name+'/skip">done attacking<br></a>')
   
        elif game.getStage() == 'attacks' and len(game.getSelection()) == 0:
            self.response.out.write('\n <a href="/games/'+name+'/skip">done attacking<br></a>')
 
        elif game.getStage() == 'reinforce':
            self.response.out.write('\n Click a country to place a troop there')

        elif game.getStage() == 'fortify' and len(game.getSelection()) == 0:
            self.response.out.write('\n <a href="/games/'+name+'/skip">done fortifying<br></a>')

        elif game.getStage() == 'fortify' and len(game.getSelection()) == 1:
            self.response.out.write('\n <a href="/games/'+name+'/select">cancel<br></a>')

        elif game.getStage() == 'fortify' and len(game.getSelection()) == 2:
            fromCountry = game.getSelection()[0]
            toCountry = game.getSelection()[1]
            self.response.out.write('\n Move how many troops?')
            for i in range(1,game.getTroops(fromCountry),1):
                self.response.out.write('\n <a href="/games/'+name+'/fortify/'+fromCountry+'/'+toCountry+'/'+str(i)+'">'+str(i)+'</a>')
            self.response.out.write('<br>\n <a href="/games/'+name+'/select">cancel<br></a>')
        
        if game.getLastAttack(email) and game.showAttackResult:
            self.response.out.write('''<br>Attack Results:''')
            if game.lastAttack['captured']:
                self.response.out.write('''<br>Territory Captured!''')
            self.response.out.write('''
            <br>Attacking Rolls: '''+repr(game.lastAttack['attack'])+'''
            <br>Defending Rolls: '''+repr(game.lastAttack['defense'])+'''
            <br>Attacking Troops Lost: '''+str(game.lastAttack['attackersKilled'])+'''
            <br>Defending Troops Lost: '''+str(game.lastAttack['defendersKilled'])+'''<br>''')
        

        self.response.out.write('\n <div style="position: relative; z-index:100"> <img src=/pics/toConvertOriginal.png>')
        self.response.out.write('\n <font color="FFFFFF">')
        playerColorMap = {}
        colors = ['blueCircle','redCircle','orangeCircle','greenCircle','pinkCircle']
        i=0
        for player in game.getPlayers():
            playerColorMap[player]='/pics/'+colors[i]+'.png'
            i+=1

        i=0
        for country in game.getCountries():
            if game.getTurn() != email:
                link = None
            elif game.getStage() == 'reinforce':
                if game.isOwned(country, email):
                    link = '/games/'+name+'/reinforce/'+country+'/1'
                else:
                    link = None
            elif game.getStage() == 'attacks':
                if len(game.getSelection()) == 0:
                    if game.isOwned(country, email) and game.getTroops(country)>1:
                        link = '/games/'+name+'/select/'+country
                    else:
                        link = None
                elif len(game.getSelection()) == 1:
                    if not game.isOwned(country, email) and game.isTouching(country, game.getSelection()[0]):
                        link = '/games/'+name+'/select/'+game.getSelection()[0]+'/'+country
                    else:
                        link = None
                elif len(game.getSelection()) == 2:
                    link = None
            elif game.getStage() == 'fortify':
                if len(game.getSelection()) == 0:
                    if game.isOwned(country, email):
                        link = '/games/'+name+'/select/'+country
                    else:
                        link = None
                elif len(game.getSelection()) == 1:
                    if game.isOwned(country, email) and game.isTouching(country, game.getSelection()[0]):
                        link = '/games/'+name+'/select/'+game.getSelection()[0]+'/'+country
                    else:
                        link = None
                else:
                    link = None

            cors = game.getCordinates(country)
            x = cors[0] - 10
            y = cors[1] - 10
            color = playerColorMap[game.getOwner(country)]
            self.response.out.write('''\n     
            <div style="position: absolute; left: '''+str(x)+'''; top: '''+str(y)+'''; z-index: 200" title="name: '''+country+'''">''')
            if link:
                self.response.out.write('''<a href="'''+link+'''" style="text-decoration: none">''')
            self.response.out.write('''
                    <font color="FFFFFF">
                    <div style="position: absolute; left: 4; z-index: 400">'''+str(game.getTroops(country))+'''</div>
                    <div style="position: absolute; z-index: 300"><img src="'''+color+'''"; id="'''+str(i)+'''"></div>''')
            if country in game.getSelection():
                self.response.out.write('''\n<div style="position: absolute; left: -5; top: -5; z-index: 250"> <img src=/pics/highlight.png></div>''')
            self.response.out.write('''\n</font>''')
            if link:
                self.response.out.write('''</a>''')
            self.response.out.write('''</div>''')
            
            i+=1

        self.response.out.write('\n </div>')
        self.response.out.write('\n </font>')
       
        self.response.out.write('\n <div style="position:relative">')
        #self.response.out.write('''
        #<script type="text/javascript">
        #var myVar = 'hello';
        #window.alert(myVar);
        #</script>
        #''')
        
        self.response.out.write('Turn Order: ')
        for player in game.getPlayers():
            self.response.out.write(player+', '+playerColorMap[player][6:-10]+'; ')
        #mapString = game.display()
        #mapString = mapString.replace('\n','<br>')
        #self.response.out.write('<tt><pre>')
        #self.response.out.write(mapString)
        #self.response.out.write('</tt></pre><br><br><br>')


        self.response.out.write('</div> </html> </body>')

    def post(self, name):
        text = cgi.escape(self.request.get('content'))
        loader = Loader(name)
        game = loader.load()
        result = parseInput(text,game)
        if result:
            loader.save(game)
        self.redirect('/games/'+name)
    
class UpdateSelection(webapp.RequestHandler):
    def get(self, name, urlAfterAction=''):
        words = urlAfterAction.split('/')
        if len(words) > 2:
            raise Exception, "Selection list should only ever have 2 countries in it"
        loader = Loader(name)
        game = loader.load()
        if words == [""]:
            game.clearSelection()
        else:
            for word in words:
                if not game.isCountry(word):
                    raise Exception, "entry "+word+" is not a country"
            game.setSelection(words)
        game.showAttackResult = False
        loader.save(game)
        self.redirect('/games/'+name)

class Reinforce(webapp.RequestHandler):
    def get(self, name, country, howMany):
        user = users.get_current_user()
        loader = Loader(name)
        game = loader.load()
        result = game.reinforce(country,int(howMany),user.email())
        if result:
            loader.save(game)
        self.redirect('/games/'+name)

class Attack(webapp.RequestHandler):
    def get(self, name, fromCountry, toCountry, howMany):
        user = users.get_current_user()
        loader = Loader(name)
        game = loader.load()
        result = game.attack(fromCountry,toCountry,int(howMany),user.email())
        if result:
            if game.getTroops(fromCountry)<2:
                game.clearSelection()
                game.justMadeFreeMove = True
            loader.save(game)
            self.redirect('/games/'+name)
        else:
            self.redirect('/games/'+name)
            return
            self.response.out.write("<html><body>")
            self.response.out.write('Problem processing order')
            self.response.out.write('<br>game problem description:<br>')
            self.response.out.write('troops in from country: '+str(game.getTroops(fromCountry)))
            self.response.out.write('troops in to country: '+str(game.getTroops(toCountry)))
            self.response.out.write('attacking with: '+howMany)
            self.response.out.write('hm...')
            self.response.out.write('fill out an error report?')
            self.response.out.write('</body></html>')
                        
class Freemove(webapp.RequestHandler):
    def get(self, name, fromCountry, toCountry, howMany):
        user = users.get_current_user()
        loader = Loader(name)
        game = loader.load()
        
        result = game.freeMove(fromCountry,toCountry,int(howMany),user.email())
        if result:
            game.clearSelection()
            loader.save(game)
            self.redirect('/games/'+name)
        else:
            self.response.out.write("<html><body>")
            self.response.out.write('Problem processing order')
            self.response.out.write('</body></html>')
                        
class Fortify(webapp.RequestHandler):
    def get(self, name, fromCountry, toCountry, howMany):
        user = users.get_current_user()
        loader = Loader(name)
        game = loader.load()
        result = game.fortify(fromCountry,toCountry,int(howMany),user.email())
        if result:
            game.clearSelection()
            loader.save(game)
            self.redirect('/games/'+name)
        else:
            self.response.out.write("<html><body>")
            self.response.out.write('Problem processing order')
            self.response.out.write('</body></html>')

class Skip(webapp.RequestHandler):
    def get(self, name):
        user = users.get_current_user()
        loader = Loader(name)
        game = loader.load()
        result = game.skip(user.email())
        if result:
            game.clearSelection()
            loader.save(game)
            self.redirect('/games/'+name)
        else:
            self.response.out.write("<html><body>")
            self.response.out.write('Problem processing order')
            self.response.out.write('</body></html>')

application = webapp.WSGIApplication([
('/games/(.*)/parse', PlayRisk),
('/games/(.*)/reinforce/(.*)/(.*)', Reinforce),
('/games/(.*)/attack/(.*)/(.*)/(.*)', Attack),
('/games/(.*)/freemove/(.*)/(.*)/(.*)', Freemove),
('/games/(.*)/fortify/(.*)/(.*)/(.*)', Fortify),
('/games/(.*)/select/(.*)', UpdateSelection),
('/games/(.*)/select', UpdateSelection),
('/games/(.*)/skip', Skip),
('/games/(.*)', PlayRisk),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__=='__main__':
    main()
