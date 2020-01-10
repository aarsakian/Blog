from blog import app

from datetime import datetime

from freezegun import freeze_time
from werkzeug.contrib.atom import AtomFeed

from blog.models import Tags, Posts, Categories, BlogPost, Answer, ViewImageHandler

from blog.utils import find_modified_tags, find_tags_to_be_removed, datetimeformat, \
     make_external

import pytest
from blog.errors import InvalidUsage
#
# from blog.search import query_search_index, find_posts_from_index
#
# from . import BlogTestBase

TEST_IMAGE = '2019_1_4_16z.gif'
TEST_IMAGE2 = u'12_3_4_3_12z.png'


def test_add_a_tag(tags, dispose_of):
    tag_keys = tags.add(["a new tag"])
    assert "a new tag" == tag_keys[0].get().tag
    dispose_of(tag_keys)


def test_add_a_tag_once(tags, dispose_of):
    tags.add(["a new tag"])
    tags_keys = tags.add(["a new tag", "a really new tag"])

    assert len(tags) == 2
    assert tags.get_keys(["a new tag", "a really new tag"]), tags_keys
    dispose_of(tags_keys)


def test_add_tags(tags, dispose_of):
    tag_keys = tags.add(["a new tag", "a second new tag"])
    assert ["a new tag", "a second new tag"] == \
           [tag_keys[0].get().tag, tag_keys[1].get().tag]
    dispose_of(tag_keys)


def test_delete_a_tag(tags):
    tags.add(["a new tag"])
    tags.delete("a new tag")
    assert [] == tags


def test_delete_tags(tags):
    tags.add(["a new tag", "a second new tag"])
    tags.delete(["a new tag", "a second new tag"])
    assert [] == tags


def test_get_keys_of_tags(tags, dispose_of):
    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)
    assert new_tag_keys == tags.get_keys(test_tags)
    dispose_of(new_tag_keys )


def test_add_a_category(categories, dispose_of):
    category_key = categories.add("category")
    assert "category" == category_key.get().category
    dispose_of([category_key])


def test_add_a_category_once(categories, dispose_of):
    category_key = categories.add("category")
    assert "category" == category_key.get().category
    categories.add("category")
    assert len(categories) == 1
    dispose_of([category_key])


def test_delete_a_category(categories):
    category_key = categories.add("category")
    categories.delete(category_key)
    assert [] == categories


def test_get_key_of_a_category(categories, dispose_of):
    assert categories.add("category") == categories.get_key("category")
    dispose_of([categories.get_key("category")])


def test_add_a_post(categories, tags, posts, dispose_of):

    category_key = categories.add("category")

    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)

    post_key = posts.add("a title", "body text", category_key, new_tag_keys, "this is a summary")

    assert "a title" == post_key.get().title
    assert "body text" == post_key.get().body
    assert "this is a summary" == post_key.get().summary
    assert category_key == post_key.get().category
    assert new_tag_keys == post_key.get().tags
    dispose_of([post_key])
    dispose_of([category_key])
    dispose_of(new_tag_keys)


def test_get_tags_from_posts(categories, tags, posts, dispose_of):
    category_key = categories.add("category")

    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)

    post_key = posts.add("a title", "body text", category_key, new_tag_keys)

    assert test_tags == posts.get_tags()

    dispose_of([post_key])
    dispose_of([category_key])
    dispose_of(new_tag_keys)


def test_get_empty_tags_from_posts(categories, tags, posts, dispose_of):
    category_key = categories.add("category")

    test_tags = []
    new_tag_keys = tags.add(test_tags)

    post_key = posts.add("a title", "body text", category_key, new_tag_keys)

    assert test_tags == posts.get_tags()

    dispose_of([post_key])
    dispose_of([category_key])
    dispose_of(new_tag_keys)


def test_get_tags_from_a_post(categories, tags, posts, dispose_of):
    category_key = categories.add("category")

    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)

    post_key = posts.add("a title", "body text", category_key, new_tag_keys)
    for post in posts:
        assert test_tags == post.get_tag_names()

    dispose_of([post_key])
    dispose_of([category_key])
    dispose_of(new_tag_keys)


