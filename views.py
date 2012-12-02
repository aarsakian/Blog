import logging
from blog import app
from models import BlogPost
from flask import render_template,request,jsonify,redirect,url_for, Markup
from google.appengine.ext import db
from google.appengine.api import memcache
from models import BlogPost,Tag,Category
try:
    from simplejson import loads,dumps
except ImportError:
    from json import loads,dumps
from google.appengine.api import users
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin
from datetime import datetime, timedelta, date
from math import ceil
import re



KEY="posts"
TAG="tags"
CATEGORY="categories"


headerdict={"machine_learning":"Gaussian Graphical Models","programming":"Programming","about":"About Me"}
months=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

class Action(object):
    def __init__(self):
        """load basic members using memcache"""
        self.posts_tags_db=[]
        self.catdict={}
      
        self.posts=memcache.get(KEY)
        if self.posts is None:
            self.posts = BlogPost.all().order("-timestamp")
            memcache.add(KEY,self.posts)
        self.tags=memcache.get(TAG)
        if self.tags is None:
            self.tags = Tag.all()
            memcache.add(TAG,self.tags)
        self.categories=memcache.get(CATEGORY)
        if self.categories is None:
            self.categories= Category.all()
            memcache.add(CATEGORY,self.categories)
        for post in self.posts:
            self.posts_tags_db.extend(post.tags)
            self.catdict[post.category.key()]=post.category.category
            
        logging.info(self.catdict)
       
      
                
    @staticmethod
    def deleteMemcache(self):
        memcache.delete(KEY)
        memcache.delete(CATEGORY)
        memcache.delete(TAG)
    @staticmethod
    def refetch(self):
        self.posts = BlogPost.all().order("-timestamp")
        memcache.add(KEY,self.posts)
        self.tags = Tag.all()
        memcache.add(TAG,self.tags)
        self.categories= Category.all()
        memcache.add(CATEGORY,self.categories)
        



