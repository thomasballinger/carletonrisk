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
        self.response.out.write("<html> <body>")
        self.response.out.write("""
            <script src="js.js" type="text/javascript"></script>
        """)
        loader = Loader(name)
        game = loader.load()
        self.response.out.write(str(game.getPlayers()))
        mapString = game.display()
        #mapString = mapString.replace('\n','<br>')
        self.response.out.write('<tt><pre>')
        self.response.out.write(mapString)
        self.response.out.write('</tt></pre><br><br><br>')
        user = users.get_current_user()
        if game.whosTurn == user.email():
            self.response.out.write('Your turn<br>')
            if game.turnStage == 'reinforce':
                self.response.out.write('Place reinforcements: '+str(game.reinforcementsToPlace[user.email()])+' left to place<br>')
            elif game.turnStage == 'attacks':
                self.response.out.write('Attack adjacent territories')
            elif game.turnStage == 'fortify':
                self.response.out.write('Move troops: '+str(game.fortifiesLeft)+' fortifying moves left')
        elif not user.email() in game.getPlayers():
            self.response.out.write('You are not a participant of this game.<br>')
        elif not user.email() in game.getPlayersAlive():
            self.response.out.write('You have been elimintated from this game.<br>')
        else:
            self.response.out.write('Waiting for '+game.whosTurn+'<br>')
        self.response.out.write('<form action="/games/'+name+'/parse" method="post"'+"""
                    <div><textarea name="content" rows="3" cols="60"></textarea></div>
                    <div><input type="submit" value="ok"></div>
                  </form>
        <br>
        <br>        Syntax Examples:
        <br>        place Mexico 3
        <br>        place 3 Mexico
        <br>        attack USA Canada
        <br>        attack USA Canada 3
        <br>        free move USA Canada 8
        <br>        move Mexico USA 2
        <br>        move Mexico 2 USA
        <br>        move 2 Mexico USA
        <br>        pass
       </html> </body>""")

    def post(self, name):
        user = users.get_current_user()
        text = cgi.escape(self.request.get('content'))
        loader = Loader(name)
        game = loader.load()
        result = parseInput(text,game)
        if result:
            loader.save(game)
        self.redirect('/games/'+name)
                        
application = webapp.WSGIApplication([('/games/(.*)/parse', PlayRisk),('/games/(.*)', PlayRisk)], debug=True)
def main():
    run_wsgi_app(application)
if __name__=='__main__':
    main()
