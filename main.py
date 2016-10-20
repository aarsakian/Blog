from google.appengine.ext.appstats import recording
from google.appengine.ext.webapp.util import run_wsgi_app
from blog import app
app=run_wsgi_app(app)
