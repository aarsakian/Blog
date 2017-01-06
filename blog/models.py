import logging
from google.appengine.ext import ndb
from google.appengine.api import memcache, search

from search import create_document


POSTS_INDEX = "posts_idx"


class Tag(ndb.Model):
    tag = ndb.StringProperty()


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

    def get_tag_names(self):
        return [tag_key.get().tag for tag_key in self.tags if self.tags]

    def _pre_put_hook(self):
        self.title = self.title.lstrip().rstrip()


class BlogList(list):

    @staticmethod
    def retrieve_from_memcache(cache_name):
        entities = memcache.get(cache_name)
        return list(entities) if entities else []

    def update(self):
        self._delete_memcache()
        self._populate_memcache()



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
       # self.__posts__ = BlogList.retrieve_from_memcache("POSTS_CACHE")
        #if not self.__posts__:
            self.__posts__ = list(BlogPost.query().order(-BlogPost.timestamp))
            self._populate_memcache()
            self._populate_search_index()

    @property
    def posts(self):
        return self.__posts__

    def __len__(self):
        return len(self.__posts__)

    def __iter__(self):
        return (post for post in self.__posts__)

    def __getitem__(self, post_idx):
        return self.__posts__[post_idx]

    def __contains__(self, post_key):
        if self.__posts__:
            for post in self.__posts__:
                if post.key == post_key:
                    return True
        return False

    def _populate_memcache(self):
        """populate memcache
        use key as post plus post.id"""
        logging.info('cache is empty creating index')
        if not memcache.add("POSTS_CACHE", self.__posts__):
            logging.error("Memcache set failed for posts")
            self.__posts__ = list(BlogPost.query().order(-BlogPost.timestamp))

    def _populate_search_index(self):
        try:
            for post in self.__posts__:
                category = post.category.get().category
                doc = create_document(post.key.id(), post.title, post.body,
                                      category, post.timestamp)
                search.Index(name=POSTS_INDEX).put(doc)

        except search.Error:
            logging.exception('Indexing failed')

    def _delete_memcache(self):
        logging.info('deleting cache for Posts')
        if not memcache.delete('POSTS_CACHE') != 2:  # delete not successful
            logging.error("Memcache delete failed for posts")

    def add(self, raw_title, raw_body, category_key, tags_ids, summary=None):
        post_key = BlogPost(title=raw_title,
                            body=raw_body,
                            category=category_key,
                            tags=tags_ids,
                            summary=summary).put()
        self.__posts__.append(BlogPost.get_by_id(post_key.id()))
        self.update()
        return post_key

    def get_tags(self):
        tags = []
        [tags.extend(post.get_tag_names()) for post in self.__posts__]
        return tags

    def get_other_tags(self, post_id):
        other_tags = []
        [other_tags.extend(post.get_tag_names()) for post in self.__posts__ if post.key.id() != post_id]
        return other_tags

    def update(self):
        self._delete_memcache()
        self._populate_memcache()

    def delete(self, post_key):
        post = post_key.get()
        [self.__posts__.pop(post_idx) for post_idx, post in enumerate(self.__posts__) if post.key == post_key]
        post.key.delete()
        self.update()

    def get_by_title(self, title):
        for post in self.__posts__:
            if post.title == title:
                post_f = post
                break
        try:
            return post_f
        except:
            logging.error("Post Not Found")
            raise LookupError


class Tags(BlogList):

    def __init__(self):
       # self.__tags__ = BlogList.retrieve_from_memcache("TAGS_CACHE")
       # if not self.__tags__:
        self.__tags__ = list(Tag.query())
        self._populate_memcache()

    def __contains__(self, raw_tag):
        if self.__tags__:
            for tag in self.__tags__:
                if tag == raw_tag:
                    return True
        return False

    def __iter__(self):
        return (tag.tag for tag in self.__tags__)

    def __len__(self):
        return len(self.__tags__)

    def _populate_memcache(self):
        logging.info("populating cache for tags {}")
        if not memcache.add("TAGS_CACHE", self.__tags__):
            logging.error("Memcache set failed for tags")

    def _delete_memcache(self):
        if not memcache.delete('TAGS_CACHE') != 2:
            logging.error("Memcache delete failed for tags")

    def add(self, new_tags):
        new_tags_keys = [Tag(tag=new_tag).put() for new_tag in new_tags]
        self.__tags__.extend([tag_key.get() for tag_key in new_tags_keys])
        self.update()
        return new_tags_keys

    def delete(self, tags_for_deletion):
        for tag_idx, tag in enumerate(self.__tags__):
            if tag.tag in tags_for_deletion:
                tag.key.delete()
                self.__tags__.pop(tag_idx)
                self.delete(tags_for_deletion)
        self.update()

    def get_keys(self, tags):
        return [tag.key for tag in self.__tags__ if tag.tag in tags]

    def get_names(self, keys=[]):
        return [tag.tag for tag in self.__tags__]


class Categories(BlogList):

    def __init__(self):
       # self.__categories__ = BlogList.retrieve_from_memcache("CATEGORIES_CACHE")
       # if not self.__categories__:
        self.__categories__ = list(Category.query())
        self._populate_memcache()

    def __contains__(self, raw_category):
        if self.__categories__:
            for category in self.__categories__:
                if category.category == raw_category:
                    return True
        return False

    def __iter__(self):
        return (category.category for category in self.__categories__)

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
        self.update()
        return category_key

    def get_key(self, raw_category):
        logging.info("{} {}".format(raw_category, len(self.__categories__)))
        return [category.key for category in self.__categories__ if category.category == raw_category][0]

    def delete(self, category_for_deletion):
        for cat_idx, category in enumerate(self.__categories__):
            if category.category == category_for_deletion:
                category.key.delete()
                self.__categories__.pop(cat_idx)
                self.delete(category_for_deletion)
        self.update()
