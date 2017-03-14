import logging
from google.appengine.ext import ndb
from google.appengine.api import memcache

from search import add_document_in_search_index, delete_document


POSTS_INDEX = "posts_idx"


class Tag(ndb.Model):
    tag = ndb.StringProperty()

    def to_json(self):
        tag_dict = self.to_dict()
        tag_dict["id"] = str(self.key.id())
        return tag_dict


class Category(ndb.Model):
    category = ndb.StringProperty()


class BlogPost(ndb.Model):
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now_add=True)
    tags = ndb.KeyProperty(repeated=True)  # one to many relation
    category = ndb.KeyProperty(kind=Category)
    summary = ndb.TextProperty()

    @classmethod
    def get(cls, id):
        post = memcache.get('{}:posts'.format(id))
        if not post:
            post = cls.get_by_id(int(id))
            added = memcache.add(
                '{}:posts'.format(id), post, 100)
            if not added:
                logging.error('Memcache set failed for entity {}'.format(id))

        return post

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        """creates json based structure"""
        post_dict = self.to_dict()
        post_dict["id"] = self.key.id()
        post_dict["tags"] = self.get_tag_names()
        post_dict["category"] = self.category.get().category
        return post_dict

    def edit(self, title, body, updated, tags, category):
        self.title = title
        self.body = body
        self.updated = updated
        self.tags = tags
        self.category = category
        self.put()
        add_document_in_search_index(self.id, self.title, self.body,
                                     self.summary, self.get_category(),
                                     self.timestamp)

    def get_tag_names(self):
        return [tag_key.get().tag for tag_key in self.tags
                if self.tags and tag_key.get()]

    def get_category(self):
        return self.category.get().category

    def _pre_put_hook(self):
        self.title = self.title.lstrip().rstrip()


class BlogList(list):

    @staticmethod
    def retrieve_from_memcache(cache_name):
        entities = memcache.get(cache_name)
        return list(entities) if entities else []

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
        add_document_in_search_index(post.id, post.title, post.body,
                                     post.summary, post.get_category(),
                                     post.timestamp)

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
        post.key.delete()
        delete_document(post.id)

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
        return [post for post in self._posts if tag in post.get_tag_names()]


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

    def get_names(self, keys=[]):
        return [tag.tag for tag in self._tags]


class Categories(BlogList):

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

    def delete(self, category_for_deletion):
        for cat_idx, category in enumerate(self._categories):
            if category.category == category_for_deletion:
                category.key.delete()
                self._categories.pop(cat_idx)
                self.delete(category_for_deletion)
