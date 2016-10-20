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
    def append(self, post):
        """update list of posts and memcache"""
        self._delete_memcache()
        self._populate_memcache()
        self.append(post)


class Posts(BlogList):
    """list of posts"""
    def __init__(self):
        self.posts = []
        if not self._retrieve_from_memcache():
            self.posts = BlogPost.all().order('-timestamp')
            self._populate_memcache()
            self._populate_search_index()


    def _populate_memcache(self):
        """populate memcache
        use key as post plus post.id"""
        logging.info('cache is empty creating index')
        if not memcache.add("POSTS_CACHE", self.posts):
            logging.error("Memcache set failed for posts")

    def _retrieve_from_memcache(self):
        return memcache.get("POSTS_CACHE")

    def _populate_search_index(self):
        try:
            for post in self.posts:
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


class Tags(BlogList):

    def __init__(self):
        self.tags = []
        if not memcache.get("TAGS_CACHE"):
            self.tags = Tag.all()
            self._populate_memcache()

    def _retrieve_from_memcache(self):
        return memcache.get("TAGS_CACHE")

    def _populate_memcache(self):
        if not memcache.add("TAGS_CACHE", self.tags):
            logging.error("Memcache set failed for tags")

    def _delete_memcache(self):
        if not memcache.delete('TAGS_CACHE') != 2:
            logging.error("Memcache delete failed for tags")

    def __getitem__(self, tag):
        return self.tags[tag]

    def __contains__(self, tag):
        for tag in self.tags:
            if tag.tag == tag:
                break
                return True
        return False


class Categories(BlogList):

    def __init__(self):
        self.categories = []
        if not self._retrieve_from_memcache():
            self.categories = Category.all()
            self._populate_memcache()

    def _retrieve_from_memcache(self):
        return memcache.get("CATEGORIES_CACHE")

    def _populate_memcache(self):
        if not memcache.add("CATEGORIES_CACHE", self.categories):
            logging.error("Memcache set failed for categories")

    def _delete_memcache(self):
        if not memcache.delete('CATEGORIES_CACHE') != 2:
            logging.error("Memcache delete failed for categories")

    @staticmethod
    def get_key(category):
        return memcache.get(category)



