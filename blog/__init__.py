from flask import Flask

from flask_bootstrap import Bootstrap
from flask_sitemap import Sitemap
from flask_wtf.csrf import CSRFProtect




import os


bootstrap = Bootstrap()

sitemap = Sitemap()

csrf = CSRFProtect()








if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    app = Flask(__name__, root_path='blog',
                template_folder= 'templates/production',
                instance_relative_config = True)


    app.config.from_object('blog.settings.Production')
    app.jinja_env.globals['DEV'] = False
else:

    app = Flask(__name__, root_path='blog',
                instance_relative_config = True)

    app.config.from_object('blog.settings.Testing')
    app.jinja_env.globals['DEV'] = True


bootstrap.init_app(app)

sitemap.init_app(app)

csrf.init_app(app)

pagedown.init_app(app)


import views



