import StringIO
import json
import os
import cloudstorage
from base64 import b64encode

from freezegun import freeze_time as _freeze_time
from datetime import datetime
from werkzeug.contrib.atom import AtomFeed
from werkzeug.http import parse_cookie
from flask_testing import TestCase
from flask import url_for, render_template, request, flash
from flask_wtf.csrf import generate_csrf

from google.appengine.ext import testbed
from google.appengine.api import users
from google.appengine.ext import ndb
from blog.forms import PostForm, AnswerRadioForm
from blog.models import Tags, Posts, Categories, BlogPost
from blog.utils import find_modified_tags, datetimeformat, make_external,  calculate_work_date_stats
from blog.search import query_search_index, find_posts_from_index
from blog import app
from blog.views import accept_google_analytics, MSG
from contextlib import contextmanager
from google.appengine.api import datastore_types
from mock import patch
from freezegun.api import FakeDatetime

CODEVERSION = ':v0.7'

DATEFORMAT = '%A, %d %B %Y'

TEST_IMAGE = u'2019_1_4_16z.gif'
TEST_IMAGE2 = u'12_3_4_3_12z.png'


@contextmanager
def freeze_time(*args, **kwargs):
    with patch('google.appengine.ext.db.DateTimeProperty.data_type',
               new=FakeDatetime):
        datastore_types._VALIDATE_PROPERTY_VALUES[FakeDatetime] = \
            datastore_types.ValidatePropertyNothing
        datastore_types._PACK_PROPERTY_VALUES[FakeDatetime] = \
            datastore_types.PackDatetime
        datastore_types._PROPERTY_MEANINGS[FakeDatetime] = \
            datastore_types.entity_pb.Property.GD_WHEN

        with _freeze_time(*args, **kwargs):
            yield


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

        self.testbed.init_urlfetch_stub()

        self.testbed.init_app_identity_stub()
        self.testbed.init_blobstore_stub()

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

        flash(MSG)

        rendered_template = render_template('tags.html', user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=self.tags.to_json(),
                           codeversion=CODEVERSION)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_categories_view(self):

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('view_all_categories')))

        site_updated = self.posts.site_last_updated()

        flash(MSG)

        rendered_template = render_template('categories.html', user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=self.tags.to_json(),
                           codeversion=CODEVERSION)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_archives_url_resolves_to_archive_page(self):

        passed_days, remaining_days = calculate_work_date_stats()
        
        flash(MSG)
        response = self.client.get((url_for('archives')))

        post_tag_names = self.tags.to_json()

        site_updated = self.posts.site_last_updated()
        posts_json = self.posts.to_json()

        rendered_template = render_template('archives.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=posts_json,
                                            codeversion=CODEVERSION,
                                            form=self.form,
                                            posts_tags_names=post_tag_names)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_archives_url_content_is_ok(self):

        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        passed_days, remaining_days = calculate_work_date_stats()

        flash(MSG)

        response = self.client.get((url_for('archives')))

        post_tag_names = self.tags.to_json()

        site_updated = self.posts.site_last_updated()
        posts_json = self.posts.to_json()

        rendered_template = render_template('archives.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, tags=self.tags,
                                            categories=self.categories,
                                            posts=posts_json,
                                            codeversion=CODEVERSION,
                                            form=self.form,
                                            posts_tags_names=post_tag_names)

        self.assertEqualHTML(rendered_template, response.data.decode('utf-8'))

    def test_index_page_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get('/')  # create a request object
        site_updated = self.posts.site_last_updated()
        flash(MSG)
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
        flash(MSG)
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

        with open(os.path.join(TEST_IMAGE)) as f:
            self.assertTrue(current_post.add_blob(f.read(), TEST_IMAGE))

        response = self.client.get(url_for('view_a_post', category="category", year=current_post.timestamp.year,
                                           month=current_post.timestamp.month, title="a title"))
        for post in self.posts:
            if post.key != current_post.key:
                for tag in post.tags:
                    if tag in other_posts_tags:
                        related_posts.append(post)

        category = post.category.get().category
        site_updated = self.posts.site_last_updated()
        flash(MSG)

        answers_form = AnswerRadioForm()

        answers_form.r_answers.choices = [("t", answer.p_answer) for answer in current_post.answers]

        rendered_template = render_template('singlepost.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, RelatedPosts=related_posts, \
                                            Post=current_post.to_json(), posttagnames=post_tag_names,
                                            category=category,  answers_field=answers_form)

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

        response = self.client.get(url_for('view_a_post', category="category", year=current_post.timestamp.year,
                                           month=current_post.timestamp.month, title="a title"))

        related_posts = self.posts.get_related_posts(current_post.id)


        category = current_post.category.get().category
        site_updated = self.posts.site_last_updated()
        flash(MSG)

        answers_form = AnswerRadioForm()

        answers_form.r_answers.choices = [("t", answer.p_answer) for answer in current_post.answers]

        rendered_template = render_template('singlepost.html', user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days, RelatedPosts=related_posts, \
                                            Post=current_post.to_json(), posttagnames=post_tag_names,
                                            category=category, answers_field=answers_form)

        self.assertEqual(rendered_template.encode("utf-8"), response.data)

    def test_tag_pag_returns_correct_html(self):

        passed_days, remaining_days = calculate_work_date_stats()

        response = self.client.get((url_for('index')))  # create a request object
        site_updated = self.posts.site_last_updated()
        flash(MSG)

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

    def test_delete_post_with_image(self):
        with open(os.path.join(TEST_IMAGE)) as f:
            img_stringIO = StringIO.StringIO(f.read())  # in memory read

        post, _, _ = self.create_post()
        post.add_blob(img_stringIO.read(), TEST_IMAGE)
        response = self.client.delete(url_for('delete_post', id=post.key.id()))

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
                 u"category": category_key.get().category, u"id": str(asked_post.key.id()).decode('utf8'), \
                 u"tags": post_tag_names,
                 u"summary":asked_post.summary,
                 u"timestamp": asked_post.timestamp.strftime(DATEFORMAT).decode('utf8')
                    , u"updated":
                     asked_post.updated.strftime(DATEFORMAT).decode('utf8'),
                u"answers":[], u'images': []
                 }

        response = self.client.get(url_for("get_post", id=post_key.id()))

        self.assertDictEqual(data, response.json)

    def test_add_post(self):

        existing_tags = [u"a new new tag", u"a new tag"]
        freezer = _freeze_time(u"2017-03-20")
        freezer.start()
        json_data = {u'category': u'category', u'tags': existing_tags, u"summary": u"this is a summary",
                     u'title': u'a title',u'body': u'body text', u'timestamp': datetimeformat(datetime.now()).decode("utf-8"),
                     u'updated': datetimeformat(datetime.now()).decode("utf-8"), u"answers" :
                         [{u'p_answer':u'a potential answer', u'is_correct':True,
                           u'statistics': 0.0,    u'nof_times_selected': 0}]}

        response = self.client.post(url_for('main'), content_type='application/json',
                                   data=json.dumps(json_data))
        json_data[u"id"] = u'4'
        json_data[u'images'] = []
        self.assertDictEqual(json_data, response.json)
        freezer.stop()

    def test_api_posts(self):
        existing_tags = [u"a new new tag", u"a new tag"]
        freezer = _freeze_time(u"2017-03-20 17:48:18")
        freezer.start()
        json_data = {u'category': u'category', u'tags': existing_tags, u"summary": u"this is a summary",
                     u'title': u'a title', u'body': u'body text', u'timestamp': datetimeformat(datetime.now())
                .decode("utf-8"),
                     u'updated': datetimeformat(datetime.now()).decode("utf-8"),
                     u"answers":
                         [{u'p_answer': u'a potential answer', u'is_correct': True,
                           u'statistics': 0.0, u'nof_times_selected': 0}]}

        response = self.client.post(url_for('main'), content_type='application/json',
                         data=json.dumps(json_data))

        json_data[u"id"] = u'4'
        json_data[u'images'] = []
        self.assertDictEqual(json_data, response.json)
        freezer.stop()

    def test_api_posts_with_image(self):
        post, _, _ = self.create_post()
        import io
        with open(os.path.join(TEST_IMAGE), 'rb') as f:
            data = dict(
                image=[(io.BytesIO(f.read()), TEST_IMAGE)],
            )

            response = self.client.post(path='/api/posts/{}/images'.format(post.id), data=data,
                                   content_type='multipart/form-data',
                                   follow_redirects=True)

            self.assertDictEqual({'image_key':
                                      u'encoded_gs_file:YXBwX2RlZmF1bHRfYnVja2V0LzIwMTlfMV80XzE2ei5naWY='},
                                 response.json)

        with open(os.path.join(TEST_IMAGE), 'rb') as f:
            data = dict(
                wrong_key=[(io.BytesIO(f.read()), TEST_IMAGE)],
            )

            response = self.client.post(path='/api/posts/{}/images'.format(post.id), data=data,
                                   content_type='multipart/form-data',
                                   follow_redirects=True)
            return self.assertStatus(response, 500)

    def test_api_posts_with_files(self):
        existing_tags = [u"a new new tag", u"a new tag"]
        with freeze_time(u"2019-11-05"):

            with open(TEST_IMAGE, 'rb') as f:
                byte_content = f.read()

            with open(TEST_IMAGE2, 'rb') as f:
                byte_content_2 = f.read()

            images = [{'filename': "C:\\fakepath\\{}".format(TEST_IMAGE),
                      'url': "data:image/jpeg;base64,{}".format(b64encode(byte_content))},
                      {'filename': "C:\\fakepath\\{}".format(TEST_IMAGE2),
                      'url': "data:image/jpeg;base64,{}".format(b64encode(byte_content_2))}]


            json_data = {u'category': u'category', u'tags': existing_tags, u"summary": u"this is a summary",
                         u'title': u'a title', u'body': u'body text', u'timestamp': datetimeformat(datetime.now())
                    .decode("utf-8"),
                         u'updated': datetimeformat(datetime.now()).decode("utf-8"),
                         u"answers":[], u'images':images}

            response = self.client.post(url_for('main'), content_type='application/json',
                             data=json.dumps(json_data))

            json_data[u"id"] = u'4'
            json_data[u'images'] = [{u'blob_key': u'encoded_gs_file:YXBwX2RlZmF1bHRfYnVja2V0LzIwMTlfMV80XzE2ei5naWY=',
                                      u'filename': TEST_IMAGE}, {u'blob_key': u'encoded_gs_file:YXBwX2RlZmF1bHRfYnVja2V0LzEyXzNfNF8zXzEyei5wbmc=',
                                                     u'filename': TEST_IMAGE2}]
            self.assertDictEqual(json_data, response.json)

    def test_no_post(self):

        response = self.client.get(url_for('main'))

        self.assertFalse(response.json)

    def test_edit_post_add_answers(self):
        post, _, _ = self.create_post()

        editing_tags = ["a new tag", "tag to added"]
        json_data = {u'category': u'a new category', 'tags': editing_tags, 'title': 'a new title', 'body': 'body text',
                     u'summary': u'this is a new summary',
                     'answers': [{u"p_answer": u"ans1", "is_correct": True}, {u"p_answer": u"ans2", "is_correct": False}]}

        response = self.client.put(url_for('edit_post', id=post.key.id()), content_type='application/json',
                                   data=json.dumps(json_data))

        data = {u"title": u'a new title', u"body": post.body, u"category":
            u"a new category", u"id": str(post.key.id()).decode('utf8'), \
                u"tags": post.get_tag_names(),
                u'summary': u'this is a new summary',
                u"timestamp": post.timestamp.strftime(DATEFORMAT).decode('utf8')
            , u"updated": post.updated.strftime(DATEFORMAT).decode('utf8'),
                u"answers": [{u"p_answer": u"ans1", u"is_correct": True,
                              u'statistics': 0.0, u'nof_times_selected': 0},
                             {u"p_answer": u"ans2", u"is_correct": False,
                              u'statistics': 0.0, u'nof_times_selected': 0}], u'images': []}

        self.assertDictEqual(data, response.json)

    def test_edit_post(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]
        editing_tags = ["a new tag", "tag to added"]  # final tags are "a new tag", "tag to added"

        existing_tag_keys = self.tags.add(existing_tags)

        post_key = self.posts.add("a title", "body text", category_key, existing_tag_keys, "this is a summary")

        self.posts.add("a title 2", "body text 2", category_key, existing_tag_keys, "this is a summary 2")

        updating_post = post_key.get()

        json_data = {u'category': u'a new category', 'tags': editing_tags, 'title': 'a new title', 'body': 'body text',
                     u'summary': u'this is a new summary',
                     'answers':[]}

        response = self.client.put(url_for('edit_post', id=post_key.id()), content_type='application/json',
                                   data=json.dumps(json_data))

        tag_names = [u"a new tag", u"a new new tag", u"tag to added"]
        post_tag_names = [u"a new tag", u"tag to added"]

        data = {u"title": u'a new title', u"body": updating_post.body, u"category":
                 u"a new category", u"id": str(updating_post.key.id()).decode('utf8'), \
                 u"tags": post_tag_names,
                u'summary': u'this is a new summary',
                 u"timestamp": updating_post.timestamp.strftime(DATEFORMAT).decode('utf8')
                    , u"updated":
                     updating_post.updated.strftime(DATEFORMAT).decode('utf8'),
                 u"answers":updating_post.answers,u'images':[],
                 }

        self.assertDictEqual(data, response.json)

    def test_edit_a_post_view(self):

        category_key = self.categories.add("category")

        existing_tags = ["a new tag", "a new new tag"]

        existing_tag_keys = self.tags.add(existing_tags)

        post_key = self.posts.add("a title", "body text", category_key, existing_tag_keys, "this is a summary")

        response = self.client.get(url_for('edit_a_post_view', postkey=post_key))

        flash(MSG)

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

        flash(MSG)
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

        flash(MSG)

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

        flash(MSG)
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

    def test_view_filtered_posts_by_category(self):

         category_key = self.categories.add("a category")
         existing_tags = ["a new tag", "a new new tag"]
         existing_tag_keys = self.tags.add(existing_tags)

         self.posts.add("about", "body text", category_key, existing_tag_keys)

         second_tags = ["a new second tag", "a new new second tag"]
         second_tag_keys = self.tags.add(second_tags)

         self.posts.add("about second post", "body secod text", category_key, second_tag_keys)

         self.posts.filter_by_category('a category')

         passed_days, remaining_days = calculate_work_date_stats()
         site_updated = self.posts.site_last_updated()

         flash(MSG)

         rendered_template = render_template("posts.html", user_status=users.is_current_user_admin(),
                                             siteupdated=site_updated, \
                                             daysleft=remaining_days, dayspassed=passed_days,
                                             tags=self.tags, categories=self.categories,
                                             posts=self.posts.to_json(),
                                             codeversion=CODEVERSION, form=self.form)

         response = self.client.get(path='/categories/a category')

         return self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    def test_404_not_found_page(self):
        response = self.client.get(path='/a path not existing')
        flash(MSG)
        rendered_template = render_template('404.html')

        return self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    def test_500_error_page(self):
        json_data = {u'category': u'a new category', 'tags': '', 'title': 'a new title', 'body': 'body text',
                     u'summary': u'this is a new summary',
                     'answers': []}

        response = self.client.put(url_for('edit_post', id='34'), content_type='application/json',
                                   data=json.dumps(json_data))
        accept_google_analytics()
        rendered_template = render_template('500.html')

        return self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

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

    def test_api_answers_post_method(self):
        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary",
                       [{"p_answer":"ans1", "is_correct":True},{"p_answer":"ans2","is_correct":False}])


        json_data_f = {"p_answer":"ans2","is_correct":"True"}

        response = self.client.post(url_for('answers', title="a title"), content_type='application/json',
                                    data=json.dumps(json_data_f))#, headers={"csrf_token":csrf_token})

        self.assertDictEqual({u'msg': u'Sorry, no attempts left!', u'result': False,
                              u'remaining_attempts': 0,u'alert_type':u'warning',
                              u'answers_stats':{}}, response.json)

        json_data_f = {"p_answer": "ans2", "is_correct": "True"}
        response = self.client.post(url_for('answers', title="a title"), content_type='application/json',
                                    data=json.dumps(json_data_f))

        self.assertDictEqual({u'msg': u'Sorry, no attempts left!',u'alert_type':u'warning', u'result': False,
                              u'remaining_attempts':-1,
                              u'answers_stats': {}
                              }, response.json)

    def test_api_answers_post_method_correct_guess(self):
        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary",
                       [{"p_answer": "ans1", "is_correct": True}, {"p_answer": "ans2", "is_correct": False}])

        json_data_f = {"p_answer": "ans1", "is_correct": "True"}

        response = self.client.post(url_for('answers', title="a title"), content_type='application/json',
                                    data=json.dumps(json_data_f))  # , headers={"csrf_token":csrf_token})

        self.assertDictEqual({u'msg': u'Great!', u'result': True,
                              u'remaining_attempts': 0, u'alert_type': u'success',
                              u'answers_stats': {u'Answer': u'Selection', u'ans1': 1, u'ans2': 0}}, response.json)

    def test_is_cookie_set(self):
        with app.test_client() as c:
            c.post(url_for('ga_accept'), follow_redirects=True)

            c_value = request.cookies.get('ga_accepted')

            self.assertEqual(c_value,  'True')

    def test_is_cookie_set_false(self):
        with app.test_client() as c:
            c.post(url_for('ga_decline'), follow_redirects=True)

            c_value = request.cookies.get('ga_accepted')

            self.assertEqual(c_value, 'False')

    def test_accept_google_analytics(self):
        with app.test_client() as c:
            c.post(url_for('ga_accept'), follow_redirects=True)
            accept_google_analytics()
            self.assertTrue(app.jinja_env.globals['ga_accepted'])

        with app.test_client() as c:
            c.post(url_for('ga_decline'), follow_redirects=True)
            accept_google_analytics()
            self.assertFalse(app.jinja_env.globals['ga_accepted'])

    def test_questions_view(self):
        category_key = self.categories.add("reconstructing a test")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary",
                       [{"p_answer": "ans1", "is_correct": True}, {"p_answer": "ans2", "is_correct": False}])

        category_key = self.categories.add("reconstructing a test")
        test_tags = ["a tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title here", "body to test the question text",
                       category_key, new_tag_keys, "this is a summary",
                       [{"p_answer": "a test answ correct", "is_correct": True},
                        {"p_answer": "a wrong tet answer", "is_correct": False}])

        response = self.client.get(path="/questions/reconstructing a test")

        self.posts.filter_by_category("reconstructing a test")

        flash(MSG)
        passed_days, remaining_days = calculate_work_date_stats()
        site_updated = self.posts.site_last_updated()
        self.posts.to_answers_form()

        rendered_template = render_template("questions.html", user_status=users.is_current_user_admin(),
                                            siteupdated=site_updated, \
                                            daysleft=remaining_days, dayspassed=passed_days,
                                            tags=self.tags, categories=self.categories,
                                            posts=self.posts,
                                            codeversion=CODEVERSION)


        self.assertEqualHTML(rendered_template.decode('utf8'), response.data.decode('utf8'))

    def test_redirect_nonwww(self):
        app.config['SERVER_NAME'] = "arsakian.com"
        with app.test_request_context():

            with app.test_client() as c:
                response = c.get(url_for('index', _external=True))
                self.assertEqual(response.location, "http://www.arsakian.com/")

                response = c.get(url_for('archives', _external=True))
                self.assertEqual(response.location, "http://www.arsakian.com/archives")
        app.config['SERVER_NAME'] = None

    def test_send_image_file(self):

        with open(os.path.join(TEST_IMAGE)) as f:
            img_stringIO = StringIO.StringIO(f.read())  # in memory read

        post, _, _ = self.create_post()
        image_key = post.add_blob(img_stringIO.read(), TEST_IMAGE)

        response = self.client.get(path='/images/{}'.format(TEST_IMAGE),
                                      content_type='multipart/form-data',
                                      follow_redirects=True)

        with open(os.path.join(TEST_IMAGE)) as f:

            self.assertEqual(f.read(), response.data)

        # with app.test_client() as c:
        #     accept_google_analytics()
        #
        #     self.assertRaises(cloudstorage.NotFoundError, c.get(path='/images/{}'.format("non existent"),
        #                           content_type='multipart/form-data',
        #                           follow_redirects=True))


    # def test_upload(self):
    #     output = StringIO()
    #     output.write('hello there')
    #
    #     response = self.client.post(url_for('upload'), buffered=True,
    #                        content_type='multipart/form-data',
    #                                 data={'file_field': (output, 'hello there')})
    #
    #
    #     self.assertEqual('ok',response.data)
