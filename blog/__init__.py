from flask import Flask

from flask_bootstrap import Bootstrap5
from flask_sitemap import Sitemap
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from google.cloud import ndb, storage
import google.auth.credentials
from unittest import mock



import os




sitemap = Sitemap()

csrf = CSRFProtect()

login_manager = LoginManager()








if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):

    app = Flask(__name__, root_path='blog',
                template_folder='templates/production',
                instance_relative_config = True)

    app.config.from_object('blog.settings.Production')
    app.jinja_env.globals['DEV'] = False
    client = ndb.Client()
    storage_client = storage.Client()
    os.environ["BUCKET_NAME"] = 'aarsakian'
else:
    app = Flask(__name__)

    os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"
    os.environ["DATASTORE_PROJECT_ID"] = "test"
    os.environ["BUCKET_NAME"] = "test-bucket"
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    credentials = mock.Mock(spec=google.auth.credentials.Credentials)
    storage_client = mock.create_autospec(storage.Client)
    client = ndb.Client(project="test", credentials=credentials)
    #storage_client = storage.Client(project="test", credentials=credentials)

    mock_bucket = mock.create_autospec(storage.Bucket)
    storage_client.get_bucket.return_value = mock_bucket
    mock_blob = mock.create_autospec(storage.Blob)
    mock_bucket.blob.return_value = mock_blob

    mock_blob.key = ndb.BlobKeyProperty()

    app.config.from_object('blog.settings.Testing')
    app.jinja_env.globals['DEV'] = True


def ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)

    return middleware


bootstrap = Bootstrap5(app)

sitemap.init_app(app)

csrf.init_app(app)

login_manager.init_app(app)
# Wrap the app in middleware.
app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)


from . import views



