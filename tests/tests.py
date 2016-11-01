import unittest
from flask_testing import TestCase
from flask import url_for, render_template
from blog import app
from blog.views import CODEVERSION, fetch_everything_from_db, calculate_work_date_stats
from google.appengine.ext import testbed
from google.appengine.api import users
from blog.forms import PostForm

class MyTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        # enable memcache
        self.testbed.init_memcache_stub()

        self.testbed.init_user_stub()

        return app

    def test_edit_url_resolves_to_edit_page_view(self):
        posts, tags, categories = fetch_everything_from_db()
        passed_days, remaining_days = calculate_work_date_stats()
        form = PostForm()

        response = self.client.get("/edit")

        rendered_template = render_template('new_post.html',user_status=users.is_current_user_admin(),siteupdated="",\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags,categories=categories,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION)

        self.assertEqual(rendered_template, response.data)

    def test_index_page_returns_correct_html(self):
        posts, tags, categories = fetch_everything_from_db()
        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('index')))  # create a request object

        rendered_template = render_template("index.html",user_status=users.is_current_user_admin(),siteupdated='NA',\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags,categories=categories,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION)
        self.assertEqual(rendered_template, response.data)


if __name__ == '__main__':
    unittest.main()
