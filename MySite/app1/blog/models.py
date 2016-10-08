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



class Posts(list):
    """list of posts"""
    def __init__(self):
        self.posts = BlogPost.all().order('-timestamp')
        self._populate_memcache()
        self._populate_search_index()

    def _populate_memcache(self):
        """populate memcache
        use key as post plus post.id"""
        logging.info('cache is empty creating index')
        for post in self.posts:
            if not memcache.add('{}'.format(post.key().id()), post):
                logging.error("Memcache set failed for article {}".format
                              (post.title))


    def _populate_search_index(self):
        try:
            for post in self.posts:
                category = db.get(post.category.key()).category
                doc = create_document(post.key().id(), post.title, post.body,
                                      category, post.timestamp)
                search.Index(name=POSTS_INDEX).put(doc)

        except search.Error:
            logging.exception('Indexing failed')

    def to_json(self):
        """prepare data for json consumption add extra fields"""
        posts_jsonified = []
        for post in self.posts:
            post_dict = db.to_dict(post)
            post_dict["id"] = post.key().id()
            post_dict["tags"] = [db.get(tag).tag for tag in post.tags]
            post_dict["category"] = db.get(post.category.key()).category
            posts_jsonified.append(post_dict)

        return posts_jsonified


class Tags(list):

    def __init__(self):
        self.tags = []

    def populate(self):
        self.tags = Tag.all()
        self._populate_memcache()

    def _populate_memcache(self):
        for tag in self.tags:
            if not memcache.add('{}'.format(tag.tag), tag):
                logging.error("Memcache set failed for tag {}".format
                              (tag.tag))

    @staticmethod
    def get_keys(tags):
        return [(memcache.get(tag), tag) for tag in tags if memcache.get(tag)]

    def __contains__(self, tag):
        for tag in self.tags:
            if tag.tag == tag:
                break
                return True
        return False


class Categories(list):

    def __init__(self):
        self.categories = []

    def populate(self):
        self.categories = Category.all()
        self._populate_memcache()

    def _populate_memcache(self):
        for category in self.categories:
            if not memcache.add('{}'.format(category.category), category):
                logging.error("Memcache set failed for tag {}".format
                              (category.category))

    @staticmethod
    def get_key(category):
        return memcache.get(category)



