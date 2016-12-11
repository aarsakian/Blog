import unittest
from datetime import datetime
from flask_testing import TestCase
from flask import url_for, render_template
from blog import app
from blog.views import CODEVERSION, fetch_everything_from_db, calculate_work_date_stats, find_update_of_site
from google.appengine.ext import testbed
from google.appengine.api import users
from google.appengine.ext import ndb, db
from blog.forms import PostForm
from blog.models import Tags, Posts, Categories, BlogPost
from blog.utils import find_tags_to_be_deleted_from_an_edited_post

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

        self.tags = Tags()
        self.categories = Categories()
        self.posts = Posts()

    def test_edit_url_resolves_to_edit_page_view(self):

        passed_days, remaining_days = calculate_work_date_stats()
        form = PostForm()

        response = self.client.get((url_for('tags')))
        if self.posts:
            posts_json = self.posts.to_json()
            site_updated = find_update_of_site(self.posts[len(self.posts)-1])
        else:
            site_updated = 'NA'
            posts_json = []

        rendered_template = render_template('main.html',user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=self.tags,categories=self.categories,
                           posts=posts_json,
                           codeversion=CODEVERSION, form=form)


        self.assertEqual(rendered_template, response.data)

    def test_index_page_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('index')))  # create a request object

        rendered_template = render_template("index.html",user_status=users.is_current_user_admin(),siteupdated='NA',\
                           daysleft=remaining_days,dayspassed=passed_days,tags=self.tags,categories=self.categories,
                           posts=self.posts.to_json(),
                           codeversion=CODEVERSION)
        self.assertEqual(rendered_template, response.data)

    def test_selected_post_page_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        post = self.posts.get_by_title("this is a summary")
        print (post)
        post_tag_names = post.get_tags()

        other_posts_tags = self.posts.get_other_tags(post.key().id())

        related_posts = []
        print url_for('post', year=post.timestamp.year,
                                           month=post.timestamp.month, title=post.title)
        response = self.client.get(url_for('post', year=post.timestamp.year,
                                           month=post.timestamp.month, title=post.title))
        for post in self.posts:
            if post != post:
                for tag in post.tags:
                    if tag in other_posts_tags:
                        related_posts.append(post)

        rendered_template = render_template('singlepost.html',user_status=users.is_current_user_admin(),siteupdated='NA',\
                           daysleft=remaining_days, dayspassed=passed_days,RelatedPosts=related_posts,\
                           Post=post, posttagnames=post_tag_names)



        self.assertEqual(rendered_template, response.data)


    def tearDown(self):
        self.testbed.deactivate()

if __name__ == '__main__':
    unittest.main()
