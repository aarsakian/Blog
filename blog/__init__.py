from flask import Flask
import settings
from flask_bootstrap import Bootstrap


bootstrap = Bootstrap()

app = Flask('blog')
app.config.from_object('blog.settings')

bootstrap.init_app(app)

if app.config['DEBUG']:
   app.debug=True  


import views
import search