class APost(Action):
    def __init__(self,title=None,body=None,date=None,category=None,posttags=None,id=None):
        logging.info([title,body,date,category,posttags,id])
        Action.__init__(self)
        if id==None:
           
            self.title=title
            self.body=body
            self.date=date
            self.postcategory=category
            self.posttags=posttags
            
        elif title==None:
            self.obj = BlogPost.get_by_id(int(id))
            self.id = self.obj.key().id()
            self.post_tags_keys = self.obj.tags
            
        else:
            self.obj = BlogPost.get_by_id(int(id))
            self.id = self.obj.key().id()
            self.post_tags_keys = self.obj.tags
            self.title=title
            self.body=body
            self.date=date
            self.postcategory=category
            self.posttags=posttags
    def delete(self):
        """delete a post"""
        restTags=list(set(self.posts_tags_db)^set(self.post_tags_keys))
        logging.info(restTags)
        [db.get(tagkey).delete() for tagkey in    self.post_tags_keys  if tagkey not in restTags]
             #delete the tag if it does not exists in rest posts
        self.obj.delete()
        self.deleteMemcache(self)
        self.refetch(self)
    
    def update(self):
        """updates a post"""
        
        #for catobj in self.categories:
        #    logging.info([catobj.key(),catobj.category,catkeys])
        #    if catobj.category==self.postcatkey:#AN OLD CATEGORY
        #        catkey=catobj.key()
        #    elif catobj.key() not in self.catkeys:#not used category
        #        catobj.delete()
        #    else:
        #        logging.info(catobj.key().id())
                #newcatobj=Category()
                #newcatobj.category=category
                #newcatobj.put()
                #catkey=newcatobj.key()
             
      
        post_tagsdb_values=[]
        post_tagsdb_keys=[]
        existingTags=[]
        existingTagskeys=[]
        tagsleft=[]
     
       #find the existing tags of the post
        for tagkey in self.posts_tags_db:
            if tagkey not in self.post_tags_keys:
                try:
                    tagsleft.append(Tag.get_by_id(tagkey.id()).tag)
                except AttributeError:#ops a post without a tag
                    continue
            existingTagskeys.append(tagkey)
            existingTags.append(db.get(tagkey).tag) #existing Tags
          
     
        
        for tagkey in self.post_tags_keys:post_tagsdb_values.append(db.get(tagkey).tag)#previous Tags of the post
        
         
        logging.info([self.posttags,type(self.posttags),type(post_tagsdb_values),post_tagsdb_values])  
        unchangedtags=[]
        returnedTags=[]
        logging.info(['posttags',self.posttags,post_tagsdb_values])
        if post_tagsdb_values:#post does have tags
            logging.info(post_tagsdb_values)
            unchangedtags=set(self.posttags) & set( post_tagsdb_values)#changes tags added or removed
            newtags=set(self.posttags) ^ unchangedtags#new tags for this post
            oldtags=list(set(post_tagsdb_values)^unchangedtags)
            logging.info(["new",newtags,"old",oldtags,"unchanged",unchangedtags,list(unchangedtags)])
  
            if list(unchangedtags):
                unchangedtags=list(unchangedtags)
                for tag in unchangedtags:
                    tagid=db.get(existingTagskeys[existingTags.index(tag)]).key().id()
                    returnedTags.append({"tag":tag,"tagid":tagid})
            else:unchangedtags=[]
            i=0
            logging.info(['Tags from other posts',existingTags])
            for tag in oldtags:#tags to be removed
                
                tag_key= existingTagskeys[existingTags.index(tag)]
                if tag not in  tagsleft:#delete not used tags
                    tagobj=db.get(tag_key)
                    logging.info(["deleting",tag,tagobj]) 
                    tagobj.delete()
                pos=post_tagsdb_values.index(tag)
            
          
                self.obj.tags.pop(pos-i)
          
                i+=1
        elif  self.posttags[0]!='':#new tags do exist

            logging.info(self.posttags)
            newtags=set(self.posttags)#does not have tags

        else:newtags=[]
       
     
     
            
        if newtags:
            for tag in list(newtags):#add new tag and update Post
                logging.info(tag)
                if tag not in existingTags:   
                    tagobj=Tag()
                    tagobj.tag=tag
                    tagid=tagobj.put().id()
                    returnedTags.append({"tag":tag,"tagid":tagid})
                    
                else:
                   tag_key= existingTagskeys[existingTags.index(tag)]
                   tagobj=Tag.get(tag_key)
                   returnedTags.append({"tag":tagobj.tag,"tagid":tagobj.key().id()})           
                self.obj.tags.append(tagobj.key())
        if isinstance(self.postcategory,list):self.postcategory=self.postcategory[0]
        #logging.info([self.catdict.values().index(self.postcategory[0])])
        self.obj.title=self.title
        self.obj.body=self.body   
        self.obj.category=self.catdict.keys()[self.catdict.values().index(self.postcategory)]
        self.obj.updated=datetime.now()
        self.obj.put()
      
        tags=[]
        [tags.append({"tag":db.get(key).tag,"tagid":db.get(key).key().id()}) for key in self.obj.tags]
          
        data=[]
        updated=str(self.obj.updated.day)+" "+str(months[self.obj.updated.month])+" "+str(self.obj.updated.year)
        dateposted=str(self.obj.timestamp.day)+" "+str(months[self.obj.timestamp.month])+" "+str(self.obj.timestamp.year)    
        data.append({"title":self.obj.title,"body":self.obj.body,"category":db.get(self.obj.category.key()).category,
                         "catid": db.get(self.obj.category.key()).key().id(),"id":str(self.obj.key().id()),\
             "tags":tags,"date":dateposted,"updated":updated})
        self.deleteMemcache(self)
        self.refetch(self)
        return(data,returnedTags)
    
        
    def submitApost(self):
        returnedTags=[]
   
        def Tagupdate (tag):
            #logging.info(self.tags.filter('tag',tag).count())
            if  tag!="" and self.tags.filter('tag',tag).count()==0:#tag does not exist
                return(Tag(tag=tag).put())
            else:
                return(self.tags.filter('tag',tag)[0].key())#otherwise find its key
            
        posttagkeys=[]
       
        if not self.tags:#Tags are empty therefore insert new tags
            posttagkeys=[Tag(tag=tag).put() for tag in self.posttags  if tag!=""]
        elif self.posttags[0]!="": posttagkeys=map(Tagupdate ,self.posttags)
        for key in posttagkeys:
            obj=db.get(key)
            returnedTags.append({"tag":obj.tag,"tagid":obj.key().id()})  
        catnames=[]
        catkeys=[]
        if self.categories:   #categories exist make list of them 
            [catnames.append(catobj.category) for catobj in self.categories]
            [catkeys.append(catobj.key()) for catobj in self.categories]
            catobjs=dict(zip(catnames,catkeys))
            if  self.postcategory in catobjs.keys():catkey=catobjs[self.postcategory]
            else:#this post has a new category
                newcatobj=Category()
                newcatobj.category=self.postcategory 
                newcatobj.put()
                catkey=newcatobj.key()
        else:
            newcatobj=Category()
            newcatobj.category=self.postcategory
            newcatobj.put()
            catkey=newcatobj.key()
     
              
        
        post=BlogPost()
        post.title=self.title
        post.body=self.body
        post.tags=posttagkeys
        post.category=catkey
        post.put()
       
        self.deleteMemcache(self)
        self.refetch(self)
        return(post.key(),returnedTags)
      
   