def test_get_other_tags_from_a_post(categories, tags, posts, dispose_of):
    category_key = categories.add("category")

    test_tags1 = ["a new tag", "a new new tag"]
    test_tags2 = ["a new tag 1", "a new new tag"]

    new_tag_keys1 = tags.add(test_tags1)
    new_tag_keys2 = tags.add(test_tags2)

    post_key1 = posts.add("a title", "body text", category_key, new_tag_keys1)
    post_key2 = posts.add("a title 2", "body text 2", category_key, new_tag_keys2)

    assert set(test_tags2) == set(posts.get_other_tags(post_key1.id()))
    dispose_of([post_key1, post_key2])
    dispose_of([category_key])
    dispose_of(tags.get_keys())



def test_edit_post(categories, tags, posts, dispose_of):
    category_key = categories.add("category")

    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)

    post_key = posts.add("a title", "body text", category_key, new_tag_keys)

    post = post_key.get()
    post.edit("a modified title", "a modified body text", datetime.now(), new_tag_keys, category_key)

    assert "a modified title" == post_key.get().title
    assert "a modified body text" == post_key.get().body
    assert category_key == post_key.get().category
    assert new_tag_keys == post_key.get().tags

    dispose_of([post_key])
    dispose_of([category_key])
    dispose_of(new_tag_keys)


def test_get_answers(post_with_answers):
    post, _, _, _ = post_with_answers

    assert post.get_answers() == [{u'is_correct': True, u'p_answer': u'ans1'},
                                  {u'is_correct': False, u'p_answer': u'ans2'},
                                  {u'is_correct': False, u'p_answer': u'ans3'}]


def test_edit_post_answers(categories, tags, post_with_answers):
    category_key = categories.add("category")

    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)

    post, _, _, _ = post_with_answers
    post.edit("a modified title", "a modified body text", datetime.now(), new_tag_keys, category_key,"",
              raw_answers=[{u'is_correct': True, u'p_answer': u'ans1'},
                                             {u'is_correct': True, u'p_answer': u'ans2_mod'},
                                             {u'is_correct': False, u'p_answer': u'ans3'}])

    assert post.get_answers() == [{u'is_correct': True, u'p_answer': u'ans1'},
                                             {u'is_correct': True, u'p_answer': u'ans2_mod'},
                                             {u'is_correct': False, u'p_answer': u'ans3'}]


def test_statistics_when_editing_a_post(post_with_answers):
    post, category_key, tags_key, _ = post_with_answers
    post.set_selected_answer("ans1")
    post.set_selected_answer("ans1")

    assert post.get_answers_statistics() == \
           {"Answer": "Selection", u"ans1": 2, u"ans2": 0, u"ans3": 0}

    post.edit("a modified title", "a modified body text", datetime.now(), tags_key,
               category_key, "",raw_answers=[{u'is_correct': True, u'p_answer': u'ans1'},
                                             {u'is_correct': True, u'p_answer': u'ans2_mod'},
                                             {u'is_correct': False, u'p_answer': u'ans3'}])
    assert post.get_answers_statistics() == {"Answer": "Selection", u"ans1": 2, u"ans2_mod": 0, u"ans3": 0}


def test_delete_post(categories, tags, posts, dispose_of):
    category_key = categories.add("category")

    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)

    post_key = posts.add("a title", "body text", category_key, new_tag_keys)

    posts.delete(post_key)
    assert posts == []

    dispose_of([category_key])
    dispose_of(new_tag_keys)


