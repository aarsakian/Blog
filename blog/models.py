import logging
from google.appengine.ext import ndb
from google.appengine.api import memcache

from utils import datetimeformat

from errors import InvalidUsage

from forms import AnswerRadioForm
from search import add_document_in_search_index, delete_document, find_posts_from_index
from utils import find_modified_tags, find_tags_to_be_removed, find_tags_to_be_added, make_external

POSTS_INDEX = "posts_idx"


class Answer(ndb.Model):
    p_answer = ndb.TextProperty()
    is_correct = ndb.BooleanProperty(default=False)
    nof_times_selected = ndb.IntegerProperty(default=0)
    statistics = ndb.FloatProperty(default=0.0)


class Tag(ndb.Model):
    tag = ndb.StringProperty()

    def to_json(self):
        tag_dict = self.to_dict()
        tag_dict["id"] = str(self.key.id())
        return tag_dict


class Category(ndb.Model):
    category = ndb.StringProperty()


    def to_json(self):
        cat_dict = self.to_dict()
        cat_dict["id"] = str(self.key.id())
        return cat_dict

    @staticmethod
    def add_to_memcache(category):
        added = memcache.add(
            '{}:posts'.format(id), category, 100)
        if not added:
            logging.error('Memcache set failed for entity {}'.format(id))

    @classmethod
    def get(cls, id):
        category = memcache.get('{}:categories'.format(id))
        if not category:
            category = cls.get_by_id(int(id))
            Category.add_to_memcache(category)
        return category


class BlogPost(ndb.Model):
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now_add=True)
    tags = ndb.KeyProperty(repeated=True)  # one to many relation
    category = ndb.KeyProperty(kind=Category)
    summary = ndb.TextProperty()
    answers = ndb.StructuredProperty(Answer, repeated=True)

    def strip_answers_jsoned(self):
        return [{"p_answer" :answer.p_answer, "is_correct":False}
                for answer in self.answers if answer.p_answer != u'']

    @staticmethod
    def add_to_memcache(post):
        added = memcache.add(
            '{}:posts'.format(id), post, 100)
        if not added:
            logging.error('Memcache set failed for entity {}'.format(id))

    @classmethod
    def get(cls, id):
        post = memcache.get('{}:posts'.format(id))
        if not post:
            post = cls.get_by_id(int(id))
            BlogPost.add_to_memcache(post)
        return post

    @property
    def id(self):
        return self.key.id()

    def set_selected_answer(self, p_answer):
        for answer in self.answers:
            if answer.p_answer == p_answer:
                self.selected_answer = answer
                break

    def to_json(self):
        """creates json based structure"""
        post_dict = self.to_dict()
        jsoned_data = {}
        jsoned_data[u"title"] = post_dict["title"]
        jsoned_data[u"body"] = post_dict["body"]
        jsoned_data[u"summary"] = post_dict["summary"]
        jsoned_data[u"id"] = str(self.key.id())
        jsoned_data[u"tags"] = self.get_tag_names()
        jsoned_data[u"category"] = self.category.get().category
        jsoned_data[u"updated"] = datetimeformat(post_dict["updated"])
        jsoned_data[u"timestamp"] = datetimeformat(post_dict["timestamp"])
        jsoned_data[u"answers"] = post_dict["answers"]
        return jsoned_data

    def to_answers_form(self):

        self.answers_form = AnswerRadioForm()
        self.answers_form.r_answers.choices = [(answer.p_answer, answer.p_answer) for answer in self.answers]

    def edit(self, title, body, updated, tags, category_key, summary=None, answers=[]):

        self.title = title
        self.body = body
        self.updated = updated
        self.tags = tags
        self.category = category_key
        self.summary = summary
        if answers:
            self.answers = [Answer(p_answer=answer['p_answer'],
                                        is_correct=answer['is_correct']) for answer in answers]



        self.put()
        add_document_in_search_index(self.id, self.title, self.body,
                                     self.summary, self.get_category(),
                                     self.timestamp, self.get_tag_names())

    def get_tag_names(self):
        return [tag_key.get().tag for tag_key in self.tags
                if self.tags and tag_key.get()]

    def get_category(self):
        return self.category.get().category

    def _pre_put_hook(self):
        self.title = self.title.lstrip().rstrip()

    def is_answer_correct(self):
        return self.selected_answer.is_correct

    def update_statistics(self):
        self.selected_answer.nof_times_selected += 1
        self.put()

        total_participation = \
            sum([answer.nof_times_selected for answer in self.answers])

        for answer in self.answers:
            answer.statistics = float(answer.nof_times_selected)/total_participation


