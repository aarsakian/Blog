from flask import Flask
import settings

app = Flask('blog')
app.config.from_object('blog.settings')

if app.config['DEBUG']:
   app.debug=True  


import views