# def test_to_json_of_posts(categories, tags, posts):
#     category_key1 = categories.add("category 1")
#     category_key2 = categories.add("category 2")
#
#     test_tags = ["a new tag", "a new new tag"]
#     new_tag_keys = tags.add(test_tags)
#
#     post_key2 = posts.add("a new title", "new body text", category_key2, new_tag_keys, "a summary  2")
#     post_key1 = posts.add("a title", "body text", category_key1, new_tag_keys, "a summary")
#
#     post2 = post_key2.get()
#
#     with open(os.path.join(TEST_IMAGE), "rb") as f:
#         assert post2.add_blob(f.read(), TEST_IMAGE, 'image/jpeg')
#
#     with open(os.path.join(TEST_IMAGE2), "rb") as f:
#         assert post2.add_blob(f.read(), TEST_IMAGE2, 'image/jpeg')
#
#     json_result = [{u'body':  post_key1.get().body, u'category': post_key1.get().category.get().category
#                        , u'updated':
#                     datetimeformat(post_key1.get().updated), u'tags':
#                     [{"key": str(new_tag_keys[0]), "val":new_tag_keys[0].get().tag},
#                      {"key": str(new_tag_keys[1]), "val":new_tag_keys[1].get().tag}],
#                     u'timestamp':  datetimeformat(post_key1.get().timestamp),
#                     u'title':  post_key1.get().title, u'id': str(post_key1.get().key.id()),
#                     u'summary':post_key1.get().summary,
#                     u'answers':post_key1.get().answers,
#                     u'images': []
#                     },
#                     {u'body':  post_key2.get().body, u'category': post_key2.get().category.get().category
#                         , u'updated':
#                     datetimeformat(post_key2.get().updated), u'tags':
#                     [{"key": str(new_tag_keys[0]), "val":new_tag_keys[0].get().tag},
#                      {"key": str(new_tag_keys[1]), "val":new_tag_keys[1].get().tag}],
#                     u'timestamp':  datetimeformat(post_key2.get().timestamp),
#                     u'title':  post_key2.get().title, u'id': str(post_key2.get().key.id()),
#                     u'summary':post_key2.get().summary,
#                     u'answers': post_key2.get().answers,u'images':[{u'blob_key': u'encoded_gs_file:YXBwX2RlZmF1bHRfYnVja2V0LzIwMTlfMV80XzE2ei5naWY=',
#                                   u'filename': TEST_IMAGE}, {u'blob_key': u'encoded_gs_file:YXBwX2RlZmF1bHRfYnVja2V0LzEyXzNfNF8zXzEyei5wbmc=',
#                                                  u'filename': TEST_IMAGE2}]}]
#     assert json_result == posts.to_json()

# def test_retrieve_from_memcache(self):
#     category_key = categories.add("category")
#
#     test_tags = ["a new tag", "a new new tag"]
#     new_tag_keys = tags.add(test_tags)
#
#     post_key = posts.add("a title", "body text", category_key, new_tag_keys)
#
#     id = post_key.id()
#
#     memcached_post = BlogPost.get(id)  # requested a post added to MEMCACHE
#
#     assert memcached_post.key, post_key)


def test_get_by_title(categories, tags, posts, dispose_of):
    category_key = categories.add("category")

    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)

    post_key = posts.add("a title", "body text", category_key, new_tag_keys)
    post = posts.get_by_title("a title")
    assert post_key == post.key

    dispose_of([post_key])
    dispose_of([category_key])
    dispose_of(new_tag_keys)


def test_get_by_title_assert_raises(categories, tags, posts, dispose_of):
    category_key = categories.add("category")

    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)

    post_key = posts.add("a title", "body text", category_key, new_tag_keys)
    # test exception
    with pytest.raises(InvalidUsage):
        posts.get_by_title("a non existent title")

    dispose_of([post_key])
    dispose_of([category_key])
    dispose_of(new_tag_keys)


def test_get_names_from_tags(tags, dispose_of):
    test_tags = ["a new tag", "a new new tag"]
    tag_keys = tags.add(test_tags)

    assert test_tags == tags.get_names()

    dispose_of(tag_keys)


def test_to_json_of_a_tag(tags, dispose_of):
    test_tags = ["a new tag", "a new new tag"]
    tag_key1, tag_key2 = tags.add(test_tags)
    tag = tag_key1.get()

    test_dict = {"id":str(tag_key1.id()), "tag":u"a new tag"}

    assert test_dict == tag.to_json()

    dispose_of([tag_key1, tag_key2])


def test_to_json_of_tags(tags, dispose_of):
    test_tags = [u"a new tag", u"a new new tag"]
    tag_key1, tag_key2 = tags.add(test_tags)

    json_data = [{"id":key,"tag":val} for key, val in zip([str(tag_key1.id()), str(tag_key2.id())], test_tags)]

    assert json_data == tags.to_json()

    dispose_of([tag_key1, tag_key2])


def test_get_a_post(categories, tags, posts, dispose_of):
    category_key = categories.add("category")
    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)
    post_key = posts.add("a title", "body text", category_key, new_tag_keys)

    #test with no memcache
    post = BlogPost.get(post_key.id())
    assert post.key == post_key

    #test memcached
    post = BlogPost.get(post_key.id())
    assert post.key == post_key

    dispose_of([post.key])
    dispose_of(new_tag_keys)
    dispose_of([category_key])


