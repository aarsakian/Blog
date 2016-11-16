import logging, json
from blog import app
from models import Posts, Tags, Categories
from flask import render_template,request,jsonify,redirect,url_for, Markup
from google.appengine.ext import db
from google.appengine.api import memcache,search
from models import BlogPost,Tag,Category
from datetime import date
from search import query_options,_INDEX_NAME,delete_document, delete_all_in_index
try:
    from simplejson import loads,dumps
except ImportError:
    from json import loads,dumps
from google.appengine.api import users
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin
from datetime import datetime, timedelta, date
from math import ceil
from functools import wraps
from re import compile
from jinja2.environment import Environment
from random import randint
from itertools import chain
from forms import PostForm

KEY="posts"
TAG="tags"
CATEGORY="categories"
CODEVERSION=":v0.65"

headerdict={"machine_learning":"Gaussian Graphical Models","programming":"Programming","about":"About Me"}
months=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

class Action(object):
    def __init__(self):
        """load basic members using memcache"""
        logging.info("initialized")
        self.posts_tags_db=[]
        self.catdict={}
        self.posts_tags_dict={}
        self.posts=memcache.get(KEY)

      

        if isinstance(self.posts,list):self.nofposts=len(self.posts)-2
        else:self.nofposts=self.posts.count()-2
        self.tags=memcache.get(TAG)
        if self.tags is None:
            self.tags = Tag.all()
            memcache.add(TAG,self.tags)
        self.categories=memcache.get(CATEGORY)
        if self.categories is None:
            self.categories= Category.all()
            memcache.add(CATEGORY,self.categories)

        for post in self.posts:
            logging.info(['posts',post.title])
            self.posts_tags_db.extend(post.tags)
            tags=[]
            for key in post.tags:tags.append(db.get(key).tag)
            self.posts_tags_dict[post.key()]=tags
            self.catdict[post.category.key()]=post.category.category
        logging.info(['catdict',self.catdict])
        self.tagnames=list(chain.from_iterable(self.posts_tags_dict.values()))
      
       
      
    
    
      
                
    @staticmethod
    def deleteMemcache(self):
        memcache.delete(KEY)
        memcache.delete(CATEGORY)
        memcache.delete(TAG)
    @staticmethod
    def refetch(self):
        self.posts =BlogPost.all().order('-timestamp')
        memcache.add(KEY,self.posts)
        self.tags = Tag.all()
        memcache.add(TAG,self.tags)
        self.categories= Category.all()
        memcache.add(CATEGORY,self.categories)
        createIndex(self.posts)
    
    def getall(self,catname=None,tagname=None):
        data=[]
 
        if catname:
            catkey=[categoryobj.key() for categoryobj in self.categories if categoryobj.category==catname][0]
            posts=[]
            [posts.append(post) for post in self.posts if catkey ==post.category.key()]
        #logging.info([catkey,len(categories)])
        elif tagname:
            logging.info(tagname)
            tagkey=[tagobj.key() for tagobj in self.tags if tagobj.tag==tagname]
            if tagkey:tagkey=tagkey[0]
            posts=[]
            [posts.append(post) for post in self.posts if tagkey in post.tags]
           
        else:posts=self.posts
        

        
        for post in posts:
           
            tags=[]
            [tags.append({"tag":db.get(key).tag,"tagid":db.get(key).key().id()}) for key in post.tags]
      
            updated=str(post.updated.day)+" "+str(months[post.updated.month])+" "+str(post.updated.year)
            dateposted=str(post.timestamp.day)+" "+str(months[post.timestamp.month])+" "+str(post.timestamp.year)
            data.append({"title":post.title,"body":post.body,"category":db.get(post.category.key()).category,
                         "catid": db.get(post.category.key()).key().id(),"id":str(post.key().id()),\
                        "tags":tags,"date":dateposted,"updated":updated})
        return(data)



