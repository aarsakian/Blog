from flask import Flask

from flask_bootstrap import Bootstrap
from flask_sitemap import Sitemap
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from google.cloud import ndb, storage
import google.auth.credentials
import mock



import os


bootstrap = Bootstrap()

sitemap = Sitemap()

csrf = CSRFProtect()

login_manager = LoginManager()








if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):

    app = Flask(__name__, root_path='blog',
                template_folder= 'templates/production',
                instance_relative_config = True)

    app.config.from_object('blog.settings.Production')
    app.jinja_env.globals['DEV'] = False
    client = ndb.Client()
    storage_client = storage.Client()
else:
    app = Flask(__name__)

    os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"
    os.environ["DATASTORE_PROJECT_ID"] = "test"

    credentials = mock.Mock(spec=google.auth.credentials.Credentials)
    client = ndb.Client(project="test", credentials=credentials)
    storage_client = storage.Client(project="test", credentials=credentials)

    app.config.from_object('blog.settings.Testing')
    app.jinja_env.globals['DEV'] = True


def ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)

    return middleware


bootstrap.init_app(app)

sitemap.init_app(app)

csrf.init_app(app)

login_manager.init_app(app)
# Wrap the app in middleware.
app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)


from . import views