def test_filter_posts_by_a_tag(posts, categories, tags, dispose_of):
    category_key = categories.add("category")
    test_tags = ["a new tag", "a new new tag"]
    new_test_tags = ["a second tag", "a new second tag"]
    new_tag_keys = tags.add(test_tags)
    new_test_tag_keys = tags.add(new_test_tags)
    post_key = posts.add("a title", "body text", category_key, new_tag_keys)
    post_key2 = posts.add("a title", "a second body text", category_key, new_test_tag_keys )

    posts.filter_by_tag("a new tag")
    print(posts, hex(id(posts)), len(posts))
    assert posts == [post_key.get()]

    dispose_of([post_key, post_key2])
    dispose_of(tags.get_keys())
    dispose_of([category_key])


# def test_filter_posts_by_category(posts):
#
#     post1, _, _, _ = post_with_answers({"ans1": True, "ans2": False}, category="cat 1")
#     post2, _, _, _ = post_with_answers({"ans1": True, "ans2": False}, category="cat 2")
#
#     posts.filter_by_category("cat 1")
#
#     assert posts == [post2]
#
#     posts.filter_by_category("cat 1")
#
#     assert posts == [post1]
#
#     posts.filter_by_category("wrong cat")
#
#     assert posts == []

def test_get_category(categories, tags, posts, dispose_of):
    category_key = categories.add("category")
    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)
    post_key = posts.add("a title", "body text", category_key, new_tag_keys)

    post = BlogPost.get(post_key.id())

    assert "category" == post.get_category()

    dispose_of([post_key])
    dispose_of(new_tag_keys)
    dispose_of([category_key])


def test_get_tagnames(categories, tags, posts, dispose_of):
    category_key = categories.add("category")
    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)
    post_key = posts.add("a title", "body text", category_key, new_tag_keys)

    post = BlogPost.get(post_key.id())

    tag_names = post.get_tag_names()

    assert test_tags == tag_names

    dispose_of([post_key])
    dispose_of(new_tag_keys)
    dispose_of([category_key])


def test_posts_contains_a_post(categories, tags, posts, dispose_of):
    category_key = categories.add("category")
    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)
    post_key = posts.add("a title", "body text", category_key, new_tag_keys)

    assert post_key in posts

    dispose_of([post_key])
    dispose_of(new_tag_keys)
    dispose_of([category_key])


def test_tags_contains_a_tag(tags, dispose_of):
    test_tags = ["a new tag", "a new new tag"]
    tag_keys = tags.add(test_tags)

    assert test_tags[0] in tags

    dispose_of(tag_keys)


def test_categories_contains_a_category(categories, dispose_of):
    category_key = categories.add("category")
    assert "category" in categories

    dispose_of([category_key])


def test_filter_matched(categories, tags, posts, dispose_of):
    category_key = categories.add("category")
    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)
    post_key = posts.add("a title", "body text", category_key, new_tag_keys)
    post_key2 = posts.add("a title", "body sec2 text", category_key, new_tag_keys)

    posts.filter_matched([post_key.id()])
    assert posts == [post_key.get()]

    dispose_of([post_key, post_key2])
    dispose_of(tags.get_keys())
    dispose_of([category_key])


def test_site_last_updated(categories, tags, posts, dispose_of):
    freezer = freeze_time("2017-11-29 17:48:18")
    freezer.start()
    category_key = categories.add("category")
    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)
    post_key1 = posts.add("a title", "body text", category_key, new_tag_keys)
    post_key2 = posts.add("a title", "body sec2 text", category_key, new_tag_keys)

    last_updated = posts.site_last_updated()
    assert "Wednesday 29 November 2017" == last_updated
    freezer.stop()

    dispose_of([post_key1, post_key2])
    dispose_of(new_tag_keys)
    dispose_of([category_key])


def test_get_related_posts(categories, tags, posts, dispose_of):
    category_key = categories.add("category")
    test_tags = ["a new tag", "a new new tag"]
    new_tag_keys = tags.add(test_tags)
    current_post_key = posts.add("a title", "body text", category_key, new_tag_keys)

    rel_test_tags = ["a new tag", "a different tag"]
    rel_tag_keys = tags.add(rel_test_tags )
    rel_post_key = posts.add("a different title", "body sec2 text", category_key, rel_tag_keys)
    rel_post = BlogPost.get(rel_post_key.id())

    related_posts = posts.get_related_posts(current_post_key.id())

    assert [rel_post] == related_posts

    dispose_of([current_post_key, rel_post_key])
    dispose_of(tags.get_keys())

    dispose_of([category_key])


