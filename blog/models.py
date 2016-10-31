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
    def append(self, entity):
        """update list of posts and memcache"""
        logging.info("RECEVI ", entity, self.entities)

class Posts(BlogList):
    """list of posts"""
    def __init__(self):
        self.posts = []
        if not self._retrieve_from_memcache():
            self.posts = BlogPost.all().order('-timestamp')
            self._populate_memcache()
            self._populate_search_index()
        else:
            self.posts = self._retrieve_from_memcache()


    def _populate_memcache(self):
        """populate memcache
        use key as post plus post.id"""
        logging.info('cache is empty creating index')
        if not memcache.add("POSTS_CACHE", self.posts):
            logging.error("Memcache set failed for posts")

    def _retrieve_from_memcache(self):
        cached_posts = memcache.get("POSTS_CACHE")
        if not cached_posts:
            return []
        else:
            return list(cached_posts)


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

    def add(self, raw_title, raw_body, category_key, tags_ids):
        post_key = BlogPost(title=raw_title,
                              body=raw_body,
                              category=category_key,
                              tags=tags_ids).put()
        self.append(BlogPost.get_by_id(post_key.id()))

    def append(self, post):
        if self.posts:
            self._delete_memcache()
            self._populate_memcache()
            self.posts.append(post)

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
            self.tags = Tag.all().order('-tag')
            self._populate_memcache()
        else:
            self.tags =  self._retrieve_from_memcache()

    def _retrieve_from_memcache(self):
        cached_tags = memcache.get("TAGS_CACHE")
        if not cached_tags:
            return []
        else:
            return list(cached_tags)

    def _populate_memcache(self):
        if not memcache.add("TAGS_CACHE", self.tags):
            logging.error("Memcache set failed for tags")

    def _delete_memcache(self):
        if not memcache.delete('TAGS_CACHE') != 2:
            logging.error("Memcache delete failed for tags")

    def add(self, new_tag):
        tag_key = Tag(tag=new_tag).put()
        self.append(Tag.get_by_id(tag_key.id()))
        return tag_key

    def append(self, tag):
        if self.tags:
            self._delete_memcache()
            self._populate_memcache()
            self.tags.append(tag)

    def __getitem__(self, tag):
        return self.tags[tag]

    def __contains__(self, raw_tag):
        if self.tags:
            for tag in self.tags:

                if tag.tag == raw_tag:
                    logging.info(tag.tag==raw_tag)
                    return True
        return False


class Categories(BlogList):

    def __init__(self):
        self.categories = []
        if not self._retrieve_from_memcache():
            self.categories = Category.all().order('-category')
            self._populate_memcache()
        else:
            self.categories = self._retrieve_from_memcache()

    def _retrieve_from_memcache(self):
        cached_categories = memcache.get("CATEGORIES_CACHE")
        if not cached_categories:
            return []
        else:
            return list(cached_categories)

    def _populate_memcache(self):
        if not memcache.add("CATEGORIES_CACHE", self.categories):
            logging.error("Memcache set failed for categories")

    def _delete_memcache(self):
        if not memcache.delete('CATEGORIES_CACHE') != 2:
            logging.error("Memcache delete failed for categories")

    def add(self, raw_category):
        category_key = Category(category=raw_category).put()
        self.append(Category.get_by_id(category_key.id()))
        return category_key

    def append(self, category):
        if self.categories:
            self._delete_memcache()
            self._populate_memcache()
            self.categories.append(category)

    def __getitem__(self, raw_category):
        if self.categories:
            for category in self.categories:
                if category.category == raw_category:
                    logging.info(str(category))
                    return category
        return None

    @staticmethod
    def get_key(category):
        return memcache.get(category)



