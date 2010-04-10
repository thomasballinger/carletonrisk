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
        game = loader.load()
        
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
        self.response.out.write('\n <a href="http://jquery.com/">The name of this game is '+name+'<br></a>')

        self.response.out.write('\n <div style="position: relative; z-index:100"> <img src=/pics/toConvertOriginal.png>')
        
        playerColorMap = {}
        colors = ['blueCircle','redCircle','orangeCircle','greenCircle','pinkCircle']
        i=0
        for player in game.getPlayers():
            playerColorMap[player]='/pics/'+colors[i]+'.png'
            i+=1

        if game.getTurn() != game.getWhosTurn:
            link = '/games/'+name
        elif game.getStage() == 'reinforce':
            line = '/games/'+name+'/reinforce'
        elif game.getStage() == 'attacks':
            link = '/games/'+name+'/attack'
        elif game.getStage() == 'fortify':
            link = '/games/'+name+'/fortify'

        i=0
        for country in game.getCountries():
            cors = game.getCordinates(country)
            x = cors[0] - 10
            y = cors[1] - 10
            color = playerColorMap[game.getOwner(country)]
            self.response.out.write('''\n 
                <div style="position: absolute; left: '''+str(x)+'''; top: '''+str(y)+'''; z-index: 200" title="name: '''+country+'''"> 
                    <a href="'''+link+'''">
                    <div style="position: absolute; left: 4; z-index: 400">'''+str(game.getTroops(country))+'''</div>
                    <div style="position: absolute; z-index: 300"><img src="'''+color+'''"; id="'''+str(i)+'''"></div> 
                    </a>
                </div>''')
            i+=1

        self.response.out.write('\n </div>')
       
        self.response.out.write('\n <div style="position:relative">')
        #self.response.out.write('''
        #<script type="text/javascript">
        #var myVar = 'hello';
        #window.alert(myVar);
        #</script>
        #''')
        self.response.out.write(str(game.getPlayers()))
        #mapString = game.display()
        #mapString = mapString.replace('\n','<br>')
        #self.response.out.write('<tt><pre>')
        #self.response.out.write(mapString)
        #self.response.out.write('</tt></pre><br><br><br>')


        if game.whosTurn == email:
            self.response.out.write('Your turn<br>')
            if game.turnStage == 'reinforce':
                self.response.out.write('Place reinforcements: '+str(game.reinforcementsToPlace[email])+' left to place<br>')
            elif game.turnStage == 'attacks':
                self.response.out.write('Attack adjacent territories')
            elif game.turnStage == 'fortify':
                self.response.out.write('Move troops: '+str(game.fortifiesLeft)+' fortifying moves left')
        elif not email in game.getPlayers():
            self.response.out.write('You are not a participant of this game.<br>')
        elif not email in game.getPlayersAlive():
            self.response.out.write('You have been elimintated from this game.<br>')
        else:
            self.response.out.write('Waiting for '+game.whosTurn+'<br>')
        


        self.response.out.write('<form action="/games/'+name+'/parse" method="post">'+'''
                    <div><textarea name="content" rows="3" cols="60"></textarea></div>
                    <div><input type="submit" value="ok"></div>
                  </form>
            </div>
        </html> </body>''')

    def post(self, name):
        text = cgi.escape(self.request.get('content'))
        loader = Loader(name)
        game = loader.load()
        result = parseInput(text,game)
        if result:
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
        else:
            self.response.out.write("<html><body>")
            self.response.out.write('Problem processing order')
            self.response.out.write('</body></html>')

class Attack(webapp.RequestHandler):
    def get(self, name, fromCountry, toCountry, howMany):
        user = users.get_current_user()
        loader = Loader(name)
        game = loader.load()
        result = game.attack(fromCountry,toCountry,int(howMany),user.email())
        if result:
            loader.save(game)
            self.redirect('/games/'+name)
        else:
            self.response.out.write("<html><body>")
            self.response.out.write('Problem processing order')
            self.response.out.write('</body></html>')
                        
class Freemove(webapp.RequestHandler):
    def get(self, name, fromCountry, toCountry, howMany):
        user = users.get_current_user()
        loader = Loader(name)
        game = loader.load()
        result = game.freeMove(fromCountry,toCountry,int(howMany),user.email())
        if result:
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
('/games/(.*)/skip', Skip),
('/games/(.*)', PlayRisk),
], debug=True)
def main():
    run_wsgi_app(application)
if __name__=='__main__':
    main()