def test_update_category(categories, dispose_of):
    category_key = categories.add("category")

    categories.update("a modified category", category_key)
    category = categories.get(category_key)

    assert "a modified category" == category.category

    dispose_of([category_key])


def test_update_category_without_key(categories, dispose_of):
    category_key = categories.update("a modified category")
    category = categories.get(category_key)

    assert "a modified category" == category.category

    dispose_of([category_key])


def test_update_tags_without_post(categories, tags, posts, dispose_of):
    test_tags = ["a new tag", "a new new tag"]
    tag_keys = tags.add(test_tags)

    category_key = categories.add("category")
    post_key = posts.add("a title", "body text", category_key, tag_keys)

    test_new_tags = ["a new different tag", "a new new tag"]
    tags.update(test_new_tags)
    tag_names = tags.get_names()

    assert tag_names == [u"a new tag",  u"a new new tag", u"a new different tag"]

    dispose_of([post_key])
    dispose_of(tags.get_keys())
    dispose_of([category_key])


def test_update_tags(categories, tags, posts, dispose_of):
    """
    replacing a new tag with a new different tag
    :return:
    """
    test_tags = ["a new tag", "a new new tag"]
    tag_keys = tags.add(test_tags)

    category_key = categories.add("category")
    post_key = posts.add("a title", "body text", category_key, tag_keys)

    test_new_tags = ["a new different tag", "a new new tag"]
    tags.update(test_new_tags, BlogPost.get(post_key.id()))
    tag_names = tags.get_names()

    assert tag_names == [ u"a new new tag", u"a new different tag"]

    dispose_of([post_key])
    dispose_of(tags.get_keys())
    dispose_of([category_key])


# def test_rebuild_index(categories, tags, posts):
#     test_tags = ["a new tag", "a new new tag"]
#     tag_keys = tags.add(test_tags)
#
#     category_key = categories.add("category")
#     post_key = posts.add("a title", "body text", category_key, tag_keys)
#
#     posts.rebuild_index()
#
#     results = query_search_index("body")
#     posts_ids = find_posts_from_index(results)
#
#     assert post_key.id(), posts_ids[0])

def test_add_to_feed(categories, tags, posts, dispose_of):
    test_tags = ["a new tag", "a new new tag"]
    tag_keys = tags.add(test_tags)

    category_key = categories.add("category")
    post_key = posts.add("a title", "body text", category_key, tag_keys)

    feed_org = AtomFeed('Recent Articles',
                    feed_url='http://localhost/recent.atom', url="")

    feed_model = AtomFeed('Recent Articles',
                        feed_url='http://localhost/recent.atom', url="")

    for post in posts:
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

    feed = posts.add_to_feed(feed_model, "http://localhost/recent.atom")

    assert feed_org.to_string() == feed.to_string()

    dispose_of([post_key])
    dispose_of(tag_keys)
    dispose_of([category_key])


def test_stripped_answers(categories, tags, dispose_of):
    test_tags = ["a new tag", "a new new tag"]
    tag_keys = tags.add(test_tags)

    ans1 = Answer(p_answer="ans1",
           is_correct=True)

    ans2 = Answer(p_answer="ans2",
                  is_correct=False)

    category_key = categories.add("category")
    summary = "a summmary"
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

    assert post.strip_answers_jsoned() == jsoned_answers

    dispose_of([post_key])
    dispose_of(tag_keys)
    dispose_of([category_key])


def test_selected_answer_setter(post_with_answers):
    post, _, _, _ = post_with_answers
    ans1 = Answer(p_answer="ans1",
                  is_correct=True)

    post.set_selected_answer("ans1")
    print("ans1", ans1)
    assert ans1 == \
           post.selected_answer


def test_is_answer_correct(post_with_answers):
    post, _, _, _ = post_with_answers
    post.set_selected_answer("ans1")

    assert post.is_answer_correct()

    post.set_selected_answer('ans2')
    assert not post.is_answer_correct()

    post.set_selected_answer('non existent')
    assert not post.is_answer_correct()


def test_to_answer_form(posts, post_with_answers):

    with app.test_request_context():
        post, _, _, _ = post_with_answers
        posts.to_answers_form()
        print (dir(post))
        assert [(u'ans1', u'ans1'), (u'ans2', u'ans2')] == post.answers_form.r_answers.choices


