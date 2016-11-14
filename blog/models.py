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

    def get_tags(self):
        return [Tag.get_by_id(tag_key.id()).tag for tag_key in self.tags]

    def to_json(self):
        post_dict = db.to_dict(self)
        post_dict["id"] = self.key().id()
        post_dict["tags"] = [db.get(tag).tag for tag in self.tags]
        post_dict["category"] = db.get(self.category.key()).category
        return post_dict


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
                posts_jsonified.append(post.to_json())

        return posts_jsonified


class Posts(BlogList, JsonMixin):
    """list of posts"""

    def __init__(self):
        self.__posts__ = BlogList.retrieve_from_memcache("POSTS_CACHE")
        if not self.__posts__:
            self.__posts__ = list(BlogPost.all().order('-timestamp'))
            self._populate_memcache()
            self._populate_search_index()

    @property
    def posts(self):
        return self.__posts__

    def __len__(self):
        logging.info("SPOST {}".format(len(self.__posts__)))
        return len(self.__posts__)

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
        return post_key

    def get_other_tags(self, post_id):
        posts = []
        [posts.extend(post.get_tags()) for post in self.__posts__ if post.id != post_id]
        return posts


class Tags(BlogList):

    def __init__(self):
        self.__tags__ = BlogList.retrieve_from_memcache("TAGS_CACHE")
        if not self.__tags__:
            self.__tags__ = list(Tag.all())
            self._populate_memcache()

    def __contains__(self, raw_tag):
        if self.__tags__:
            for tag in self:
                if tag == raw_tag:
                    return True
        return False

    def __iter__(self):
        return (tag.tag for tag in self.__tags__)

    def __len__(self):
        return len(self.__tags__)

    def _populate_memcache(self):
        logging.info("populating cache for tags {}".format(self.__tags__))
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

    def delete(self, tag):
        obj = self.__tags__[tag]
        obj.delete()



class Categories(BlogList):

    def __init__(self):
        self.__categories__ = BlogList.retrieve_from_memcache("CATEGORIES_CACHE")
        if not self.__categories__:
            self.__categories__ = list(Category.all())
            self._populate_memcache()

    def __contains__(self, raw_category):
        if self.__categories__:
            for category in self.__categories__:
                if category.category == raw_category:
                    return True
        return False

    def __iter__(self):
        return (category.category for category in self.__categories__)

    def __getitem__(self, category_idx):
        return self.__categories__[category_idx]

    def _populate_memcache(self):
        logging.info("populating cache for categories {}".format(self.__categories__))
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

    def get_key(self, raw_category):
        if raw_category in self.__categories__:
            return self.__categories[self.__categories__.index(raw_category)].key()