class APost(Action):
    def __init__(self,title=None,body=None,date=None,category=None,posttags=None,id=None):

        Action.__init__(self)
        if id==None:
           
            self.title=title
            self.body=body
            self.date=date
            self.postcategory=category
            self.posttags=posttags
            
        elif title==None:
            self.obj =BlogPost.get_by_id(int(id))
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
            
    def retrieve(self):
        """retrieves a post"""
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
        return(data)
        
    def delete(self):
        """delete a post"""
        restTags=list(set(self.posts_tags_db)^set(self.post_tags_keys))
        logging.info(restTags)
        [db.get(tagkey).delete() for tagkey in    self.post_tags_keys  if tagkey not in restTags]
             #delete the tag if it does not exists in rest posts
        self.obj.delete()
        self.deleteMemcache(self)
        self.refetch(self)
        delete_document([str(self.obj.key())])
    
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
        
         
     #   logging.info([self.posttags,type(self.posttags),type(post_tagsdb_values),post_tagsdb_values])  
        unchangedtags=[]
        returnedTags=[]
      #  logging.info(['posttags',self.posttags,post_tagsdb_values])
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
        elif  self.posttags:#new tags do exist

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
        logging.info([self.catdict.values()])
        self.obj.title=self.title
        self.obj.body=self.body   
        self.obj.category=self.catdict.keys()[self.catdict.values().index(self.postcategory)]
        self.obj.updated=datetime.now()
        self.obj.put()
        createIndex([self.obj])
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
    """uses gae api to get information about current user
    if not connected redirected him to login page
    otherwise redirect him to index"""
    user = users.get_current_user()
    if not user:
        return redirect(users.create_login_url())
    else:
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """uses gae api to get information about current user
    if connected redirected him to logout page
    otherwise redirect him to index"""
    user = users.get_current_user()
    if user:
        return redirect(users.create_logout_url(dest_url=request.url))
    else:
        return redirect(url_for('index'))
        
@app.route('/<entity>/user',methods=['GET'])
@app.route('/user',methods=['GET'])
def findUser(entity=None):
    logging.info( users.is_current_user_admin())
 
    return jsonify(user_status=users.is_current_user_admin())

    
    

def datetimeformat(value, format='%H:%M / %A-%B-%Y'):
    return value.strftime(format)

environment = Environment()
app.jinja_env.filters['datetimeformat'] = datetimeformat


def fetch_everything_from_db():
    return Posts(), Tags(), Categories()


def calculate_work_date_stats():
    passed_days = (date.today()-date(2012, 3, 2)).days
    remaining_days = int(ceil(2.0/3.0*8*365))-passed_days
    return passed_days, remaining_days


def find_update_of_site(last_post):
    return str(last_post.updated.day)+" "+months[last_post.updated.month]+" "\
                       +str(last_post.updated.year)


def boilercode(func):
    """accepts function as argument enhance with new vars"""
    @wraps(func)#propagate func attributes
    def wrapper_func(*args,**kwargs):
        posts, tags, categories = fetch_everything_from_db()
       # recentposts=posts[:3]

        if posts:
            posts_json = posts.to_json()
            site_updated = find_update_of_site(posts[len(posts)-1])
        else:
            site_updated = 'NA'
            posts_json = []
        passed_days, remaining_days = calculate_work_date_stats()
        return func(posts_json, tags, categories, site_updated, passed_days,
                    remaining_days, *args, **kwargs)
    return wrapper_func




@app.route('/<postkey>/edit',methods=['GET'])
@app.route('/edit/<postkey>',methods=['GET'])
@app.route('/edit',methods=['GET'])
@app.route('/categories',methods=['GET'])
@app.route('/tags',methods=['GET'])
@boilercode
def tags(posts_json, tags, categories, siteupdated, passed_days,
                    remaining_days, postkey=None):
    form = PostForm()

    return render_template('main.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags,categories=categories,
                           posts=posts_json,
                           codeversion=CODEVERSION, form=form)


   

@app.route('/searchresults',methods=['GET'])
@boilercode
def searchresults(posts,tags,categories,action,siteupdated,daysleft,tz,dayspassed,data=None):
    query=request.args.get('q')
    logging.info(query)
    index = search.Index(name=_INDEX_NAME)

    posts=[]
    results=index.search(query)
    logging.info([query,results])
    if results:
        for scored_document in results:
            posts.append(db.get(scored_document.doc_id))
    else:posts=[]
       
    return render_template('index.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=daysleft,finaldate=tz,dayspassed=dayspassed.days,tags=tags,categories=categories,\
                           posts=posts,posts_tags_names=action.posts_tags_dict,codeversion=CODEVERSION)


@app.route('/built with',methods=['GET'])
@app.route('/about',methods=['GET'])
@boilercode
def aboutpage(posts,tags,categories,action,siteupdated,daysleft,tz,dayspassed,data=None):
    
    
    aboutpost=[p for p in posts if p.title.find("About")!=-1][0]

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))    
    
    
  
    return render_template('about.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=daysleft,finaldate=tz,dayspassed=dayspassed.days,Post=aboutpost,codeversion=CODEVERSION)


@app.route('/', methods=['GET'])
@boilercode
def index(posts_json, tags, categories, siteupdated, passed_days,
                    remaining_days):
    """general url routing for template usage"""


    logging.info("JSON{}".format(posts_json))

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))
    return render_template('index.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags,categories=categories,
                           posts=posts_json,
                           codeversion=CODEVERSION)