def test_update_answers_statistics(post_with_answers):
    post, _, _, _ = post_with_answers

    post.set_selected_answer("ans1")

    assert (post.answers[0].statistics, post.answers[1].statistics) == (1.0, 0.0)
    assert post.answers[0].nof_times_selected, post.answers[1].nof_times_selected == (1, 0)

    post.set_selected_answer("ans2")

    assert (post.answers[0].statistics, post.answers[1].statistics) == (0.5, 0.5)
    assert (post.answers[0].nof_times_selected, post.answers[1].nof_times_selected) == (1, 1)

    post.set_selected_answer("ans2")

    assert post.answers[0].statistics == pytest.approx(0.3333, 4)
    assert post.answers[1].statistics == pytest.approx(0.6666666666666666, 4)
    assert (post.answers[0].nof_times_selected, post.answers[1].nof_times_selected) == (1, 2)
#
# def test_get_answers_statistics(self):
#     post, _, _, _ = post_with_answers({"ans1": True, "ans2": False, "ans3": False})
#     post.set_selected_answer("ans1")
#
#     answers_stats = post.get_answers_statistics()
#
#     self.assertDictEqual(answers_stats, {"Answer":"Selection","ans1": 1, "ans2": 0, "ans3":0})
#
#     post.set_selected_answer("ans2")
#
#     answers_stats = post.get_answers_statistics()
#
#     self.assertDictEqual(answers_stats, {"Answer":"Selection","ans1": 1,"ans2": 1,"ans3":0})
#
#     answers_stats = post.get_answers_statistics()
#     self.assertDictEqual(answers_stats, {"Answer": "Selection", u"ans1": 1, u"ans2": 1, u"ans3": 0})
#
# def test_add_blob(self):
#     post, _, _ = self.create_post()
#
#     with open(os.path.join(TEST_IMAGE)) as f:
#         image_key = post.add_blob(f.read(), TEST_IMAGE, 'image/jpeg')
#         assert image_key, u'encoded_gs_file:YXBwX2RlZmF1bHRfYnVja2V0LzIwMTlfMV80XzE2ei5naWY=')
#
# def test_delete_blob(self):
#     from google.appengine.ext import blobstore
#     post, _, _ = self.create_post()
#
#     with open(os.path.join(TEST_IMAGE)) as f:
#         image_key = post.add_blob(f.read(), TEST_IMAGE, 'image/jpeg')
#
#     post._delete_blob(TEST_IMAGE)
#     with self.assertRaises(blobstore.BlobNotFoundError):
#         blobstore.fetch_data(image_key, 0, 1)
#
# def test_read_blob_image(self):
#     post, _, _ = self.create_post()
#     with open(os.path.join(TEST_IMAGE)) as f:
#         post.add_blob(f.read(), TEST_IMAGE, 'image/jpeg')
#         image_file = post.read_blob_image(TEST_IMAGE)
#
#         f.seek(0)
#         assert image_file, f.read())
#
# def test_list_images(self):
#     post, _, _ = self.create_post()
#     with open(os.path.join(TEST_IMAGE)) as f:
#         post.add_blob(f.read(), TEST_IMAGE, 'image/jpeg')
#     self.assertListEqual(post.list_images(), ['/app_default_bucket/{}'.format(TEST_IMAGE)])
#
# def test_mime_type(self):
#     post, _, _ = self.create_post()
#     with open(os.path.join(TEST_IMAGE)) as f:
#         post.add_blob(f.read(), TEST_IMAGE, 'image/jpeg')
#     assert post.get_mime_type(TEST_IMAGE), 'image/jpeg')
#
# def test_delete_image(self):
#     post, _, _ = self.create_post()
#     with open(os.path.join(TEST_IMAGE)) as f:
#         image_key = post.add_blob(f.read(), TEST_IMAGE, 'image/jpeg')
#
#     post._delete_blob(TEST_IMAGE)
#     with self.assertRaises(cloudstorage.NotFoundError):
#         post.get_blob(image_key)
#
# def test_delete_blob_from_post(self):
#     post, _, _ = self.create_post()
#     with open(os.path.join(TEST_IMAGE)) as f:
#         post.add_blob(f.read(), TEST_IMAGE, 'image/jpeg')
#
#     assert 1, len(post.images))
#
#     post.delete_blob_from_post(TEST_IMAGE)
#
#     assert 0, len(post.images))
#
