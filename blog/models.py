from blog import app
from datetime import datetime
from google.appengine.ext import db
#

class Tag(db.Model):
    tag=db.StringProperty()
    
class Category(db.Model):
    category=db.StringProperty()
    

class BlogPost(db.Model):
    title = db.StringProperty()
    body = db.TextProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    updated=db.DateTimeProperty(auto_now_add=True)
    tags=db.ListProperty(db.Key)#one to many relation
    category = db.ReferenceProperty(Category,
                                   collection_name='category_posts')

 
 
#post=BlogPost()
#post.title='testr'
#post.body='everything about GGM'
#post.timestamp=datetime.now()
#post.put()
