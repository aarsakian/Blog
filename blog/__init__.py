from flask import Flask

from flask_bootstrap import Bootstrap
from flask_sitemap import Sitemap
from flask_wtf.csrf import CSRFProtect


import assets

import os


bootstrap = Bootstrap()

sitemap = Sitemap()

csrf = CSRFProtect()

app = Flask(__name__, root_path='blog',  instance_relative_config=True)

bootstrap.init_app(app)

sitemap.init_app(app)

csrf.init_app(app)


if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    app.config.from_object('blog.settings.Production')
else:
    app.config.from_object('blog.settings.Testing')

    bundles = assets.init(app)


import views



