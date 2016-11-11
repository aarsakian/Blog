import logging
from google.appengine.ext import db
from google.appengine.api import memcache, search

from search import create_document


POSTS_INDEX = "posts_idx"


class Tag(db.Model):
    tag = db.StringProperty()


class Category(db.Model):
    category = db.StringProperty()


class BlogPost(db.Model):
    title = db.StringProperty()
    body = db.TextProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now_add=True)
    tags = db.ListProperty(db.Key)  # one to many relation
    category = db.ReferenceProperty(Category,
                                    collection_name='category_posts')


class BlogList(list):

    @staticmethod
    def retrieve_from_memcache(cache_name):
        entities = memcache.get(cache_name)
        return list(entities) if entities else []


class JsonMixin:

    def to_json(self):
        """prepare data for json consumption add extra fields"""
        posts_jsonified = []
        if self.posts:
            for post in self.posts:
                post_dict = db.to_dict(post)
                post_dict["id"] = post.key().id()
                post_dict["tags"] = [db.get(tag).tag for tag in post.tags]
                post_dict["category"] = db.get(post.category.key()).category
                posts_jsonified.append(post_dict)

        return posts_jsonified


class Posts(BlogList, JsonMixin):
    """list of posts"""

    __posts__ = BlogList.retrieve_from_memcache("POSTS_CACHE")

    def __init__(self):
        if not self.__posts__:
            self.__posts__ = BlogPost.all().order('-timestamp')
            self._populate_memcache()
            self._populate_search_index()

    @property
    def posts(self):
        return self.__posts__

    def __len__(self):
        return bool(self.__posts__)

    def __iter__(self):
        return (post for post in self.__posts__)

    def __getitem__(self, post_idx):
        return self.__posts__[post_idx]

    def _populate_memcache(self):
        """populate memcache
        use key as post plus post.id"""
        logging.info('cache is empty creating index')
        if not memcache.add("POSTS_CACHE", self.posts):
            logging.error("Memcache set failed for posts")

    def _populate_search_index(self):
        try:
            for post in self.__posts__:
                category = db.get(post.category.key()).category
                doc = create_document(post.key().id(), post.title, post.body,
                                      category, post.timestamp)
                search.Index(name=POSTS_INDEX).put(doc)

        except search.Error:
            logging.exception('Indexing failed')

    def _delete_memcache(self):
        logging.info('deleting cache for Posts')
        if not memcache.delete('POSTS_CACHE') != 2:  # delete not successful
            logging.error("Memcache delete failed for posts")

    def add(self, raw_title, raw_body, category_key, tags_ids):
        post_key = BlogPost(title=raw_title,
                              body=raw_body,
                              category=category_key,
                              tags=tags_ids).put()
        logging.info("new post with key"+str(post_key))
        self.append(BlogPost.get_by_id(post_key.id()))
        self._delete_memcache()
        self._populate_memcache()


class Tags(BlogList):

    __tags__ = BlogList.retrieve_from_memcache("TAGS_CACHE")

    def __init__(self):
        if not self.__tags__:
            self.__tags__ = Tag.all()
            self._populate_memcache()

    def __getitem__(self, tag):
        return self.__tags__[tag]

    def __contains__(self, raw_tag):
        if self.__tags__:
            for tag in self:
                if tag == raw_tag:
                    return True
        return False

    def __iter__(self):
        return (tag.tag for tag in self.__tags__)

    def _populate_memcache(self):
        if not memcache.add("TAGS_CACHE", self.__tags__):
            logging.error("Memcache set failed for tags")

    def _delete_memcache(self):
        if not memcache.delete('TAGS_CACHE') != 2:
            logging.error("Memcache delete failed for tags")

    def add(self, new_tag):
        tag_key = Tag(tag=new_tag).put()
        self.__tags__.append(Tag.get_by_id(tag_key.id()))
        self._delete_memcache()
        self._populate_memcache()

        return tag_key


class Categories(BlogList):

    __categories__ = BlogList.retrieve_from_memcache("CATEGORIES_CACHE")

    def __init__(self):
        if not self.__categories__:
            self.__categories__ = Category.all()
            self._populate_memcache()

    def _populate_memcache(self):
        if not memcache.add("CATEGORIES_CACHE", self.__categories__):
            logging.error("Memcache set failed for categories")

    def _delete_memcache(self):
        if not memcache.delete('CATEGORIES_CACHE') != 2:
            logging.error("Memcache delete failed for categories")

    def add(self, raw_category):
        category_key = Category(category=raw_category).put()
        self.__categories__.append(Category.get_by_id(category_key.id()))
        self._delete_memcache()
        self._populate_memcache()
        return category_key

    def __getitem__(self, raw_category):
        if self.__categories__:
            for category in self:
                if category == raw_category:
                    return category
        return None

    def __iter__(self):
        return (category.category for category in self.__categories__)

    @staticmethod
    def get_key(category):
        return memcache.get(category)