@app.route('/archives',methods=['GET'])
@boilercode
def archives(posts,tags,categories,action,siteupdated,daysleft,tz,dayspassed):
    """general url routing for template usage"""

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))
    return render_template('posts.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=daysleft,finaldate=tz,dayspassed=dayspassed.days,tags=tags,categories=categories,\
                           posts=posts,posts_tags_names=action.posts_tags_dict,codeversion=CODEVERSION)



        
@app.route('/posts/tags')
@app.route('/tags/<tag>',methods=['GET','POST'])
@app.route('/tags/<tag>/<id>',methods=['DELETE','PUT'])
def getTag(tag=None,id=None):
    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))
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
        if request.method=="GET":

            data=action.getall(tagname=tag)
            return  jsonify(msg="OK",posts=data,type="tag")
     
            
    else:  
        tagss=[]

        [tagss.append([Tag.tag,Tag.key().id()]) for Tag in a.tags]
        tags=map(lambda tag:{"tag":tag[0],"id":tag[1]} ,tagss)
     
      
  
        return jsonify(msg="OK",tags=tags,header="My Tags used",type="tags")

@app.route('/categories/<catname>/<id>',methods=['DELETE','PUT'])
@app.route('/categories/<catname>',methods=['GET','POST'])
def catposts(catname,id=None):



    if request.method=="GET":

        return  jsonify(msg="OK",posts=data,type="category")
        
    if users.is_current_user_admin() and request.method=="POST":#new entity
        title=request.json['title']
        body=request.json['body']
        date=request.json['date']
        category=request.json['category']
        if isinstance(request.json['tags'],list):
            tagspost=request.json['tags']

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
        
        
@app.route('/posts',methods=['POST','GET'])
def main():    


    if request.method=='GET':  #all entitites
        posts = Posts()

        if posts:

            return jsonify(posts=posts.to_json())
        else:
            return jsonify(posts=[])

    if users.is_current_user_admin() and request.method == "POST":  #new entity
        posts = Posts()
        categories = Categories()
        tags = Tags()
        logging.info("new post was submitted")
        raw_post = request.get_json()
        raw_category = raw_post["category"]
        raw_tags = raw_post["tags"]

        new_tags = [raw_tag for raw_tag in raw_tags if raw_tag not in tags]

        tag_keys = [tags.add(new_tag) for new_tag in new_tags if new_tags]

        if raw_category not in categories:
            category_key = categories.add(raw_category)
        else:
            category_key = categories.get_key(raw_category)

        post_id = posts.add(raw_title=raw_post["title"],
                              raw_body=raw_post["body"],
                              category_key=category_key,
                              tags_ids=tag_keys).id()

        return jsonify(msg="OK", id=str(post_id), tags=raw_tags) ##Needs check
      


