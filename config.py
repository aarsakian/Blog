from blog.settings import Settings


class Config:
  pass


class DevelopmentConfig(Config):
  DEBUG = True


class TestingConfig(Config):
  TESTING = True
  WTF_CSRF_ENABLED = False
  SERVER_NAME = 'http://localhost:9082/'


class ProductionConfig(Config):
  SECRET_KEY = Settings.get('FLASK_SECRET_KEY')




config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}