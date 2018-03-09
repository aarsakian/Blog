from secret_keys import CSRF_SECRET_KEY, SESSION_KEY, EXCLUDED_URLS


class Config(object):
  # Set secret keys for CSRF protection
  SECRET_KEY = CSRF_SECRET_KEY
  CSRF_SESSION_KEY = SESSION_KEY
  SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS = True
  SITEMAP_URL_SCHEME = 'https'
  SITEMAP_IGNORE_ENDPOINTS = EXCLUDED_URLS
  SITEMAP_URL_METHOD = 'https'

  # Flask-Cache settings
  #CACHE_TYPE = 'gaememcached'


class Development(Config):
  DEBUG = True
  # Flask-DebugToolbar settings
  DEBUG_TB_PROFILER_ENABLED = True
  DEBUG_TB_INTERCEPT_REDIRECTS = False
  CSRF_ENABLED = True


class Testing(Config):
  TESTING = True
  DEBUG = True
  CSRF_ENABLED = True


class Production(Config):
  DEBUG = False
  CSRF_ENABLED = True