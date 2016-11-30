import unittest, subprocess
from flask_testing import TestCase
from flask import url_for, render_template
from blog import app
from blog.views import CODEVERSION, fetch_everything_from_db, calculate_work_date_stats, find_update_of_site
from google.appengine.ext import testbed
from google.appengine.api import users
from google.appengine.ext import ndb, db
from blog.forms import PostForm
from blog.models import Tags, Posts, Categories

class MyTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        # enable memcache
        self.testbed.init_memcache_stub()

        self.testbed.init_user_stub()

        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def test_edit_url_resolves_to_edit_page_view(self):
        posts, tags, categories = fetch_everything_from_db()
        passed_days, remaining_days = calculate_work_date_stats()
        form = PostForm()

        response = self.client.get((url_for('tags')))
        if posts:
            posts_json = posts.to_json()
            site_updated = find_update_of_site(posts[len(posts)-1])
        else:
            site_updated = 'NA'
            posts_json = []

        rendered_template = render_template('main.html',user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags,categories=categories,
                           posts=posts_json,
                           codeversion=CODEVERSION, form=form)


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

    def test_can_get_other_tags_from_post(self):
        pass

    def test_can_add_a_tag(self):
        tags = Tags()
        tag_key = tags.add("a new tag")
        self.assertEqual("a new tag", db.get(tag_key).tag)

    def test_can_delete_a_tag(self):
        pass

    def test_get_keys_of_tags(self):
        tags = Tags()
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = [tags.add(tag) for tag in test_tags]
        self.assertItemsEqual(new_tag_keys, tags.get_keys(test_tags))

    def test_add_a_category(self):
        categories = Categories()
        category_key = categories.add("category")
        self.assertEqual("category", db.get(category_key).category)

    def test_get_key_of_a_category(self):
        pass

    def test_can_add_post(self):
        categories = Categories()
        category_key = categories.add("category")

        tags = Tags()
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = [tags.add(tag) for tag in test_tags]

        posts = Posts()
        post_key = posts.add("a title", "body text", category_key, new_tag_keys)

        self.assertEqual("a title", db.get(post_key).title)
        self.assertEqual("body text", db.get(post_key).body)
        self.assertEqual(category_key, db.get(post_key).category.key())
        self.assertItemsEqual(new_tag_keys, db.get(post_key).tags)


    def tearDown(self):
        self.testbed.deactivate()

if __name__ == '__main__':
    unittest.main()
