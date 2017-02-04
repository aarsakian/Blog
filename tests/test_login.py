import logging


from flask_testing import TestCase
from flask import url_for, render_template, redirect
from blog import app

from blog.views import CODEVERSION, fetch_everything_from_db, calculate_work_date_stats, find_update_of_site
from google.appengine.ext import testbed
from google.appengine.api import users
from google.appengine.ext import ndb
from blog.forms import PostForm
from blog.models import Tags, Posts, Categories, BlogPost
from blog.utils import find_tags_to_be_deleted_from_an_edited_post, find_non_used_tags, \
    find_tags_to_added_from_an_edited_post, find_new_post_tags


class TestModel(TestCase):
    maxDiff = None

    def create_app(self):
        app.config['WTF_CSRF_ENABLED'] = False

        return app

    def setUp(self):
        self.testbed = testbed.Testbed()

        self.testbed.activate()

        self.testbed.init_datastore_v3_stub()

        self.testbed.init_memcache_stub()

        self.testbed.init_user_stub(enable=True)

        ndb.get_context().clear_cache()


    def assertEqualHTML(self, string1, string2, file1='', file2=''):

        u'''
        Compare two unicode strings containing HTML.
        A human friendly diff goes to logging.error() if there
        are not equal, and an exception gets raised.
        '''

        from BeautifulSoup import BeautifulSoup as bs
        import difflib
        def short(mystr):
            max = 20
            if len(mystr) > max:
                return mystr[:max]
            return mystr

        p = []
        for mystr, file in [(string1, file1), (string2, file2)]:
            if not isinstance(mystr, unicode):
                raise Exception(u'string ist not unicode: %r %s' % (short(mystr), file))
            soup = bs(mystr)
            pretty = soup.prettify()
            p.append(pretty)
        if p[0] != p[1]:
            for line in difflib.unified_diff(p[0].splitlines(), p[1].splitlines(), fromfile=file1, tofile=file2):
                logging.error(line)
            raise Exception('Not equal %s %s' % (file1, file2))

    def tearDown(self):
        self.testbed.deactivate()

    def loginUserGAE(self, email='user@example.com', id='123', is_admin=False):
        self.testbed.setup_env(
            user_email=email,
            user_id=id,
            user_is_admin='1' if is_admin else '0',
            overwrite=True)

    def loginUser(self):
        self.loginUserGAE(is_admin=True)
        return self.client.get('/login', follow_redirects=True)

    def logoutUser(self):
        self.loginUserGAE(is_admin=True)
        return self.client.get('/logout')# follow_redirects=True)

    def testLogin(self):
        rv = self.loginUser()
        self.loginUserGAE(is_admin=True)

        self.assertEqualHTML(self.client.get(url_for('index')).data.decode('utf-8'), rv.data.decode('utf-8'))

    def testLogout(self):
        rv = self.logoutUser()
        self.assertEqualHTML(redirect(users.create_logout_url('http://localhost/logout')).data.decode('utf-8'),
                             rv.data.decode('utf-8'))
    