class BlogList(list):

    @classmethod
    def get_attr(cls):
        return str(cls.__name__.lower())


class JsonMixin:

    def to_json(self):
        """prepare data for json consumption add extra fields"""
        entities = getattr(self, self.__class__.get_attr())
        return [entity.to_json() for entity in entities]


class Posts(BlogList, JsonMixin):
    """
        list of posts
    """

    def __init__(self):
        self._posts = BlogPost.query().order(-BlogPost.timestamp)

    @property
    def posts(self):
        return list(self._posts)

    def __len__(self):
        return len(self.posts)

    def __iter__(self):
        return (post for post in self.posts)

    def __getitem__(self, post_idx):
        return self.posts[post_idx]

    def __contains__(self, post_key):
        if self._posts:
            for post in self.posts:
                if post.key == post_key:
                    return True
        return False

    def add(self, raw_title, raw_body, category_key, tags_ids, summary=None, answers=None):
        """
            adds a post to the list of current posts
            and updates search index
        :param raw_title:
        :param raw_body:
        :param category_key:
        :param tags_ids:
        :param summary:
        :param answers:
        :return: key of the added post
        """

        if answers:
            for answer in answers:
                logging.info("{} {}".format(len(answer), answer))
            processed_answers = [Answer(p_answer=answer['p_answer'],
                                        is_correct=answer['is_correct'])
                                 for answer in answers if answer['p_answer'] != '']
        else:
            processed_answers = []

        post_key = BlogPost(title=raw_title,
                            body=raw_body,
                            category=category_key,
                            tags=tags_ids,
                            summary=summary,
                            answers=processed_answers).put()

        post = post_key.get()
        self.posts.append(post)
        BlogPost.add_to_memcache(post)
        add_document_in_search_index(post.id, post.title, post.body,
                                     post.summary, post.get_category(),
                                     post.timestamp, post.get_tag_names())

        return post_key

    def get_tags(self):
        tags = []
        [tags.extend(post.get_tag_names()) for post in self.posts]
        return tags

    def get_other_tags(self, post_id):
        other_tags = []
        [other_tags.extend(post.get_tag_names())
         for post in self.posts if post.key.id() != post_id]
        return other_tags

    def delete(self, post_key):
        [self.posts.pop(post_idx) for post_idx, post
         in enumerate(self.posts) if post.key == post_key]
        post_key.delete()
        delete_document(post_key.id())

    def get_by_title(self, title):
        for post in self.posts:
            if post.title.lower() == title or post.title == title:
                post_f = post
                break
        try:
            return post_f
        except:
            logging.error("Post Not Found")
            raise InvalidUsage('This post is not found', status_code=404)

    def filter_by_tag(self, tag):
        [self.posts.pop(post_idx) for post_idx, post in enumerate(self.posts)
                if tag not in post.get_tag_names()]

    def filter_by_category(self, category):
        [self.posts.pop(post_idx) for post_idx, post in enumerate(self.posts)
         if category not in post.get_category()]

    def filter_matched(self, posts_ids):
        [self.posts.pop(post_idx) for post_idx, post in enumerate(self.posts)
         if post.id not in posts_ids]

    def site_last_updated(self):
        if self.posts:
            last_post = list(BlogPost.query().order(-BlogPost.updated))[0]
            return last_post.updated.strftime('%A %d %B %Y')

    def get_related_posts(self, current_post_id):
        related_posts = []
        current_post = BlogPost.get(current_post_id)
        for post in self.posts:
            if post.id != current_post.id:
                for tag in post.tags:
                    if tag.get().tag in current_post.get_tag_names():
                        related_posts.append(post)
                        break
        return related_posts

    def add_to_feed(self, feed, base_url):
        for post in self.posts:
            catname = post.get_category()
            url = "/".join([catname,
                        post.timestamp.strftime('%B'),
                        post.timestamp.strftime('%Y')])
            feed.add(post.title, post.body,
                 content_type='html',
                 author='Armen Arsakian',
                 url=make_external(base_url, url),
                 updated=post.updated,
                 published=post.timestamp)

        return feed

    def rebuild_index(self):
        for post in self.posts:
            add_document_in_search_index(post.id, post.title, post.body,
                                         post.summary, post.get_category(),
                                         post.timestamp, post.get_tag_names())

    def to_answers_form(self):
        [post.to_answers_form() for post in self.posts]



