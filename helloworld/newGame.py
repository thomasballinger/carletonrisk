import cgi
from loader import *
from game import Game
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
          <html>
            <body>""")
        user = users.get_current_user()
        if user:
            self.response.out.write('Hello, ' + user.nickname() + '<br>')
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
        self.response.out.write("""</body>
          </html>""")

## for killing entries
#        for longstring in longstrings:
#            longstring.delete()

def cleanString(string):
    for c,r in ((' ','_'),("'",''),('"',''),('/','_over_'),('\\','_slash_'),('?',''),('*','_')):
        while True:
            index = string.find(c)
            if index == -1:
                break
            else:
                string = string[:index]+r+string[index+1:]
    return string

class NewGame(webapp.RequestHandler):
    def post(self):
        text = cleanString(cgi.escape(self.request.get('content')))
        loader = Loader(text)
        if users.get_current_user():
            user = users.get_current_user()
        else:
            user = None
        mapFile = '/maps/worldmap.txt'
        user = users.get_current_user()
        #playerList = [user.email()]+[others?]
        playerList = ['DanBuckleitner@gmail.com', 'ThomasBallinger@gmail.com'] 
        if user.email()!='ThomasBallinger@gmail.com':
            playerList = ['ThomasBallinger@gmail.com',user.email()]
        loader.new(mapFile, playerList)
        self.redirect('/')

        
application = webapp.WSGIApplication(
                                     [('/newgame', MainPage),
                                      ('/newgame/(.*)/(.*)', NewGame),
                                      ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
                
