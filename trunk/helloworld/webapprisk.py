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
        longstrings = db.GqlQuery("SELECT * FROM LongString ORDER BY date")
        user = users.get_current_user()
        if user:
            self.response.out.write('Hello, ' + user.nickname() + '<br>')
        else:
            self.redirect(users.create_login_url(self.request.uri))
        for longstring in longstrings:
            if longstring.name:
                self.response.out.write('<a href="/games/'+longstring.name+'">'+longstring.name+'</a>')
                self.response.out.write('<br>')
        self.response.out.write("""<br><form action="/sign" method="post">
                <div><textarea name="content" rows="3" cols="60"></textarea></div>
                <div><input type="submit" value="Make new game with name above"></div>
              </form>
            </body>
          </html>""")
## for killing entries
#        for longstring in longstrings:
#            longstring.delete()

def cleanString(string):
    for c,r in ((' ','_'),("'",''),('"',''),('/','_over_'),('\\','_slash_')):
        while True:
            index = string.find(c)
            if index == -1:
                break
            else:
                string = string[:index]+r+string[index+1:]
    return string

class Guestbook(webapp.RequestHandler):
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
                                     [('/', MainPage),
                                      ('/sign', Guestbook),
                                      ('/games', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
                