class Tags(BlogList, JsonMixin):

    def __init__(self):
       # self._tags = BlogList.retrieve_from_memcache("TAGS_CACHE")
       # if not self._tags:
        self._tags = list(Tag.query())
       # self._populate_memcache()

    def __contains__(self, raw_tag):
        if self._tags:
            for tag in self._tags:
                if tag.tag == raw_tag:
                    return True
        return False

    def __iter__(self):
        return (tag.tag for tag in self._tags)

    def __len__(self):
        return len(self._tags)

    @property
    def tags(self):
        return self._tags

    def _populate_memcache(self):
        logging.info("populating cache for tags {}")
        if not memcache.add("TAGS_CACHE", self._tags):
            logging.error("Memcache set failed for tags")

    def _delete_memcache(self):
        if not memcache.delete('TAGS_CACHE') != 2:
            logging.error("Memcache delete failed for tags")

    def add(self, new_tags):
        new_tags_keys = [Tag(tag=new_tag).put() for new_tag in new_tags if new_tag not in self]
        self._tags.extend([tag_key.get() for tag_key in new_tags_keys])
        return new_tags_keys

    def delete(self, tags_for_deletion):
        for tag_idx, tag in enumerate(self._tags):
            if tag.tag in tags_for_deletion:
                tag.key.delete()
                self._tags.pop(tag_idx)
                self.delete(tags_for_deletion)

    def get_keys(self, tags):
        return [tag.key for tag in self._tags if tag.tag in tags]

    def get_names(self):
        return [tag.tag for tag in self._tags]

    def update(self, editing_tags, updating_post=None):
        posts = Posts()
        if updating_post:
            remaining_tags = posts.get_other_tags(int(updating_post.id))
            old_post_tags = updating_post.get_tag_names()
        else:
            remaining_tags = posts.get_tags()
            old_post_tags = []

        non_modified_tags = set(editing_tags) & set(old_post_tags)

        tags_to_be_removed = find_tags_to_be_removed(old_post_tags, non_modified_tags, remaining_tags)
        tags_to_be_added = find_tags_to_be_added(editing_tags, non_modified_tags, remaining_tags)

        self.add(tags_to_be_added)
        self.delete(tags_to_be_removed)

        return self.get_keys(editing_tags)


class Categories(BlogList, JsonMixin):

    def __init__(self):
        self._categories = list(Category.query())

    def __contains__(self, raw_category):
        if self._categories:
            for category in self._categories:
                print  category.category, raw_category
                if category.category == raw_category:
                    return True
        return False

    def __iter__(self):
        return (category.category for category in self._categories)

    def __len__(self):
        return len(self._categories)

    @property
    def categories(self):
        return self._categories

    def add(self, raw_category):
        if raw_category not in self:
            category_key = Category(category=raw_category).put()
            self._categories.append(Category.get_by_id(category_key.id()))
        else:
            category_key = self.get_key(raw_category)

        return category_key

    def get_key(self, raw_category):
        """
            get key from a category string
        :param raw_category:
        :return: the key of the requested category
        """
        return [category.key for category in self._categories
                if category.category == raw_category][0]

    def delete(self, category_key):
        [self._categories.pop(cat_idx) for cat_idx, category
         in enumerate(self._categories) if category.key == category_key]
        category_key.delete()

    def update(self, raw_category, category_key=None):

        if category_key:
            category = Category.get(category_key.id())
            category.category = raw_category
            category.put()
        else:

            category_key = self.add(raw_category)

        return category_key

    def get(self, category_key):
        return  Category.get(category_key.id())
