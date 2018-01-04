from flask import Flask
from config import config
from flask_bootstrap import Bootstrap



bootstrap = Bootstrap()



def create_app(config_name):
   app = Flask(__name__)
   app.config.from_object(config[config_name])
   bootstrap.init_app(app)

   return app


app = create_app('production')

import views
import search




