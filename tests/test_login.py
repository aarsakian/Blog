
from . import BlogTestBase

from flask import url_for, redirect

from google.appengine.api import users


class TestLogin(BlogTestBase):

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
        return self.client.get('/logout')

    def testLogin(self):
        rv = self.loginUser()

        self.assertEqualHTML(self.client.get(url_for('index')).data.decode('utf-8'), rv.data.decode('utf-8'))

    def testLogout(self):
        rv = self.logoutUser()
        self.assertEqualHTML(redirect(users.create_logout_url('http://localhost/logout')).data.decode('utf-8'),
                             rv.data.decode('utf-8'))
