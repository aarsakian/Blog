import os

from datetime import datetime

from google.appengine.ext import testbed

from google.appengine.ext import ndb

from freezegun import freeze_time
from werkzeug.contrib.atom import AtomFeed

from blog.models import Tags, Posts, Categories, BlogPost, Answer, ViewImageHandler
from blog.utils import find_modified_tags, find_tags_to_be_added, find_tags_to_be_removed, datetimeformat, \
    make_external
from blog.errors import InvalidUsage

from blog.search import query_search_index, find_posts_from_index

from . import BlogTestBase

TEST_IMAGE = '2019_1_4_16z.gif'


class TestModels(BlogTestBase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        # enable memcache
        self.testbed.init_memcache_stub()

        self.testbed.init_user_stub()

        self.testbed.init_blobstore_stub()

        self.testbed.init_app_identity_stub()

        self.testbed.init_urlfetch_stub()

        self.testbed.init_search_stub(enable=True)
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

        self.tags = Tags()
        self.categories = Categories()
        self.posts = Posts()

    def create_answers(self, answers):
        answers_keys = [Answer(p_answer=ans,
                               is_correct=is_correct)
                        for ans, is_correct in answers.items()]
        return answers_keys

    def create_post_with_answers(self, answers, category="a category"):

        test_tags = ["a new tag", "a new new tag"]
        tag_keys = self.tags.add(test_tags)
        answers_keys = self.create_answers(answers)

        category_key = self.categories.add(category)
        summary = "a summmary"
        title = "a title"
        body = "here is a body"

        post_key = BlogPost(title=title,
                            body=body,
                            category=category_key,
                            tags=tag_keys,
                            summary=summary,
                            answers=answers_keys).put()

        return post_key.get(), category_key, tag_keys, answers_keys

    def test_add_a_tag(self):
        tag_keys = self.tags.add(["a new tag"])
        self.assertEqual("a new tag", tag_keys[0].get().tag)

    def test_add_a_tag_once(self):
        self.tags.add(["a new tag"])
        tags_keys = self.tags.add(["a new tag", "a really new tag"])

        self.assertEqual(len(self.tags), 2)
        self.assertEqual(  self.tags.get_keys(["a new tag", "a really new tag"]), tags_keys)


    def test_add_tags(self):
        tag_keys = self.tags.add(["a new tag", "a second new tag"])
        self.assertItemsEqual(["a new tag", "a second new tag"],
                              [tag_keys[0].get().tag, tag_keys[1].get().tag])

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
        self.assertEqual("category", category_key.get().category)

    def test_add_a_category_once(self):
        category_key = self.categories.add("category")
        self.assertEqual("category", category_key.get().category)
        self.categories.add("category")
        self.assertEqual(len(self.categories), 1)

    def test_delete_a_category(self):
        category_key = self.categories.add("category")
        self.categories.delete(category_key)
        self.assertItemsEqual([], self.categories)

    def test_get_key_of_a_category(self):
        self.assertEqual(self.categories.add("category"), self.categories.get_key("category"))

    def test_add_a_post(self):

        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

        self.assertEqual("a title", post_key.get().title)
        self.assertEqual("body text", post_key.get().body)
        self.assertEqual("this is a summary", post_key.get().summary)
        self.assertEqual(category_key, post_key.get().category)
        self.assertItemsEqual(new_tag_keys, post_key.get().tags)

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
        test_tags2 = ["a new tag 1", "a new new tag"]

        new_tag_keys1 = self.tags.add(test_tags1)
        new_tag_keys2 = self.tags.add(test_tags2)

        post_key1 = self.posts.add("a title", "body text", category_key, new_tag_keys1)
        self.posts.add("a title 2", "body text 2", category_key, new_tag_keys2)

        self.assertItemsEqual(test_tags2 , self.posts.get_other_tags(post_key1.id()))

    def test_find_modified_tags(self):
        test_existing_tags = ["a new tag", "a new new tag"]
        editing_tags1 = ["a new tag 1", "a new new tag 2"]
        editing_tags2 = ["a new tag 1", "a new tag"]

        modified_tags = find_modified_tags(editing_tags1, test_existing_tags)
        self.assertItemsEqual(modified_tags,  editing_tags1)

        modified_tags = find_modified_tags(editing_tags2, test_existing_tags)
        self.assertItemsEqual(modified_tags,  ["a new tag 1"])

    def test_find_tags_to_be_deleted(self):
        category_key = self.categories.add("category")

        other_tags = ["a new tag 3", "a new new tag"]
        test_existing_tags = ["a new tag", "a new new tag"]
        editing_tags1 = ["a new tag 1", "a new new tag 2"]
        editing_tags2 = ["a new tag 1", "a new tag"]

        # scenario to delete tags "a new tag",
        non_modified_tags = set(editing_tags1) & set(test_existing_tags)

        tags_to_be_removed = find_tags_to_be_removed(test_existing_tags, non_modified_tags, other_tags)
        self.assertItemsEqual(tags_to_be_removed, ["a new tag"])

        # scenario to delete all tags
        non_modified_tags = set(editing_tags1) & set(test_existing_tags)
        tags_to_be_removed = find_tags_to_be_removed(test_existing_tags, non_modified_tags, [])
        self.assertItemsEqual(tags_to_be_removed, test_existing_tags)
        # scenario not to delete any tag
        tags_to_be_removed = find_tags_to_be_removed(test_existing_tags, [], test_existing_tags)
        self.assertItemsEqual(tags_to_be_removed, [])

    def test_find_tags_to_be_added_from_an_edited_post(self):
        category_key = self.categories.add("category")

        test_existing_tags = ["a new tag", "a new new tag"]
        editing_tags1 = ["a new tag 1", "a new new tag 2"]
        editing_tags2 = ["a new tag 1", "a new tag"]

        tag_keys = self.tags.add(test_existing_tags)

        self.posts.add("a title", "body text", category_key, tag_keys)

        # scenario to add all tags "a new tag", "a new new tag"
        tags_to_be_added = find_modified_tags(editing_tags1, test_existing_tags)
        self.assertItemsEqual(tags_to_be_added,  editing_tags1)

        # scenario to add one tag "a new tag 1"
        tags_to_be_added = find_modified_tags(editing_tags2, test_existing_tags)
        self.assertItemsEqual(tags_to_be_added, ["a new tag 1"])

        # scenario not to delete any tag
        tags_to_be_added= find_modified_tags(test_existing_tags, test_existing_tags)
        self.assertItemsEqual(tags_to_be_added, [])

    def test_edit_post(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        post = post_key.get()
        post.edit("a modified title", "a modified body text", datetime.now(), new_tag_keys, category_key)

        self.assertEqual("a modified title", post_key.get().title)
        self.assertEqual("a modified body text", post_key.get().body)
        self.assertEqual(category_key, post_key.get().category)
        self.assertItemsEqual(new_tag_keys, post_key.get().tags)

    def test_get_answers(self):
        post, _, _, _ = self.create_post_with_answers({"ans1": True, "ans2": False, "ans3": False})

        self.assertItemsEqual(post.get_answers(), [{u'is_correct': True, u'p_answer': u'ans1'},
                                                 {u'is_correct': False, u'p_answer': u'ans2'},
                                                 {u'is_correct': False, u'p_answer': u'ans3'}])

    def test_edit_post_answers(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post, _, _, _ = self.create_post_with_answers({"ans1": True, "ans2": False, "ans3": False})
        post.edit("a modified title", "a modified body text", datetime.now(), new_tag_keys, category_key,"",
                  raw_answers=[{u'is_correct': True, u'p_answer': u'ans1'},
                                                 {u'is_correct': True, u'p_answer': u'ans2_mod'},
                                                 {u'is_correct': False, u'p_answer': u'ans3'}])

        self.assertItemsEqual(post.get_answers(),[{u'is_correct': True, u'p_answer': u'ans1'},
                                                 {u'is_correct': True, u'p_answer': u'ans2_mod'},
                                                 {u'is_correct': False, u'p_answer': u'ans3'}])

    def test_statistics_when_editing_a_post(self):
        post, category_key, tags_key, _ = self.create_post_with_answers({"ans1": True, "ans2": False, "ans3": False})
        post.set_selected_answer("ans1")
        post.set_selected_answer("ans1")

        self.assertEqual(post.get_answers_statistics(),
                         {"Answer": "Selection", u"ans1": 2, u"ans2": 0, u"ans3": 0})
        post.edit("a modified title", "a modified body text", datetime.now(), tags_key,
                   category_key, "",raw_answers=[{u'is_correct': True, u'p_answer': u'ans1'},
                                                 {u'is_correct': True, u'p_answer': u'ans2_mod'},
                                                 {u'is_correct': False, u'p_answer': u'ans3'}])

        self.assertEqual(post.get_answers_statistics(), {"Answer": "Selection", u"ans1": 2, u"ans2_mod": 0, u"ans3": 0})

    def test_delete_post(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        self.posts.delete(post_key)
        self.assertItemsEqual(self.posts, [])

    def test_find_tags_to_be_added(self):


        test_existing_tags = ["a new tag", "a new new tag"]
        editing_tags = ["a new tag 1", "a new new tag 2"]
        editing_tags2 = ["a new tag", "a new new tag 2"]

        non_modified_tags = set(editing_tags) & set(test_existing_tags)
        tags_to_be_added = find_tags_to_be_added(editing_tags, non_modified_tags, test_existing_tags)

        # scenario to add all tags "a new tag 1", "a new new tag 2"
        self.assertItemsEqual(editing_tags, tags_to_be_added)

        # scenario to add one tag "a new new tag 2"
        non_modified_tags = set(editing_tags2) & set(test_existing_tags)
        tags_to_be_added = find_tags_to_be_added(editing_tags2, non_modified_tags, test_existing_tags)

        self.assertItemsEqual(["a new new tag 2"], tags_to_be_added)

    def test_to_json_of_posts(self):
        category_key1 = self.categories.add("category 1")
        category_key2 = self.categories.add("category 2")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key2 = self.posts.add("a new title", "new body text", category_key2, new_tag_keys, "a summary  2")
        post_key1 = self.posts.add("a title", "body text", category_key1, new_tag_keys, "a summary")

        post2 = post_key2.get()

        with open(os.path.join(TEST_IMAGE)) as f:
            self.assertTrue(post2.add_blob(f.read(), TEST_IMAGE))

        json_result = [{u'body':  post_key1.get().body, u'category': post_key1.get().category.get().category
                           , u'updated':
                        datetimeformat(post_key1.get().updated), u'tags':
                        [(post_key1.get().tags[0].get()).tag,  (post_key1.get().tags[1].get()).tag],
                        u'timestamp':  datetimeformat(post_key1.get().timestamp),
                        u'title':  post_key1.get().title, u'id': str(post_key1.get().key.id()),
                        u'summary':post_key1.get().summary,
                        u'answers':post_key1.get().answers,
                        u'image': 'None'
                        },
                        {u'body':  post_key2.get().body, u'category': post_key2.get().category.get().category
                            , u'updated':
                        datetimeformat(post_key2.get().updated), u'tags':
                        [(post_key2.get().tags[0].get()).tag,  (post_key2.get().tags[1].get()).tag],
                        u'timestamp':  datetimeformat(post_key2.get().timestamp),
                        u'title':  post_key2.get().title, u'id': str(post_key2.get().key.id()),
                        u'summary':post_key2.get().summary,
                        u'answers': post_key2.get().answers,u'image':
                             'encoded_gs_file:YXBwX2RlZmF1bHRfYnVja2V0LzIwMTlfMV80XzE2ei5naWY='
                         }]

        self.assertEqual(json_result, self.posts.to_json())

    def test_retrieve_from_memcache(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        id = post_key.id()

        memcached_post = BlogPost.get(id)  # requested a post added to MEMCACHE

        self.assertEqual(memcached_post.key, post_key)

    def test_get_by_title(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)
        post = self.posts.get_by_title("a title")
        self.assertEqual(post_key, post.key)

    def test_get_by_title_assert_raises(self):
        category_key = self.categories.add("category")

        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)

        self.posts.add("a title", "body text", category_key, new_tag_keys)
        # test exception
        with self.assertRaises(InvalidUsage):
            self.posts.get_by_title("a non existent title")

    def test_get_names_from_tags(self):
        test_tags = ["a new tag", "a new new tag"]
        self.tags.add(test_tags)

        self.assertItemsEqual(test_tags, self.tags.get_names())

    def test_to_json_of_a_tag(self):
        test_tags = ["a new tag", "a new new tag"]
        tag_key1, tag_key2 = self.tags.add(test_tags)
        tag = tag_key1.get()

        test_dict = {"id":str(tag_key1.id()), "tag":u"a new tag"}

        self.assertDictEqual(test_dict, tag.to_json())

    def test_to_json_of_tags(self):
        test_tags = [u"a new tag", u"a new new tag"]
        tag_key1, tag_key2 = self.tags.add(test_tags)

        json_data = [{"id":key,"tag":val} for key, val in zip([str(tag_key1.id()), str(tag_key2.id())], test_tags)]

        self.assertListEqual(json_data, self.tags.to_json())

    def test_get_a_post(self):
        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        #test with no memcache
        post = BlogPost.get(post_key.id())
        self.assertEqual(post.key, post_key)

        #test memcached
        post = BlogPost.get(post_key.id())
        self.assertEqual(post.key, post_key)

    # def test_filter_posts_by_a_tag(self):
    #     category_key = self.categories.add("category")
    #     test_tags = ["a new tag", "a new new tag"]
    #     new_test_tags = ["a second tag", "a new second tag"]
    #     new_tag_keys = self.tags.add(test_tags)
    #     new_test_tag_keys = self.tags.add(new_test_tags)
    #     post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)
    #     self.posts.add("a title", "a second body text", category_key, new_test_tag_keys )
    #     print self.posts
    #     self.posts.filter_by_tag("a new tag")
    #     print self.posts, post_key.get()
    #     self.assertItemsEqual(self.posts, [post_key.get()])


    # def test_filter_posts_by_category(self):
    #
    #     post1, _, _, _ = self.create_post_with_answers({"ans1": True, "ans2": False}, category="cat 1")
    #     post2, _, _, _ = self.create_post_with_answers({"ans1": True, "ans2": False}, category="cat 2")
    #
    #     self.posts.filter_by_category("cat 1")
    #     print self.posts[0], post2
    #     self.assertItemsEqual(self.posts, [post2])
    #
    #     self.posts.filter_by_category("cat 1")
    #
    #     self.assertItemsEqual(self.posts, [post1])
    #
    #     self.posts.filter_by_category("wrong cat")
    #
    #     self.assertItemsEqual(self.posts, [])

    def test_get_category(self):
        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        post = BlogPost.get(post_key.id())

        self.assertEqual("category", post.get_category())

    def test_get_tagnames(self):
        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        post = BlogPost.get(post_key.id())

        tag_names = post.get_tag_names()

        self.assertItemsEqual(test_tags, tag_names)

    def test_posts_contains_a_post(self):
        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)

        self.assertTrue(post_key in self.posts)

        self.assertFalse("no key" in self.posts)

    def test_tags_contains_a_tag(self):
        test_tags = ["a new tag", "a new new tag"]
        self.tags.add(test_tags)

        self.assertTrue(test_tags[0] in self.tags)

        self.assertFalse("dfsd" in self.tags)

    def test_categories_contains_a_category(self):
        self.categories.add("category")

        self.assertTrue("category" in self.categories)

        self.assertFalse("" in self.categories)

    # def test_filter_matched(self):
    #     category_key = self.categories.add("category")
    #     test_tags = ["a new tag", "a new new tag"]
    #     new_tag_keys = self.tags.add(test_tags)
    #     post_key = self.posts.add("a title", "body text", category_key, new_tag_keys)
    #     self.posts.add("a title", "body sec2 text", category_key, new_tag_keys)
    #     print self.posts
    #     self.posts.filter_matched([post_key.id()])
    #     self.assertItemsEqual(self.posts, [post_key.get()])

    def test_site_last_updated(self):
        freezer = freeze_time("2017-11-29 17:48:18")
        freezer.start()
        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        self.posts.add("a title", "body text", category_key, new_tag_keys)
        self.posts.add("a title", "body sec2 text", category_key, new_tag_keys)

        last_updated = self.posts.site_last_updated()
        self.assertEqual("Wednesday 29 November 2017", last_updated)
        freezer.stop()

    def test_get_related_posts(self):
        category_key = self.categories.add("category")
        test_tags = ["a new tag", "a new new tag"]
        new_tag_keys = self.tags.add(test_tags)
        current_post = self.posts.add("a title", "body text", category_key, new_tag_keys)

        rel_test_tags = ["a new tag", "a different tag"]
        rel_tag_keys = self.tags.add(rel_test_tags )
        rel_post_key = self.posts.add("a different title", "body sec2 text", category_key, rel_tag_keys)
        rel_post = BlogPost.get(rel_post_key.id())

        related_posts = self.posts.get_related_posts(current_post.id())

        self.assertListEqual([rel_post], related_posts)

    def test_update_category(self):
        category_key = self.categories.add("category")

        self.categories.update("a modified category", category_key)
        category = self.categories.get(category_key)

        self.assertEqual("a modified category", category.category)

    def test_update_category_without_key(self):
        category_key = self.categories.update("a modified category")
        category = self.categories.get(category_key)

        self.assertEqual("a modified category", category.category)

    def test_update_tags_without_post(self):
        test_tags = ["a new tag", "a new new tag"]
        tag_keys = self.tags.add(test_tags)

        category_key = self.categories.add("category")
        self.posts.add("a title", "body text", category_key, tag_keys)

        test_new_tags = ["a new different tag", "a new new tag"]
        self.tags.update(test_new_tags)
        tag_names = self.tags.get_names()

        self.assertListEqual(tag_names, [u"a new tag",  u"a new new tag", u"a new different tag"])

    def test_update_tags(self):
        """
        replacing a new tag with a new different tag
        :return:
        """
        test_tags = ["a new tag", "a new new tag"]
        tag_keys = self.tags.add(test_tags)

        category_key = self.categories.add("category")
        post_key = self.posts.add("a title", "body text", category_key, tag_keys)

        test_new_tags = ["a new different tag", "a new new tag"]
        self.tags.update(test_new_tags, BlogPost.get(post_key.id()))
        tag_names = self.tags.get_names()

        self.assertListEqual(tag_names, [ u"a new new tag", u"a new different tag"])

    def test_rebuild_index(self):
        test_tags = ["a new tag", "a new new tag"]
        tag_keys = self.tags.add(test_tags)

        category_key = self.categories.add("category")
        post_key = self.posts.add("a title", "body text", category_key, tag_keys)

        self.posts.rebuild_index()

        results = query_search_index("body")
        posts_ids = find_posts_from_index(results)

        self.assertEqual(post_key.id(), posts_ids[0])

    def test_add_to_feed(self):
        test_tags = ["a new tag", "a new new tag"]
        tag_keys = self.tags.add(test_tags)

        category_key = self.categories.add("category")
        self.posts.add("a title", "body text", category_key, tag_keys)

        feed_org = AtomFeed('Recent Articles',
                        feed_url='http://localhost/recent.atom', url="")

        feed_model = AtomFeed('Recent Articles',
                            feed_url='http://localhost/recent.atom', url="")

        for post in self.posts:
            catname = post.get_category()
            url = "/".join([catname,
                            post.timestamp.strftime('%B'),
                            post.timestamp.strftime('%Y')])
            feed_org.add(post.title, post.body,
                     content_type='html',
                     author='Armen Arsakian',
                     url=make_external("http://localhost/recent.atom", url),
                     updated=post.updated,
                     published=post.timestamp)



        feed = self.posts.add_to_feed(feed_model, "http://localhost/recent.atom")

        self.assertEqual(feed_org.to_string(), feed.to_string())

    def test_stripped_answers(self):
        test_tags = ["a new tag", "a new new tag"]
        tag_keys = self.tags.add(test_tags)

        ans1 = Answer(p_answer="ans1",
               is_correct=True)

        ans2 = Answer(p_answer="ans2",
                      is_correct=False)

        category_key = self.categories.add("category")
        summary =  "a summmary"
        title = "a title"
        body = "here is a body"

        post_key = BlogPost(title=title,
                            body=body,
                            category=category_key,
                            tags=tag_keys,
                            summary=summary,
                            answers=[ans1, ans2]).put()

        post = post_key.get()
        jsoned_answers = [{"p_answer": "ans1", "is_correct": False},
         {"p_answer": "ans2", "is_correct": False}]

        self.assertItemsEqual(post.strip_answers_jsoned(), jsoned_answers)

    def test_selected_answer_setter(self):
        post, _, _, _ = self.create_post_with_answers({"ans1":True, "ans2":False})
        ans1 = Answer(p_answer="ans1",
                      is_correct=True)

        post.set_selected_answer("ans1")

        self.assertEqual(Answer(is_correct=True, nof_times_selected=1, p_answer=u'ans1', statistics=1.0),
                         post.selected_answer)


    def test_is_answer_correct(self):
        post, _, _, _ = self.create_post_with_answers({"ans1":True, "ans2":False})
        post.set_selected_answer("ans1")

        self.assertTrue(post.is_answer_correct())

        post.set_selected_answer('ans2')
        self.assertFalse(post.is_answer_correct())

        post.set_selected_answer('non existent')
        self.assertFalse(post.is_answer_correct())

    def test_to_answer_form(self):
        post, _, _, _ = self.create_post_with_answers({"ans1":True, "ans2":False})
        self.posts.to_answers_form()

        self.assertItemsEqual([(u'ans1', u'ans1'), (u'ans2', u'ans2')], post.answers_form.r_answers.choices)


    def test_update_answers_statistics(self):
        post, _, _, _ = self.create_post_with_answers({"ans1":True, "ans2":False})

        post.set_selected_answer("ans1")

        self.assertTupleEqual((post.answers[0].statistics, post.answers[1].statistics), (1.0, 0.0))
        self.assertTupleEqual((post.answers[0].nof_times_selected, post.answers[1].nof_times_selected), (1, 0))

        post.set_selected_answer("ans2")

        self.assertTupleEqual((post.answers[0].statistics, post.answers[1].statistics), (0.5, 0.5))
        self.assertTupleEqual((post.answers[0].nof_times_selected, post.answers[1].nof_times_selected), (1, 1))

        post.set_selected_answer("ans2")

        self.assertAlmostEqual(post.answers[0].statistics, 0.3333, places=4)
        self.assertAlmostEqual(post.answers[1].statistics, 0.6666666666666666, places=4)
        self.assertTupleEqual((post.answers[0].nof_times_selected, post.answers[1].nof_times_selected), (1, 2))

    def test_get_answers_statistics(self):
        post, _, _, _ = self.create_post_with_answers({"ans1": True, "ans2": False, "ans3": False})
        post.set_selected_answer("ans1")

        answers_stats = post.get_answers_statistics()

        self.assertDictEqual(answers_stats, {"Answer":"Selection","ans1": 1, "ans2": 0, "ans3":0})

        post.set_selected_answer("ans2")

        answers_stats = post.get_answers_statistics()

        self.assertDictEqual(answers_stats, {"Answer":"Selection","ans1": 1,"ans2": 1,"ans3":0})

        answers_stats = post.get_answers_statistics()
        self.assertDictEqual(answers_stats, {"Answer": "Selection", u"ans1": 1, u"ans2": 1, u"ans3": 0})

    def test_add_blob(self):
        post, _, _ = self.create_post()

        with open(os.path.join(TEST_IMAGE)) as f:
            image_key = post.add_blob(f.read(), TEST_IMAGE)
            self.assertEqual(image_key, u'encoded_gs_file:YXBwX2RlZmF1bHRfYnVja2V0LzIwMTlfMV80XzE2ei5naWY=')

    def test_delete_blob(self):
        from google.appengine.ext import blobstore
        post, _, _ = self.create_post()

        with open(os.path.join(TEST_IMAGE)) as f:
            image_key = post.add_blob(f.read(), TEST_IMAGE)

        post.delete_blob(post.image_blob_key)
        with self.assertRaises(blobstore.BlobNotFoundError):
            blobstore.fetch_data(image_key, 0, 1)