@app.route('/login')
def login():
    user = users.get_current_user()
    if user is None:
      
        return redirect(users.create_login_url())
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    user = users.get_current_user()
    if user is not None:
      
        return redirect(users.create_logout_url(dest_url=request.url))
    else:
        return redirect(url_for('index'))
        
@app.route('/<entity>/user',methods=['GET'])
@app.route('/user',methods=['GET'])
def findUser(entity=None):
    logging.info( users.is_current_user_admin())
 
    return jsonify(user_status=users.is_current_user_admin())

@app.route('/about',methods=['GET'])
def aboutpage():
    if 'posts' not in globals():
        global posts
    if 'categories' not in globals():
        global categories
    if 'tags' not in globals():
        global tags
    posts=memcache.get(KEY)
    tags=memcache.get(TAG)
    categories=memcache.get(CATEGORY)
  
    if not posts:
        logging.info("INDEX")
        posts = BlogPost.all().order("-timestamp").fetch(20)
        memcache.add(KEY,posts)
    if not tags:
        tags = Tag.all().fetch(20)
        memcache.add(TAG,tags)
    if not categories:
        categories= Category.all().fetch(20)
        memcache.add(CATEGORY,categories)
    try:
        post=posts[0]
        siteupdated=str(post.updated.day)+" "+months[post.updated.month]+" "+str(post.updated.year)
    except IndexError as e:
        siteupdated="Out of range"
    #tags=[]
    
    for post in posts:   logging.info([post.title])
    pattern = re.compile("About")
 

    Post=[postobj for postobj in posts if pattern.search(postobj.title)][0]
    ts=ceil(2.0/3.0*8*365)%365
    dayspassed=date.today()-date(2012,3,2)
    daysleft=int(ceil(2.0/3.0*8*365))-dayspassed.days
    tz=date(2012,3,2)+timedelta(daysleft)
    return render_template('about.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=daysleft,finaldate=tz,dayspassed=dayspassed.days,tags=tags,categories=categories,\
                           Post=Post)
    
    

    
@app.route('/categories',methods=['GET'])
@app.route('/tags',methods=['GET'])
@app.route('/',methods=['GET'])
def index(category=None):
    """general url routing for template usage"""
    if 'posts' not in globals():
        global posts
    if 'categories' not in globals():
        global categories
    if 'tags' not in globals():
        global tags
    posts=memcache.get(KEY)
    tags=memcache.get(TAG)
    categories=memcache.get(CATEGORY)
  
    if not posts:
        logging.info("INDEX")
        posts = BlogPost.all().order("-timestamp").fetch(20)
        memcache.add(KEY,posts)
    if not tags:
        tags = Tag.all().fetch(20)
        memcache.add(TAG,tags)
    if not categories:
        categories= Category.all().fetch(20)
        memcache.add(CATEGORY,categories)

    #[tags.append({"tag":obj.tag,"tagid":obj.key().id()}) for obj in Tag.all()]
   
    try:
        post=posts[0]
        siteupdated=str(post.updated.day)+" "+months[post.updated.month]+" "+str(post.updated.year)
    except IndexError as e:
        siteupdated="Out of range"
    #tags=[]
    
    #[tags.append(post.tags) for post in posts if post.tags not in tags]
  
    ts=ceil(2.0/3.0*8*365)%365
    dayspassed=date.today()-date(2012,3,2)
    daysleft=int(ceil(2.0/3.0*8*365))-dayspassed.days
    tz=date(2012,3,2)+timedelta(daysleft)
    return render_template('GGM.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=daysleft,finaldate=tz,dayspassed=dayspassed.days,tags=tags,categories=categories)
@app.route('/posts/about/<id>',methods=['PUT'])
@app.route('/posts/about',methods=['GET'])
def about(id=None):
    if 'posts' not in globals():
        global posts
    from models import Tag
    posts=memcache.get(KEY)
    tags=memcache.get(TAG)  
    categories=memcache.get(CATEGORY)
   
    data=[]
    if not posts:
      
        posts = BlogPost.all().order("-timestamp").fetch(20)
        memcache.add(KEY,posts)

  
    Posts=[]
    
    if request.method=="GET":
        pattern=re.compile("About")
        post=[post for post in posts if  pattern.search(post.title)][0]
       
           
            #tags=[]
            #
            #post.catname=[categoryobj.category for categoryobj in categories if categoryobj.key()==post.category.key()]
            #
        
        updated=str(post.updated.day)+" "+str(months[post.updated.month])+" "+str(post.updated.year)
        dateposted=str(post.timestamp.day)+" "+str(months[post.timestamp.month])+" "+str(post.timestamp.year)
        data.append({"title":post.title,"body":post.body,"category":"","id":str(post.key().id()),\
           "tags":"","date":dateposted,"updated":updated})
         
    
          
        return  jsonify(msg="OK",posts=data,type="about")
    elif users.is_current_user_admin() and request.method=="PUT":
        for post in posts:
            logging.info(post.key().id())
        [Posts.append(post) for post in posts if post.key().id()==int(id)]
        title=request.json['title']
        body=request.json['body']
        date=request.json['date']
        obj=Posts[0]
       
        obj.title=title
        obj.body=body
      
       
        #for catobj in categories:
        #    logging.info(["NOT IN",postcatkeys,catobj.key(),catobj.key() not in postcatkeys])
        
       
        obj.updated=datetime.now()
        post_tagsdb_values=[]
        post_tagsdb_keys=[]
        existingTags=[]
        existingTagskeys=[]
        tagsleft=[]
       
     
        obj.put()
        memcache.delete(KEY)
        posts = BlogPost.all()
      
        memcache.add(KEY,posts)
        
       
        data=[]
        updated=str(obj.updated.day)+" "+str(months[obj.updated.month])+" "+str(obj.updated.year)
        dateposted=str(obj.timestamp.day)+" "+str(months[obj.timestamp.month])+" "+str(obj.timestamp.year)    
        data.append({"title":obj.title,"body":obj.body,"category":db.get(obj.category.key()).category,
                         "catid": "","id":str(obj.key().id()),\
             "tags":"","date":dateposted,"updated":updated})
        logging.info(data)
        return jsonify(msg="OK",posts=data)
        
@app.route('/posts/tags')
@app.route('/tags/<tag>',methods=['GET','POST'])
@app.route('/tags/<tag>/<id>',methods=['DELETE','PUT'])
def getTag(tag=None,id=None):
    if 'posts' not in globals():
        global posts
    from models import Tag
    posts=memcache.get(KEY)
    tags=memcache.get(TAG)  
    categories=memcache.get(CATEGORY)
   
    data=[]
    if not posts:
      
        posts = BlogPost.all().order("-timestamp").fetch(20)
        memcache.add(KEY,posts)

    if not tags:
        tags = Tag.all().fetch(20)
        memcache.add(TAG,tags)
    

    if users.is_current_user_admin() and request.method=="DELETE":
     
        apost=APost(id=id)
        apost.delete()
        return jsonify(msg="OK")
    
    elif users.is_current_user_admin() and request.method=="PUT":
        title=request.json['title']
        body=request.json['body']
        date=request.json['date']
        category=request.json['category']
        posttags=request.json['tags']
        apost=APost(title,body,date,category,posttags,id)
        (data,returnedTags)=apost.update()
        return jsonify(msg="OK",tags=returnedTags,posts=data)
        
    if tag!=None:
        tagkey=[tagobj.key() for tagobj in tags if tagobj.tag==tag]
        if tagkey:tagkey=tagkey[0]
        if request.method=="GET":
            Posts=[]
            [Posts.append(post) for post in posts if tagkey in post.tags]
            logging.info(posts)
            for post in Posts:
                tags=[]
                [tags.append({"tag":db.get(key).tag,"tagid":db.get(key).key().id()}) for key in post.tags]
                post.catname=[categoryobj.category for categoryobj in categories if categoryobj.key()==post.category.key()]

             
                updated=str(post.updated.day)+" "+str(months[post.updated.month])+" "+str(post.updated.year)
                dateposted=str(post.timestamp.day)+" "+str(months[post.timestamp.month])+" "+str(post.timestamp.year)
                data.append({"title":post.title,"body":post.body,"category":post.catname,"id":str(post.key().id()),\
                    "tags":tags,"date":dateposted,"updated":updated})
                    #[postTagids.append(int(key.id())) for key in post.tags]
                    #logging.info(postTagids)
                    #if tagid  in postTagids:
                    #    Tag.get_by_id(tagid).key()
                    #    [tags.append({"tag":db.get(key).tag,"tagid":db.get(key).key().id()}) for key in post.tags]
                    #    data.append({"title":post.title,"body":post.body,"category":post.category,"id":str(post.key().id()),\
                    #    "tags":tags,"date":str(post.timestamp)[:-15]})
                    #    logging.info(tags)
            
    
               
            return  jsonify(msg="OK",posts=data,type="tag")
     
            
    else:  
        tagss=[] 
        [tagss.append([Tag.tag,Tag.key().id()]) for Tag in tags]
        tags=map(lambda tag:{"tag":tag[0],"id":tag[1]} ,tagss)
     
      
  
        return jsonify(msg="OK",tags=tags,header="My Tags used",type="tags")

@app.route('/categories/<catname>/<id>',methods=['DELETE','PUT'])
@app.route('/categories/<catname>',methods=['GET','POST'])
def catposts(catname,id=None):
    posts=memcache.get(KEY)
    tags=memcache.get(TAG)  
    categories=memcache.get(CATEGORY)
  
    data=[]
    if not posts:
      
        posts = BlogPost.all().order("-timestamp").fetch(20)
        memcache.add(KEY,posts)

    if not tags:
        tags = Tag.all().fetch(20)
        memcache.add(TAG,tags)
    if not categories:
        categories= Category.all().fetch(20)
        memcache.add(CATEGORY,categories)
    
    if request.method=="GET":    
        catkey=[categoryobj.key() for categoryobj in categories if categoryobj.category==catname][0]
        #logging.info([catkey,len(categories)])
    
           
        Posts=[]
        [Posts.append(post) for post in posts if catkey ==post.category.key()]
        logging.info([len(Posts)])
      
        for post in Posts:
            tags=[]
            [tags.append({"tag":db.get(key).tag,"tagid":db.get(key).key().id()}) for key in post.tags]
            post.catname=catname
    
     
            updated=str(post.updated.day)+" "+str(months[post.updated.month])+" "+str(post.updated.year)
            dateposted=str(post.timestamp.day)+" "+str(months[post.timestamp.month])+" "+str(post.timestamp.year)
            data.append({"title":post.title,"body":post.body,"category":post.catname,"id":str(post.key().id()),\
               "tags":tags,"date":dateposted,"updated":updated})
                        #[postTagids.append(int(key.id())) for key in post.tags]
                        #logging.info(postTagids)
                        #if tagid  in postTagids:
                        #    Tag.get_by_id(tagid).key()
                        #    [tags.append({"tag":db.get(key).tag,"tagid":db.get(key).key().id()}) for key in post.tags]
                        #    data.append({"title":post.title,"body":post.body,"category":post.category,"id":str(post.key().id()),\
                        #    "tags":tags,"date":str(post.timestamp)[:-15]})
                        #    logging.info(tags)
                
        
                   
        return  jsonify(msg="OK",posts=data,type="category")
    if users.is_current_user_admin() and request.method=="POST":#new entity
        title=request.json['title']
        body=request.json['body']
        date=request.json['date']
        category=request.json['category']
        if isinstance(request.json['tags'],list):
            tagspost=request.json['tags']
            logging.info(type(tagspost))
        apost=APost(title,body,date,category,tagspost)
        (id,tags)=apost.submitApost()
        return jsonify(msg="OK",id=id.id(),tags=tags)
        
    if users.is_current_user_admin() and request.method=="DELETE":
     
        apost=APost(id=id)
        apost.delete()
        return jsonify(msg="OK")
    
    elif users.is_current_user_admin() and request.method=="PUT":
        title=request.json['title']
        body=request.json['body']
        date=request.json['date']
        category=request.json['category']
        posttags=request.json['tags']
        apost=APost(title,body,date,category,posttags,id)
        (data,returnedTags)=apost.update()
       
            
       
        return jsonify(msg="OK",tags=returnedTags,posts=data)
        
        
@app.route('/posts',methods=['POST','GET'])#all entitites
def main():    
    posts=memcache.get(KEY)
    tags=memcache.get(TAG)
    categories=memcache.get(CATEGORY)
    logging.info(request.args)
    if not posts:
      
        posts = BlogPost.all().order("-timestamp").fetch(20)
        memcache.add(KEY,posts)

    if not tags:
        tags = Tag.all().fetch(20)
        memcache.add(TAG,tags)
    if not categories:
        categories= Category.all().fetch(20)
        memcache.add(CATEGORY,categories)
    if request.method=='GET':
        data=[]
        for post in posts:
            if post.title!='About':
                tags=[]
                [tags.append({"tag":db.get(key).tag,"tagid":db.get(key).key().id()}) for key in post.tags]
          
                updated=str(post.updated.day)+" "+str(months[post.updated.month])+" "+str(post.updated.year)
                dateposted=str(post.timestamp.day)+" "+str(months[post.timestamp.month])+" "+str(post.timestamp.year)
                data.append({"title":post.title,"body":post.body,"category":db.get(post.category.key()).category,
                             "catid": db.get(post.category.key()).key().id(),"id":str(post.key().id()),\
                 "tags":tags,"date":dateposted,"updated":updated})
        if posts: return jsonify(posts=data)
        else:return jsonify(posts=[])

    if users.is_current_user_admin() and request.method=="POST":#new entity
        title=request.json['title']
        body=request.json['body']
        date=request.json['date']
        category=request.json['category']
        if isinstance(request.json['tags'],list):
            tagspost=request.json['tags']
            logging.info(type(tagspost))
        apost=APost(title,body,date,category,tagspost)
        (id,tags)=apost.submitApost()
        return jsonify(msg="OK",id=id.id(),tags=tags)
      


@app.route('/posts/<id>',methods=['PUT','DELETE'])
def handleApost(id):
    posts=memcache.get(KEY)
    tags=memcache.get(TAG)
    categories=memcache.get(CATEGORY)
        
    if not posts:
      
        posts = BlogPost.all().order("-timestamp").fetch(20)
        memcache.add(KEY,posts)

    if not tags:
        tags = Tag.all().fetch(20)
        memcache.add(TAG,tags)
    if not categories:
        categories= Category.all().fetch(20)
        memcache.add(CATEGORY,categories)
        
    obj=BlogPost.get_by_id(int(id))
    tagkeys=obj.tags
    if users.is_current_user_admin() and request.method=="DELETE":
        apost=APost(id=id)
        apost.delete()
        return jsonify(msg="OK")
        
    elif  users.is_current_user_admin() and request.method=="PUT":
        title=request.json['title']
        body=request.json['body']
        date=request.json['date']
        category=request.json['category']
        posttags=request.json['tags']
        apost=APost(title,body,date,category,posttags,id)
        (data,returnedTags)=apost.update()
       
            
       
        return jsonify(msg="OK",tags=returnedTags,posts=data)
    

@app.route('/posts/categories', methods=['GET','POST'])#new entity
def action(id=None):
    if 'posts' not in globals():
        global posts
        
    posts=memcache.get(KEY)
    tags=memcache.get(TAG)
    categories=memcache.get(CATEGORY)
        
    if not posts:
      
        posts = BlogPost.all().order("-timestamp").fetch(20)
        memcache.add(KEY,posts)

    if not tags:
        tags = Tag.all().fetch(20)
        memcache.add(TAG,tags)
    if not categories:
        categories= Category.all().fetch(20)
        memcache.add(CATEGORY,categories)
    data=[]
    
   
#    if users.is_current_user_admin() and request.method=="POST":#new entity
#        title=request.json['title']
#        body=request.json['body']
#        date=request.json['date']
#        category=request.json['category']
#        if isinstance(request.json['tags'],list):
#            tags=request.json['tags']
#            logging.info(type(tags))
#        tagsdb=Tag.all()
#        returnedTags=[]
#        
#        def Tagupdate (tag):
#            logging.info(tagsdb.filter('tag',tag).count())
#            if  tag!="" and tagsdb.filter('tag',tag).count()==0:#tag does not exist
#                return(Tag(tag=tag).put())
#            else:
#                return(tagsdb.filter('tag',tag)[0].key())#otherwise find its key
#            
#        keys=[]
#        logging.info(tagsdb.count())
#        if not bool(tagsdb.count()):#Tags are empty 
#            keys=[Tag(tag=tag).put() for tag in tags  if tag!=""]
#          
#            logging.info(keys)
#        elif tags[0]!="": keys=map(Tagupdate ,tags)
#        for key in keys:
#            obj=db.get(key)
#            returnedTags.append({"tag":obj.tag,"tagid":obj.key().id()})  
#        
#        if categories:    
#            for catobj in categories:
#                if catobj.category!=category:
#                    logging.info(typeCategory())
#                    newcatobj=Category()
#                    newcatobj.category=category
#                    newcatobj.put()
#                    catkey=newcatobj.put().key()
#        else:
#            newcatobj=Category()
#            newcatobj.category=category
#            newcatobj.put()
#            catkey=newcatobj.put().key()
#                     
#     
#              
#        
#        post=BlogPost()
#        post.title=title
#        post.body=body
#        post.tags=keys
#        post.category=catkey
#        post.put()
#        memcache.delete(KEY)
#        memcache.delete(CATEGORY)
#        categories=Category.all()
#        posts = BlogPost.all()
#        memcache.add(KEY,posts)
#        return jsonify(msg="OK",id=post.key().id(),tags=returnedTags)
#   
    if request.method=='GET':
      
       # posts = BlogPost.all()
       # posts.order("-timestamp")

    
           # if category=="categories":
                Categories=[] 
                [Categories.append([categoryobj.category,categoryobj.key().id()]) for categoryobj in categories]
                Categories=map(lambda category:{"category":category[0],"catid":category[1]} ,Categories)
                logging.info(Categories)
      
  
                return jsonify(msg="OK",categories=Categories,header="Categories",type="categories")
            #
            #elif category!="about":
            #    if id==None:#get a category
            #        postss=[]
            #        [postss.append(post) for post in posts if post.category ==category]
            #        logging.info(postss)
            #        for post in postss:
            #            tags=[]
            #            [tags.append({"tag":db.get(key).tag,"tagid":db.get(key).key().id()}) for key in post.tags]
            #         
            #            updated=str(post.updated.day)+" "+str(months[post.updated.month])+" "+str(post.updated.year)
            #            dateposted=str(post.timestamp.day)+" "+str(months[post.timestamp.month])+" "+str(post.timestamp.year)
            #            data.append({"title":post.title,"body":post.body,"category":post.category,"id":str(post.key().id()),\
            #                "tags":tags,"date":dateposted,"updated":updated})
            #    else:#get a post with id
            #        post=BlogPost.get_by_id(int(id))
            #        tags=[]
            #        [tags.append({"tag":db.get(key).tag,"tagid":db.get(key).key().id()}) for key in post.tags]
            #        updated=str(post.updated.day)+" "+str(months[post.updated.month])+" "+str(post.updated.year)
            #        dateposted=str(post.timestamp.day)+" "+str(months[post.timestamp.month])+" "+str(post.timestamp.year)
            #        data.append({"title":post.title,"body":post.body,"category":category,"id":str(post.key().id()),\
            #        "tags":tags,"date":dateposted,"updated":updated})
            #
            #
            #else:
            #    about=BlogPost.all().filter('category =','about')[0]
            #    updated=str(about.updated.day)+" "+str(months[about.updated.month])+" "+str(about.updated.year)
            #    data.append({"title":about.title,"body":about.body,"category":about.category,"id":str(about.key().id()),
            #                 "updated":updated})
       
    
            
          
 
    
        #data=dumps(data)
        #if posts=="None":
        #    return jsonify(posts="None", header=headerdict[category])
        #else:
            #try:
            #    header=headerdict[category]
            #except KeyError:
            #    header="All Posts"
    #return jsonify(posts=data)
#       
#            
#    elif users.is_current_user_admin() and request.method=="PUT":
#        posttags=request.json['tags']
#      #  logging.info(request.json['category'])
#      #  logging.info(markdown.markdown(request.json['body'],safe_mode=True, enable_attributes=False))
#        obj=BlogPost.get_by_id(int(id))
#        obj.body=request.json['body']
#        obj.date=request.json['date']
#        obj.title=request.json['title']
#        postcategory=request.json['category']
#        catkey=[categoryobj.key() for categoryobj in categories if  postcategory==categoryobj.category]
#        logging.info(catkey)
#        if not catkey:#new category
#            logging.info(request.json['category'])
#            newcatobj=Category()
#            catobj=Category(category=postcategory)
#            catobj.put()
#            obj.category=catobj.key()
#        else:
#            obj.category=catkey[0]
#       
#        logging.info(obj.category)
#        obj.updated=datetime.now()
#        post_tagsdb_values=[]
#        post_tagsdb_keys=[]
#        existingTags=[]
#        existingTagskeys=[]
#        tagsleft=[]
#       
#        for post in posts:
#            for tagkey in post.tags:
#                if post.key()!=obj.key():
#                    try:
#                        tagsleft.append(Tag.get_by_id(tagkey.id()).tag)
#                    except AttributeError:#ops a post without a tag
#                        continue
#                existingTagskeys.append(Tag.get_by_id(tagkey.id()).key())
#                existingTags.append(Tag.get_by_id(tagkey.id()).tag) #existing Tags
#          
#     
#        
#        for tagkey in obj.tags:post_tagsdb_values.append(db.get(tagkey).tag)#previous Tags of the post
#        
#         
#  
#        unchangedtags=[]
#        logging.info(['posttags',posttags,post_tagsdb_values])
#        if post_tagsdb_values:#post does have tags
#            logging.info(post_tagsdb_values)
#            unchangedtags=set(posttags) & set( post_tagsdb_values)#changes tags added or removed
#            newtags=set(posttags) ^ unchangedtags#new tags for this post
#            oldtags=list(set(post_tagsdb_values)^unchangedtags)
#            logging.info(["new",newtags,"old",oldtags,"unchanged",unchangedtags])
#  
#            returnedTags=[]
#            for tag in unchangedtags:
#                tagid=db.get(existingTagskeys[existingTags.index(tag)]).key().id()
#                returnedTags.append({"tag":tag,"tagid":tagid})
#            
#            i=0
#            for tag in oldtags:#tags to be removed
#                
#                tag_key= existingTagskeys[existingTags.index(tag)]
#                if tag not in  tagsleft:#delete not used tags
#                   tagobj=Tag.get(tag_key)
#                   tagobj.delete()
#                pos=post_tagsdb_values.index(tag)
#            
#          
#                obj.tags.pop(pos-i)
#          
#                i+=1
#        else:
#            import ast
#            newtags=set(ast.literal_eval(str([tags])))#does not have tags
#            
#       
#     
#     
#    
#        #returnedTags=[]
#       
#            
#            
#            
#        logging.info( post_tagsdb_values)
#        for tag in list(newtags):#add new tag and update Post
#            logging.info(tag)
#            if tag not in existingTags:   
#                tagobj=Tag()
#                tagobj.tag=tag
#                tagid=tagobj.put().id()
#                returnedTags.append({"tag":tag,"tagid":tagid})
#                
#            else:
#               tag_key= existingTagskeys[existingTags.index(tag)]
#               tagobj=Tag.get(tag_key)
#               returnedTags.append({"tag":tagobj.tag,"tagid":tagobj.key().id()})           
#            obj.tags.append(tagobj.key())
#
#     
#        obj.put()
#        memcache.delete(KEY)
#        posts = BlogPost.all()
#        memcache.add(KEY,posts)
#        return jsonify(msg="OK",tags=returnedTags)
#        
#    elif users.is_current_user_admin() and request.method=="DELETE":
#     
#        obj=BlogPost.get_by_id(int(id))
#        tagkeys=obj.tags
#        post_tags_db=[]
#        
#        [post_tags_db.extend(post.tags) for post in posts]
#        restTags=list(set(post_tags_db)^set(tagkeys))
#        logging.info(restTags)
#        for tagkey in tagkeys:
#            if tagkey not in restTags:  db.get(tagkey).delete() #delete the tag if it does not exists in rest posts
#          
#        obj.delete() 
#        posts = BlogPost.all()
#        memcache.add(KEY,posts)
#    #    
#        return jsonify(msg="OK")
#    else:
#        return jsonify(msg="NOT ALLOWED")



@app.route('/<category>/<postTitle>',methods=['GET'])
def post(category,postTitle=None):
    if 'posts' not in globals():
        global posts
    posts=memcache.get(KEY)
    tags=memcache.get(TAG)  
    categories=memcache.get(CATEGORY)
    if not posts:
        logging.info("INDEX")
        posts = BlogPost.all().order("-timestamp").fetch(20)
        memcache.add(KEY,posts)

    if not tags:
        tags = Tag.all().fetch(20)
        memcache.add(TAG,tags)
    if not categories:
        categories= Category.all().fetch(20)
        memcache.add(CATEGORY,categories)
    logging.info([postTitle])
    if postTitle:
        Post=[postobj for postobj in posts if postobj.title==postTitle][0]
        tagnames=[]
        [tagnames.append(tag.tag) for tag in tags if tag.key() in Post.tags]
   
    else:
        for post in posts:
            (t,post.catname)=[(lambda post:posts.remove(post),category.category) for category in categories if not post.category.key()==category.key()][0]
    for category in categories:
    ##    
       logging.info([category.category,category.key(),Post.category.key()==category.key()])
    Post.catname=[category.category for category in categories if Post.category.key()==category.key()][0]
    
    
    try:
        post=posts[0]
        siteupdated=str(post.updated.day)+" "+months[post.updated.month]+" "+str(post.updated.year)
    except IndexError as e:
        siteupdated="Out of range"
    #tags=[]
    
    #[tags.append(post.tags) for post in posts if post.tags not in tags]
  
    ts=ceil(2.0/3.0*8*365)%365
    dayspassed=date.today()-date(2012,3,2)
    daysleft=int(ceil(2.0/3.0*8*365))-dayspassed.days
    tz=date(2012,3,2)+timedelta(daysleft)
    return render_template('GGM.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=daysleft,finaldate=tz,dayspassed=dayspassed.days,tags=tags,categories=categories,\
                           Post=Post,tagnames=tagnames)

def make_external(url):
    return urljoin(request.url_root, url)


@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url, url=request.url_root)
    #articles = BlogPost.all()
    pattern=re.compile("About")
    articles=memcache.get(KEY)
    articles.order("-timestamp")
    categories=memcache.get(CATEGORY)
    for article in articles:
        catname=[catobj.category for catobj in categories if catobj.key()==article.category.key()][0]
        feed.add(article.title, unicode(article.body),
                 content_type='html',
                 author='Armen',
                 url=make_external("#!/"+str(catname)+str(article.key().id())),
                 updated=article.updated,
                 published=article.timestamp)
    return feed.get_response()






