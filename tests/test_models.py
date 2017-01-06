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
from blog.models import Tags, Posts, Categories
from blog.utils import find_tags_to_be_deleted_from_an_edited_post, find_tags_to_added_from_an_edited_post, \
    find_new_post_tags, find_non_used_tags

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

    def test_add_a_tag(self):
        tag_keys = self.tags.add(["a new tag"])
        self.assertEqual("a new tag", db.get(tag_keys[0]).tag)

    def test_add_tags(self):
        tag_keys = self.tags.add(["a new tag", "a second new tag"])
        self.assertItemsEqual(["a new tag", "a second new tag"],
                              [db.get(tag_keys[0]).tag, db.get(tag_keys[1]).tag])

    def test_delete_a_tag(self):
        self.tags.add(["a new tag"])
        self.tags.delete("a new tag")
        self.assertItemsEqual([], self.tags)

    def test_delete_tags(self):
        self.tags.add(["a new tag", "a second new tag"])
        self.tags.delete(["a new tag", "a second new tag"])
        self.assertItemsEqual([], self.tags)

    def test_get_keys_of_tags(self):
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.assertItemsEqual(new_tag_keys, self.tags.get_keys(test_tags))

    def test_add_a_category(self):
        category_key = self.categories.add("category")
        self.assertEqual("category", db.get(category_key).category)

    def test_delete_a_category(self):
        self.categories.add("category")
        self.categories.delete("category")
        self.assertItemsEqual([], self.categories)

    def test_get_key_of_a_category(self):
        self.assertEqual(self.categories.add("category"), self.categories.get_key("category"))

    def test_add_a_post(self):

        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        self.assertEqual("a title", db.get(post_key).title)
        self.assertEqual("body text", db.get(post_key).body)
        self.assertEqual("this is a summary", db.get(post_key).summary)
        self.assertEqual(category_key, db.get(post_key).category.key())
        self.assertItemsEqual(new_tag_keys, db.get(post_key).tags)

    def test_get_tags_from_posts(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        self.posts.add("a title", "body text", category_key, new_tag_keys)

        self.assertItemsEqual(test_tags, self.posts.get_tags())

    def test_get_empty_tags_from_posts(self):
        category_key = self.categories.add("category")

        test_tags = []
        new_tag_keys = self.tags.add(test_tags)

        self.posts.add("a title", "body text", category_key, new_tag_keys)

        self.assertItemsEqual(test_tags, self.posts.get_tags())

    def test_get_tags_from_a_post(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        self.posts.add("a title", "body text", category_key, new_tag_keys)
        for post in self.posts:
            self.assertItemsEqual(test_tags, post.get_tag_names())

    def test_get_other_tags_from_a_post(self):
        category_key = self.categories.add("category")

        test_tags1 = ["a new tag", "a new new tag"]
        test_tags2 = ["a new tag 1", "a new new tag 2"]

        new_tag_keys1 = self.tags.add(test_tags1)
        new_tag_keys2 = self.tags.add(test_tags2)

        post_key1 = self.posts.add("a title", "body text", category_key, new_tag_keys1)
        self.posts.add("a title 2", "body text 2", category_key, new_tag_keys2)
        self.assertItemsEqual(test_tags2, self.posts.get_other_tags(post_key1.id()))

    def test_find_tags_to_be_deleted_from_an_edited_post(self):
        category_key = self.categories.add("category")

        test_existing_tags = ["a new tag", "a new new tag"]
        editing_tags1 = ["a new tag 1", "a new new tag 2"]
        editing_tags2 = ["a new tag 1", "a new tag"]

        tag_keys = self.tags.add(test_existing_tags)

        self.posts.add("a title", "body text", category_key, tag_keys)

        # scenario to delete all tags "a new tag", "a new new tag"
        tags_to_be_removed = find_tags_to_be_deleted_from_an_edited_post(editing_tags1, test_existing_tags)
        self.assertItemsEqual(tags_to_be_removed,  test_existing_tags)

        # scenario to delete one tag "a new new tag"
        tags_to_be_removed = find_tags_to_be_deleted_from_an_edited_post(editing_tags2, test_existing_tags)
        self.assertItemsEqual(tags_to_be_removed, ["a new new tag"])

        # scenario not to delete any tag
        tags_to_be_removed = find_tags_to_be_deleted_from_an_edited_post(test_existing_tags, test_existing_tags)
        self.assertItemsEqual(tags_to_be_removed, [])

    def test_find_tags_to_be_added_from_an_edited_post(self):
        category_key = self.categories.add("category")

        test_existing_tags = ["a new tag", "a new new tag"]
        editing_tags1 = ["a new tag 1", "a new new tag 2"]
        editing_tags2 = ["a new tag 1", "a new tag"]

        tag_keys = self.tags.add(test_existing_tags)

        self.posts.add("a title", "body text", category_key, tag_keys)

        # scenario to add all tags "a new tag", "a new new tag"
        tags_to_be_added = find_tags_to_added_from_an_edited_post(editing_tags1, test_existing_tags)
        self.assertItemsEqual(tags_to_be_added,  editing_tags1)

        # scenario to add one tag "a new tag 1"
        tags_to_be_added = find_tags_to_added_from_an_edited_post(editing_tags2, test_existing_tags)
        self.assertItemsEqual(tags_to_be_added, ["a new tag 1"])

        # scenario not to delete any tag
        tags_to_be_added= find_tags_to_added_from_an_edited_post(test_existing_tags, test_existing_tags)
        self.assertItemsEqual(tags_to_be_added, [])

    def test_edit_post(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        post = db.get(post_key)
        post.edit("a modified title", "a modified body text", datetime.now(), new_tag_keys, category_key)

        self.assertEqual("a modified title", db.get(post_key).title)
        self.assertEqual("a modified body text", db.get(post_key).body)
        self.assertEqual(category_key, db.get(post_key).category.key())
        self.assertItemsEqual(new_tag_keys, db.get(post_key).tags)

    def test_delete_post(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        self.posts.delete(post_key)
        self.assertItemsEqual(self.posts, [])

    def test_find_new_post_tags(self):

        category_key = self.categories.add("category")

        test_existing_tags = ["a new tag", "a new new tag"]
        editing_tags = ["a new tag 1", "a new new tag 2"]
        editing_tags2 = ["a new tag", "a new new tag 2"]

        tag_keys = self.tags.add(test_existing_tags)

        post_key = self.posts.add("a title", "body text", category_key, tag_keys)
        updating_post = db.get(post_key)
        existing_tags = self.posts.get_tags()
        old_post_tags = updating_post.get_tag_names()

        tags_to_be_deleted = find_tags_to_be_deleted_from_an_edited_post(editing_tags, old_post_tags)
        tags_to_be_added = find_tags_to_added_from_an_edited_post(editing_tags, old_post_tags )

        # scenario to add all tags "a new tag 1", "a new new tag 1"
        new_post_tags = find_new_post_tags(old_post_tags, tags_to_be_deleted, tags_to_be_added)

        self.assertItemsEqual(editing_tags, new_post_tags)

        # scenario to add one tag "a new tag 1"
        tags_to_be_deleted = find_tags_to_be_deleted_from_an_edited_post(editing_tags2, old_post_tags)
        tags_to_be_added = find_tags_to_added_from_an_edited_post(editing_tags2, old_post_tags )
        new_post_tags = find_new_post_tags(old_post_tags, tags_to_be_deleted, tags_to_be_added)

        self.assertItemsEqual(editing_tags2, new_post_tags)

    def test_to_json_of_posts(self):
        category_key1 = self.categories.add("category 1")
        category_key2 = self.categories.add("category 2")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key1 = self.posts.add("a title", "body text", category_key1, new_tag_keys, "a summary")
        post_key2 = self.posts.add("a new title", "new body text", category_key2, new_tag_keys, "a summary  2")

        json_result = [{'body':  db.get(post_key1).body, 'category': db.get(post_key1).category.category
                           , 'updated':
                        db.get(post_key1).updated, 'tags':
                        [db.get(db.get(post_key1).tags[0]).tag,  db.get(db.get(post_key1).tags[1]).tag],
                        'timestamp':  db.get(post_key1).timestamp,
                        'title':  db.get(post_key1).title, 'id': db.get(post_key1).key().id(),
                        'summary':db.get(post_key1).summary},
                        {'body':  db.get(post_key2).body, 'category': db.get(post_key2).category.category
                            , 'updated':
                        db.get(post_key2).updated, 'tags':
                        [db.get(db.get(post_key2).tags[0]).tag,  db.get(db.get(post_key2).tags[1]).tag],
                        'timestamp':  db.get(post_key2).timestamp,
                        'title':  db.get(post_key2).title, 'id': db.get(post_key2).key().id(),
                         'summary':db.get(post_key2).summary}]
        self.assertEqual(json_result, self.posts.to_json())

    def test_retrieve_from_memcache(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        posts = Posts.retrieve_from_memcache("POSTS_CACHE")
        self.assertEqual(posts[0].key(), post_key)

        # edit test
        post = db.get(post_key)

        new_test_tags = ["a new tag 1", "a new new tag2"]
        new_tag_keys = self.tags.add(new_test_tags)

        post.edit("a modified title 2", "a modified body text", datetime.now(), new_tag_keys, category_key)

        self.posts.update()
        posts = Posts.retrieve_from_memcache("POSTS_CACHE")
        self.assertEqual(posts[0].title, "a modified title 2")
        self.assertItemsEqual(posts[0].tags, new_tag_keys)

    def test_get_by_title(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)
        post = self.posts.get_by_title("a title")
        self.assertEqual(post_key, post.key())

    def test_get_by_title_assert_raises(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        self.posts.add("a title", "body text", category_key, new_tag_keys)
        # test exception
        with self.assertRaises(LookupError):
            self.posts.get_by_title("a non existent title")

    def test_find_non_used_tags(self):
        remaining_tags = ["tag1", "tag2"]
        test_tags = ["tag1", "tag3"]

        non_used_tags = find_non_used_tags(test_tags, remaining_tags)
        self.assertItemsEqual(non_used_tags, ["tag3"])

    def test_get_names_from_tags(self):
        test_tags = ["a new tag", "a new new tag"]
        self.tags.add(test_tags)

        self.assertItemsEqual(test_tags, self.tags.get_names())

    def tearDown(self):
        self.testbed.deactivate()

if __name__ == '__main__':
    unittest.main()
