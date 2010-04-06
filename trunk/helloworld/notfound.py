import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
          <html>
            <body>""")
        self.response.out.write('Page not yet implemented')
        self.response.out.write('<br>')
        self.response.out.write("""<a href="/">Back to root<br>
            </body>
          </html>""")
        
application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
                