@app.route('/posts/<id>', methods=['PUT','DELETE','GET'])
def handleApost(id):
    posts = Posts()
    tags = Tags()
    categories = Categories()

    tags_keys = []
    tags_already_existing = []




    # if not tags:
    #     tags = Tag.all().fetch(20)
    #     memcache.add(TAG,tags)
    # if not categories:
    #     categories= Category.all().fetch(20)
    #     memcache.add(CATEGORY,categories)
    #
    #
    # if request.method=="GET":
    #     apost=APost(id=id)
    #     data=apost.retrieve()
    #     return jsonify(msg="OK",posts=data)
    # elif users.is_current_user_admin() and request.method=="DELETE":
    #     apost=APost(id=id)
    #     apost.delete()
    #     return jsonify(msg="OK")
        
    if users.is_current_user_admin() and request.method=="PUT":
        title = request.json['title']
        body = request.json['body']

        raw_category = request.json['category']
        raw_post_tags = request.json['tags']

        updating_post = BlogPost.get_by_id(int(id))
        existing_post_tags = updating_post.get_tags()

        #potential new tags to be added
        unchanged_tags = set(existing_post_tags) & set(raw_post_tags)
        potential_new_tags = set(raw_post_tags) ^ unchanged_tags#new tags for this post
        potential_removed_tags = set(existing_post_tags) ^ unchanged_tags

        other_posts_tags = posts.get_other_tags(id)

        if potential_new_tags:

            new_tags = [potential_new_tag for potential_new_tag in
                        potential_new_tags if potential_new_tag not in tags and potential_new_tag != '']
            if new_tags:
                tags_keys = [tags.add(new_tag) for new_tag in new_tags if new_tags]
            tags_already_existing = set(potential_new_tags) & set(other_posts_tags)

        logging.info("potential removed tags {} potential "
                     "new_tags {} unchanged tags {} other post tags {} "
                     "raw post tags {}".format(potential_removed_tags, potential_new_tags,
                                                         unchanged_tags,other_posts_tags,raw_post_tags))
        if potential_removed_tags:
            to_be_removed_tags =  (potential_removed_tags ^ set(other_posts_tags))^potential_removed_tags
            logging.info(" SS {}".format(to_be_removed_tags))
            [tags.delete(tag) for tag in to_be_removed_tags]

        tags_keys.extend(tags.get_keys(unchanged_tags))
        if tags_already_existing:
            tags_keys.extend(tags.get_keys(tags_already_existing))
        logging.info("FINA {} {}".format(tags_keys ,tags.get_keys(unchanged_tags)))
        updating_post.title = title
        updating_post.body = body
        updating_post.category = categories.get_key(raw_category)
        updating_post.tags = tags_keys

     #   self.obj.category=self.catdict.keys()[self.catdict.values().index(self.postcategory)]
        updating_post.updated = datetime.now()
        updating_post.put()
        posts.update()



       #3 for tagkey in self.post_tags_keys:post_tagsdb_values.append(db.get(tagkey).tag)#previous Tags of the post


     # #   logging.info([self.posttags,type(self.posttags),type(post_tagsdb_values),post_tagsdb_values])
     #    unchangedtags=[]
     #    returnedTags=[]
     #  #  logging.info(['posttags',self.posttags,post_tagsdb_values])
     #    if post_tagsdb_values:#post does have tags
     #        logging.info(post_tagsdb_values)
     #        unchangedtags=set(self.posttags) & set( post_tagsdb_values)#changes tags added or removed
     #        newtags=set(self.posttags) ^ unchangedtags#new tags for this post
     #        oldtags=list(set(post_tagsdb_values)^unchangedtags)
     #        logging.info(["new",newtags,"old",oldtags,"unchanged",unchangedtags,list(unchangedtags)])
     #
     #        if list(unchangedtags):
     #            unchangedtags=list(unchangedtags)
     #            for tag in unchangedtags:
     #                tagid=db.get(existingTagskeys[existingTags.index(tag)]).key().id()
     #                returnedTags.append({"tag":tag,"tagid":tagid})
     #        else:unchangedtags=[]
     #        i=0
     #        logging.info(['Tags from other posts',existingTags])
     #        for tag in oldtags:#tags to be removed
     #
     #            tag_key= existingTagskeys[existingTags.index(tag)]
     #            if tag not in  tagsleft:#delete not used tags
     #                tagobj=db.get(tag_key)
     #                logging.info(["deleting",tag,tagobj])
     #                tagobj.delete()
     #            pos=post_tagsdb_values.index(tag)
     #
     #
     #            self.obj.tags.pop(pos-i)
     #
     #            i+=1
     #    elif  self.posttags:#new tags do exist
     #
     #        logging.info(self.posttags)
     #        newtags=set(self.posttags)#does not have tags
     #
     #    else:newtags=[]




        # if newtags:
        #     for tag in list(newtags):  # add new tag and update Post
        #         logging.info(tag)
        #         if tag not in existingTags:
        #             tagobj = Tag()
        #             tagobj.tag = tag
        #             tagid = tagobj.put().id()
        #             returnedTags.append({"tag": tag, "tagid": tagid})
        #
        #         else:
        #             tag_key = existingTagskeys[existingTags.index(tag)]
        #             tagobj = Tag.get(tag_key)
        #             returnedTags.append({"tag": tagobj.tag, "tagid": tagobj.key().id()})
        #         self.obj.tags.append(tagobj.key())
        # if isinstance(self.postcategory, list): self.postcategory = self.postcategory[0]
        # logging.info([self.catdict.values()])
        # self.obj.title = self.title
        # self.obj.body = self.body
        # self.obj.category = self.catdict.keys()[self.catdict.values().index(self.postcategory)]
        # self.obj.updated = datetime.now()
        # self.obj.put()
        # createIndex([self.obj])
        # tags = []
        # [tags.append({"tag": db.get(key).tag, "tagid": db.get(key).key().id()}) for key in self.obj.tags]
        #
        data = []
        # updated = str(self.obj.updated.day) + " " + str(months[self.obj.updated.month]) + " " + str(
        #     self.obj.updated.year)
        # dateposted = str(self.obj.timestamp.day) + " " + str(months[self.obj.timestamp.month]) + " " + str(
        #     self.obj.timestamp.year)
        logging.info("afte {}".format(raw_post_tags))
        data.append(
             {"title": updating_post.title, "body": updating_post.body, "category":
                 db.get(updating_post.category.key()).category,
              "catid": categories.get_key(raw_category).id(), "id": str(updating_post.key().id()), \
              "tags": raw_post_tags, "date": updating_post.timestamp ,"updated": updating_post.updated})
        # self.deleteMemcache(self)
        # self.refetch(self)
    #    return(data, raw_post_tags)

     #   (data,returnedTags)=apost.update()
       
            
       
        return jsonify(msg="OK",tags=raw_post_tags, posts=data)
    

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


