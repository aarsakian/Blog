import unittest
import json
import logging

from freezegun import freeze_time
from datetime import datetime
from werkzeug.contrib.atom import AtomFeed
from flask_testing import TestCase
from flask import url_for, render_template, request

from google.appengine.ext import testbed
from google.appengine.api import users
from google.appengine.ext import ndb
from blog.forms import PostForm
from blog.models import Tags, Posts, Categories, BlogPost
from blog.utils import find_modified_tags, datetimeformat, make_external,  calculate_work_date_stats
from blog.search import query_search_index, find_posts_from_index


CODEVERSION = ':v0.7'




from . import BlogTestBase

class TestViews(BlogTestBase):
    maxDiff = None

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        # enable memcache
        self.testbed.init_memcache_stub()

        self.testbed.init_user_stub(enable=True)

        self.testbed.init_search_stub(enable=True)

        self.testbed.setup_env(
            USER_EMAIL='test@example.com',
            USER_ID='123',
            USER_IS_ADMIN='1',
            overwrite=True)

        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

        self.tags = Tags()
        self.categories = Categories()
        self.posts = Posts()
        self.form = PostForm()

    def test_tags_view(self):

        passed_days, remaining_days = calculate_work_date_stats()


        response = self.client.get((url_for('view_all_tags')))

        site_updated = self.posts.site_last_updated()

        rendered_template = render_template('tags.html', user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=self.tags.to_json(),
                           codeversion=CODEVERSION)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_categories_view(self):

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('view_all_categories')))

        site_updated = self.posts.site_last_updated()

        rendered_template = render_template('categories.html', user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=self.tags.to_json(),
                           codeversion=CODEVERSION)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_archives_url_resolves_to_archive_page(self):

        passed_days, remaining_days = calculate_work_date_stats()
        

        response = self.client.get((url_for('archives')))

        post_tag_names = self.tags.to_json()

        site_updated = self.posts.site_last_updated()
        posts_json = self.posts.to_json()
        rendered_template = render_template('archives.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=posts_json,
                                            codeversion=CODEVERSION, form=self.form, posts_tags_names=post_tag_names)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_archives_url_content_is_ok(self):

        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        passed_days, remaining_days = calculate_work_date_stats()
        

        response = self.client.get((url_for('archives')))

        post_tag_names = self.tags.to_json()

        site_updated = self.posts.site_last_updated()
        posts_json = self.posts.to_json()
        rendered_template = render_template('archives.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=posts_json,
                                            codeversion=CODEVERSION, form=self.form, posts_tags_names=post_tag_names)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_index_page_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get('/')  # create a request object
        site_updated = self.posts.site_last_updated()
        rendered_template = render_template("posts.html", user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=self.posts.to_json(),
                                            codeversion=CODEVERSION,
                                            form=self.form)
        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_index_page_with_content_is_ok(self):

        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('index')))  # create a request object

        site_updated = self.posts.site_last_updated()

        rendered_template = render_template("posts.html", user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated,
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=self.posts.to_json(),
                                            codeversion=CODEVERSION, form=self.form)
        self.assertEqualHTML(rendered_template.decode('utf-8'), response.data.decode('utf-8'))

    def test_selected_post_page_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        current_post = self.posts.get_by_title("a title")

        post_tag_names = current_post.get_tag_names()

        other_posts_tags = self.posts.get_other_tags(current_post.key.id())

        related_posts = []

        response = self.client.get(url_for('view_a_post', category="category", year=current_post.timestamp.year,
                                           month=current_post.timestamp.month, title="a title"))
        for post in self.posts:
            if post.key != current_post.key:
                for tag in post.tags:
                    if tag in other_posts_tags:
                        related_posts.append(post)

        category = post.category.get().category
        site_updated = self.posts.site_last_updated()
        rendered_template = render_template('singlepost.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, RelatedPosts=related_posts, \
                                            Post=current_post.to_json(), posttagnames=post_tag_names, category=category)

        self.assertEqual(rendered_template.encode("utf-8"), response.data)

    def test_select_post_with_related_posts_returns_correct_html(self):
        passed_days, remaining_days = calculate_work_date_stats()

        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        test_tags_related = ["a new tag", "a different tag"]
        new_rel_tag_keys = self.tags.add(test_tags_related)
        self.posts.add("a better title", "body without text",
                       category_key, new_rel_tag_keys, "this is new a summary")

        current_post = self.posts.get_by_title("a title")
        post_tag_names = current_post.get_tag_names()

        other_posts_tags = self.posts.get_other_tags(current_post.key.id())

        related_posts = []

        response = self.client.get(url_for('view_a_post', category="category", year=current_post.timestamp.year,
                                           month=current_post.timestamp.month, title="a title"))

        related_posts = self.posts.get_related_posts(current_post.id)


        category = current_post.category.get().category
        site_updated = self.posts.site_last_updated()
        rendered_template = render_template('singlepost.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, RelatedPosts=related_posts, \
                                            Post=current_post.to_json(), posttagnames=post_tag_names, category=category)

        self.assertEqual(rendered_template.encode("utf-8"), response.data)

    def test_tag_pag_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('index')))  # create a request object
        site_updated = self.posts.site_last_updated()
        rendered_template = render_template("posts.html", user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=self.posts.to_json(),
                                            codeversion=CODEVERSION, form=self.form)
        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_delete_post(self):

        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        response = self.client.delete(url_for('delete_post', id=post_key.id()))

        self.assertEqual("OK", response.json["msg"])

    def test_get_post(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]

        existing_tag_keys = self.tags.add(existing_tags)

        post_key = self.posts.add("a title", "body text", category_key, existing_tag_keys, "this is a summary")

        asked_post = post_key.get()

        post_tag_names = asked_post.get_tag_names()

        tag_names = self.tags.get_names()

        data = {u"title": asked_post.title, u"body": asked_post.body, u"category":
            asked_post.category.get().category,
                 u"catid": str(category_key.id()).decode('utf8'), u"id": str(asked_post.key.id()).decode('utf8'), \
                 u"tags": post_tag_names,
                 u"date": asked_post.timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8')
                    , u"updated":
                     asked_post.updated.strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8'),
                 }

        response = self.client.get(url_for("get_post", id=post_key.id()))

        self.assertDictEqual(data, response.json)

    def test_add_post(self):

        existing_tags = [u"a new new tag", u"a new tag"]
        freezer = freeze_time("2017-03-20 17:48:18")
        freezer.start()
        json_data = {u'category': u'category', u'tags': existing_tags, u"summary": u"this is a summary",
                     u'title': u'a title',u'body': u'body text', u'timestamp': datetimeformat(datetime.now())
                ,
                     u'updated': datetimeformat(datetime.now())
             }

        response = self.client.post(url_for('main'), content_type='application/json',
                                   data=json.dumps(json_data))
        json_data[u"id"] = u'4'
        self.assertDictEqual(json_data, response.json)
        freezer.stop()

    def test_api_posts(self):
        existing_tags = [u"a new new tag", u"a new tag"]
        freezer = freeze_time("2017-03-20 17:48:18")
        freezer.start()
        json_data = {u'category': u'category', u'tags': existing_tags, u"summary": u"this is a summary",
                     u'title': u'a title', u'body': u'body text', u'timestamp': datetimeformat(datetime.now())
            ,
                     u'updated': datetimeformat(datetime.now())
                     }

        self.client.post(url_for('main'), content_type='application/json',
                         data=json.dumps(json_data))

        response = self.client.get(url_for('main'))

        json_data[u"id"] = u'4'
        self.assertDictEqual(json_data, response.json[0])
        freezer.stop()

    def test_no_post(self):

        json_data = {}

        response = self.client.get(url_for('main'))

        self.assertDictEqual(json_data, response.json)

    def test_edit_post(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]
        editing_tags = ["a new tag", "tag to added"]  # final tags are "a new tag", "tag to added"

        existing_tag_keys = self.tags.add(existing_tags)

        post_key = self.posts.add("a title", "body text", category_key, existing_tag_keys, "this is a summary")

        self.posts.add("a title 2", "body text 2", category_key, existing_tag_keys, "this is a summary 2")

        updating_post = post_key.get()

        json_data = {'category': 'category', 'tags': editing_tags, 'title': 'a title', 'body': 'body text'}

        response = self.client.put(url_for('edit_post', id=post_key.id()), content_type='application/json',
                                   data=json.dumps(json_data))

        tag_names = [u"a new tag", u"a new new tag", u"tag to added"]
        post_tag_names = [u"a new tag", u"tag to added"]

        data = {u"title": updating_post.title, u"body": updating_post.body, u"category":
            updating_post.category.get().category,
                 u"catid": str(category_key.id()).decode('utf8'), u"id": str(updating_post.key.id()).decode('utf8'), \
                 u"tags": post_tag_names,
                 u"date": updating_post.timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8')
                    , u"updated":
                     updating_post.updated.strftime('%a, %d %b %Y %H:%M:%S GMT').decode('utf8'),
                 }

        self.assertDictEqual(data, response.json)

    def test_edit_a_post_view(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]

        existing_tag_keys = self.tags.add(existing_tags)

        post_key = self.posts.add("a title", "body text", category_key, existing_tag_keys, "this is a summary")

        response = self.client.get(url_for('edit_a_post_view', postkey=post_key))

        site_updated = self.posts.site_last_updated()
        passed_days, remaining_days = calculate_work_date_stats()

        rendered_template = render_template('posts.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days,
                                            codeversion=CODEVERSION, form=self.form)

        self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    def test_about_page(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]

        existing_tag_keys = self.tags.add(existing_tags)

        self.posts.add("about", "body text", category_key, existing_tag_keys, "this is a summary")

        requested_post = self.posts.get_by_title('about')

        response = self.client.get(url_for('aboutpage'))

        passed_days, remaining_days = calculate_work_date_stats()

        site_updated = self.posts.site_last_updated()

        rendered_template = render_template('about.html',user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,Post=requested_post,
                           codeversion=CODEVERSION)

        self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    def test_searchresults(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]

        existing_tag_keys = self.tags.add(existing_tags)

        self.posts.add("about", "body text", category_key, existing_tag_keys, "this is a summary")

        passed_days, remaining_days = calculate_work_date_stats()

        site_updated = self.posts.site_last_updated()

        rendered_template = render_template("posts.html",  user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days,
                                            posts=self.posts.to_json(),
                                            codeversion=CODEVERSION, form=self.form)

        response = self.client.get(url_for('searchresults', q="body"))

        self.assertEqualHTML( response.data.decode('utf8'),rendered_template.decode('utf8'))

    def test_search_query(self):

        category_key = self.categories.add("category")
        existing_tags = ["a new tag", "a new new tag"]
        existing_tag_keys = self.tags.add(existing_tags)

        self.posts.add("about", "body text", category_key, existing_tag_keys, "this is a summary")

        query_string = "body"
        results = query_search_index(query_string)
        posts_ids = find_posts_from_index(results)
        self.posts.filter_matched(posts_ids)

        response = self.client.get(url_for('searchsite', query="body"))

        return self.assertDictEqual({u'data':self.posts.to_json()}, response.json)

    def test_view_filtered_posts_by_tag(self):

        category_key = self.categories.add("category")
        existing_tags = ["a new tag", "a new new tag"]
        existing_tag_keys = self.tags.add(existing_tags)

        self.posts.add("about", "body text", category_key, existing_tag_keys)

        second_tags = ["a new second tag", "a new new second tag"]
        second_tag_keys = self.tags.add(second_tags)

        self.posts.add("about second post", "body secod text", category_key, second_tag_keys)

        self.posts.filter_by_tag('a new tag')

        passed_days, remaining_days = calculate_work_date_stats()
        site_updated = self.posts.site_last_updated()
        rendered_template = render_template("posts.html",  user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days,
                                            tags=self.tags, categories=self.categories,
                                            posts=self.posts.to_json(),
                                            codeversion=CODEVERSION, form=self.form)

        response = self.client.get(path='/tags/a new tag')

        return self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    # def test_view_filtered_posts_by_category(self):
    #
    #     category_key = self.categories.add("a category")
    #     existing_tags = ["a new tag", "a new new tag"]
    #     existing_tag_keys = self.tags.add(existing_tags)
    #
    #     self.posts.add("about", "body text", category_key, existing_tag_keys)
    #
    #     second_tags = ["a new second tag", "a new new second tag"]
    #     second_tag_keys = self.tags.add(second_tags)
    #
    #     self.posts.add("about second post", "body secod text", category_key, second_tag_keys)
    #
    #     self.posts.filter_by_category('a category')
    #
    #     passed_days, remaining_days = calculate_work_date_stats()
    #     site_updated = self.posts.site_last_updated()
    #
    #     rendered_template = render_template("posts.html", user_status=users.is_current_user_admin(),
    #                                         siteupdated=site_updated, \
    #                                         daysleft=remaining_days, dayspassed=passed_days,
    #                                         tags=self.tags, categories=self.categories,
    #                                         posts=self.posts.to_json(),
    #                                         codeversion=CODEVERSION, form=self.form)
    #
    #     response = self.client.get(path='/categories/a category')
    #
    #     return self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    def test_404_not_found_page(self):
        response = self.client.get(path='/a path not existing')
        rendered_template = render_template('404.html')

        return self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    def test_wrong_url(self):
        response = self.client.get(path='/category/2017/Jan/a post not existing')

        rendered_template = render_template('404.html')

        self.assertEqual(rendered_template.encode("utf-8"), response.data)


    def test_user(self):
        response = self.client.get(path='/user')
        return self.assertDictEqual({'user_status':users.is_current_user_admin()},response.json)

    def test_redirect_on_search(self):
        response = self.client.get((url_for('index', q="test redirect on search")))  # cre

        return self.assertStatus(response, 302)

    def test_feed(self):
        category_key = self.categories.add("category")
        existing_tags = ["a new tag", "a new new tag"]
        existing_tag_keys = self.tags.add(existing_tags)

        self.posts.add("about", "body text", category_key, existing_tag_keys)

        response = self.client.get(path='/recent.atom')

        feed = AtomFeed('Recent Articles',
                        feed_url='http://localhost/recent.atom', url=request.url_root)

        feed = self.posts.add_to_feed(feed, request.url)

        return self.assertEqual(feed.to_string(), response.data.decode('utf8'))

    def test_rebuild_index(self):
        category_key = self.categories.add("category")
        existing_tags = ["a new tag", "a new new tag"]
        existing_tag_keys = self.tags.add(existing_tags)

        self.posts.add("about", "body text", category_key, existing_tag_keys)

        response = self.client.get(path='/rebuild_index')

        return self.assertStatus(response, 302)