import cgi
import random

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class GameFile(db.Model):
    name = db.StringProperty()
    pickledGame = db.TextProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("<html><body> Let's play risk!<br>")

        games = db.GqlQuery("SELECT * FROM GameFile ORDER BY name")

        if not users.get_current_user():
            self.response.out.write('you should log into your google account')
        else:
            self.redirect(users.create_login_url(self.request.uri))
        self.response.out.write('games:<br>')
        if games:
            for game in games:
                self.response.out.write("""<button type="button"
                onclick="/game/"""+game.name+"""">"""+game.name+"""</button>""")

            # Write the submission form and the footer of the page
        affirmativeSlogan = random.choice(['"You got my attention"','"I got that"','"Yes, sir!"', '"Right away, sir!"'])
        
        self.response.out.write("""
                  <form action="/game" method="post">
                    <div><textarea name="content" rows="3" cols="60"></textarea></div>
                    <div><input type="submit" value="Create new game"></div>
                  </form>
                  <form action="/makeNode" method="post">
                    <div><textarea name="content" rows="3" cols="60"></textarea></div>
                    <div><input type="submit" value="Play current Game"></div>
                  </form>

                  <img src=pics/hamlet.jpg />
                </body>
              </html>""")

class Gamepage(webapp.RequestHandler):
    def post(self):
        state = State()
        state.name = random.choice(['USA', 'Mexico', 'Canada'])
        state.number = random.randint(1,10)
        if users.get_current_user():
            greeting.author = users.get_current_user()
            state.owner = users.get_current_user()
            
        greeting.content = parseInput(self.request.get('content'))
        
        greeting.put()
        state.put()
        self.redirect('/')


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/game', Gamepage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
