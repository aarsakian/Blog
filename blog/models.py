import logging
from google.appengine.ext import ndb
from google.appengine.api import memcache

from utils import datetimeformat

from search import add_document_in_search_index, delete_document, find_posts_from_index
from utils import find_modified_tags, find_tags_to_be_removed, find_tags_to_be_added

POSTS_INDEX = "posts_idx"


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

    def to_json(self):
        """creates json based structure"""
        post_dict = self.to_dict()
        jsoned_data = {}
        jsoned_data[u"title"] = post_dict["title"]
        jsoned_data[u"body"] = post_dict["body"]
        jsoned_data[u"summary"] = post_dict["summary"]
        jsoned_data[u"id"] = int(self.key.id())
        jsoned_data[u"tags"] = self.get_tag_names()
        jsoned_data[u"category"] = self.category.get().category
        jsoned_data[u"updated"] = datetimeformat(post_dict["updated"])
        jsoned_data[u"timestamp"] = datetimeformat(post_dict["timestamp"])
        return jsoned_data

    def edit(self, title, body, updated, tags, category):
        self.title = title
        self.body = body
        self.updated = updated
        self.tags = tags
        self.category = category
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
        self._posts = list(BlogPost.query().order(-BlogPost.timestamp))

    @property
    def posts(self):
        return self._posts

    def __len__(self):
        return len(self._posts)

    def __iter__(self):
        return (post for post in self._posts)

    def __getitem__(self, post_idx):
        return self._posts[post_idx]

    def __contains__(self, post_key):
        if self._posts:
            for post in self._posts:
                if post.key == post_key:
                    return True
        return False

    def add(self, raw_title, raw_body, category_key, tags_ids, summary=None):
        """
            adds a post to the list of current posts
            and updates search index
        :param raw_title:
        :param raw_body:
        :param category_key:
        :param tags_ids:
        :param summary:
        :return: key of the added post
        """
        post_key = BlogPost(title=raw_title,
                            body=raw_body,
                            category=category_key,
                            tags=tags_ids,
                            summary=summary).put()
        post = post_key.get()
        self._posts.append(post)
        BlogPost.add_to_memcache(post)
        add_document_in_search_index(post.id, post.title, post.body,
                                     post.summary, post.get_category(),
                                     post.timestamp, post.get_tag_names())

        return post_key

    def get_tags(self):
        tags = []
        [tags.extend(post.get_tag_names()) for post in self._posts]
        return tags

    def get_other_tags(self, post_id):
        other_tags = []
        [other_tags.extend(post.get_tag_names())
         for post in self._posts if post.key.id() != post_id]
        return other_tags

    def delete(self, post_key):
        [self._posts.pop(post_idx) for post_idx, post
         in enumerate(self._posts) if post.key == post_key]
        post_key.delete()
        delete_document(post_key.id())

    def get_by_title(self, title):
        for post in self._posts:
            if post.title == title:
                post_f = post
                break
        try:
            return post_f
        except:
            logging.error("Post Not Found")
            raise LookupError

    def filter_by_tag(self, tag):
        [self._posts.pop(post_idx) for post_idx, post in enumerate(self._posts)
                if tag not in post.get_tag_names()]

    def filter_matched(self, posts_ids):
        [self._posts.pop(post_idx) for post_idx, post in enumerate(self._posts)
         if post.id not in posts_ids]

    def site_last_updated(self):
        if self.posts:
            last_post = self._posts[-1]
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
        new_tags_keys = [Tag(tag=new_tag).put() for new_tag in new_tags]
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
        else:
            remaining_tags = posts.get_tags()

        old_post_tags = updating_post.get_tag_names()

        non_modified_tags = set(editing_tags) & set(old_post_tags)

        tags_to_be_removed = find_tags_to_be_removed(old_post_tags, non_modified_tags, remaining_tags)
        tags_to_be_added = find_tags_to_be_added(editing_tags, non_modified_tags, remaining_tags)

        tags.add(tags_to_be_added)
        tags.delete(tags_to_be_removed)

        return tags.get_keys(editing_tags)


class Categories(BlogList, JsonMixin):

    def __init__(self):
        self._categories = list(Category.query())

    def __contains__(self, raw_category):
        if self._categories:
            for category in self._categories:
                if category.category == raw_category:
                    return True
        return False

    def __iter__(self):
        return (category.category for category in self._categories)

    @property
    def categories(self):
        return self._categories

    def add(self, raw_category):
        category_key = Category(category=raw_category).put()
        self._categories.append(Category.get_by_id(category_key.id()))

        return category_key

    def get_key(self, raw_category):
        """
            get key from a category string
        :param raw_category:
        :return: the key of the requested category
        """
        logging.info("{} {}".format(raw_category, len(self._categories)))
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
        else:
            category_key = self.add(raw_category)

        return category_key

    def get(self, category_key):
        return  Category.get(category_key.id())