@app.route('/random',methods=['GET'])
@app.route('/<category>/<year>/<month>/<postTitle>',methods=['GET'])
@boilercode
def post(posts,tags,categories,action,siteupdated,daysleft,tz,dayspassed,category=None,postTitle=None,year=None,month=None):

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))

    if postTitle:
       # posts=posts.filter('title =',postTitle)
   
      
        Post=[postobj for postobj in posts if postobj.title.replace(' ','')==postTitle.replace(' ','')][0]

       
        
       
       
               
        for category in categories:
    ##    
            logging.info([category.category,category.key(),Post.category.key()==category.key()])
            Post.catname=[category.category for category in categories if Post.category.key()==category.key()][0]
         
                
                
   
    else:
     
        try:
            Post=posts[randint(0,action.nofposts-1)]
        except ValueError:
             
            return render_template('singlepost.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=daysleft,finaldate=tz,dayspassed=dayspassed.days,RelatedPosts=None,\
                           Post=None,codeversion=CODEVERSION)

        #for post in posts:
        #    (t,post.catname)=[(lambda post:posts.remove(post),category.category) for category in categories if not post.category.key()==category.key()][0]
    Posttagnames=[]
    RelatedPosts=[]
    for tag in tags:
        if tag.key() in Post.tags:
            Posttagnames.append(tag.tag)
          
    
    for postkey,tagnames in action.posts_tags_dict.items():
        if postkey!=Post.key():
            [RelatedPosts.append(db.get(postkey)) for tag in Posttagnames if tag in tagnames]
                  
    
    return render_template('singlepost.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=daysleft,finaldate=tz,dayspassed=dayspassed.days,RelatedPosts=RelatedPosts,\
                           Post=Post, posttagnames= Posttagnames)

def make_external(url):
    return urljoin(request.url_root, url)


@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url, url=request.url_root)
    #articles = BlogPost.all()
    pattern=compile("About")
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


@app.route('/search',methods=['GET'])
def searchsite():
    data=[]
    query_string=request.args.get('query', '')
    try:
        query = search.Query(query_string=query_string, options=query_options)

        index = search.Index(name=_INDEX_NAME)

        results=index.search(query)


        if results:
            for scored_document in results:

                data.append({scored_document.fields[0].name:scored_document.fields[0].value,\
                             scored_document.fields[1].name:scored_document.fields[1].value,\
                             scored_document.fields[2].name:scored_document.fields[2].value,\
                             "year":scored_document.fields[3].value.year,\
                             "month":scored_document.fields[3].value.month})


        # process scored_document
    except search.Error:
        data.append('Search failed')

    return jsonify(data=data)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')