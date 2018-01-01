# appengine_config.py
from google.appengine.ext import vendor

# Add any libraries install in the "lib" folder.
vendor.add('lib')

from flask import Flask
from settings import Config
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import  CsrfProtect



bootstrap = Bootstrap()



def create_app():
   app = Flask(__name__)
   app.config.from_object(Config)
   bootstrap.init_app(app)

   return app


app = create_app()


import views
import search
