from flask import Flask

from flask_bootstrap import Bootstrap

import os


bootstrap = Bootstrap()

app = Flask(__name__, root_path='blog')
bootstrap.init_app(app)

if os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('blog.settings.Testing')

else:
    app.config.from_object('blog.settings.Production')


import views



