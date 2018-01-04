
from . import BlogTestBase

from flask import url_for, redirect

from google.appengine.api import users
from google.appengine.ext import testbed


class TestLogin(BlogTestBase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()

        self.testbed.init_user_stub(enable=True)

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
        return self.client.get('/logout')

    def testLogin(self):
        rv = self.loginUser()

        self.assertEqualHTML(self.client.get(url_for('index')).data.decode('utf-8'), rv.data.decode('utf-8'))

    def testLogout_withLoggedInUser(self):
        self.loginUser()
        rv = self.logoutUser()
        self.assertEqualHTML(redirect(users.create_logout_url('http://localhost/logout')).data.decode('utf-8'),
                             rv.data.decode('utf-8'))

    def testLogout(self):
        rv = self.logoutUser()
        self.assertEqualHTML(redirect(url_for('index')).data.decode('utf-8'),
                             rv.data.decode('utf-8'))