import logging, json
from blog import app
from models import Posts, Tags, Categories
from flask import render_template,request,jsonify,redirect,url_for, Markup

from google.appengine.api import memcache,search
from models import BlogPost,Tag,Category

from search import query_search_index, find_posts_from_index

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
from utils import find_modified_tags, find_tags_to_be_removed, find_tags_to_be_added, datetimeformat

KEY="posts"
TAG="tags"
CATEGORY="categories"
CODEVERSION=":v0.7"

headerdict={"machine_learning":"Gaussian Graphical Models","programming":"Programming","about":"About Me"}
months=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


@app.route('/login', methods=['GET'])
def login():
    """
    uses gae api to get information about current user
    if not connected redirected him to login page
    otherwise redirect him to index
    """
    user = users.get_current_user()
    if not user:
        return redirect(users.create_login_url('/edit'))
    elif users.is_current_user_admin(): # already logged
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
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
    return jsonify(user_status=users.is_current_user_admin())

    
    



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
            site_updated = find_update_of_site(posts[len(posts)-1])
        else:
            site_updated = 'NA'

        passed_days, remaining_days = calculate_work_date_stats()

        return func(posts, tags, categories, site_updated, passed_days,
                    remaining_days, *args, **kwargs)
    return wrapper_func





@app.route('/categories',methods=['GET'])
@app.route('/tags',methods=['GET'])
@boilercode
def tags(posts, tags, categories, siteupdated, passed_days,
                    remaining_days, postkey=None):
    form = PostForm()

    return render_template('posts.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags,categories=categories,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION, form=form)


   

@app.route('/searchresults',methods=['GET'])
@boilercode
def searchresults(posts, tags, categories, siteupdated, passed_days,
          remaining_days):
    query_string = request.args.get('q')
    results = query_search_index(query_string)
    form = PostForm()
    if results:
        posts_ids = find_posts_from_index(results)
        posts.filter_matched(posts_ids)

    return render_template('posts.html', user_status=users.is_current_user_admin(), siteupdated=siteupdated, \
                           daysleft=remaining_days, dayspassed=passed_days,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION, form=form)


@app.route('/built with',methods=['GET'])
@app.route('/about',methods=['GET'])
@boilercode
def aboutpage(posts, tags, categories, siteupdated, passed_days,
                    remaining_days, postkey=None):

    requested_post = posts.get_by_title("about")

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))    

    return render_template('about.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
                           daysleft=remaining_days,dayspassed=passed_days,Post=requested_post,
                           codeversion=CODEVERSION)


@app.route('/', methods=['GET'])
@app.route('/posts/tag/<tag>')
@app.route('/posts/category/<category>')
@boilercode
def index(posts, tags, categories, siteupdated, passed_days,
          remaining_days, **kwargs):
    """
    general url routing for template usage
    """

    if request.args.get('q'):
        return redirect(url_for('searchresults', q=request.args.get('q')))

    if "tag" in kwargs.keys():
        tag = kwargs["tag"]
        posts.filter_by_tag(tag)

    if "category" in kwargs.keys():
        category = kwargs["category"]
        posts.filter_by_category(category)

    form = PostForm()

    return render_template('posts.html', user_status=users.is_current_user_admin(), siteupdated=siteupdated, \
                           daysleft=remaining_days, dayspassed=passed_days, tags=tags, categories=categories,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION,
                           form=form)

@app.route('/archives',methods=['GET'])
@boilercode
def archives(posts, tags, categories, site_updated, passed_days,
                    remaining_days):
    """general url routing for template usage"""

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))

    form = PostForm()

    return render_template('posts.html',user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags,categories=categories,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION, form=form)



        





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
        
        
@app.route('/api/posts',methods=['POST','GET'])
def main():

    if request.method=='GET':  #all entitites
        posts = Posts()

        if posts:
            return jsonify(posts.to_json())
        else:
            return jsonify({})

    if users.is_current_user_admin() and request.method == "POST":  #new entity
        posts = Posts()
        categories = Categories()
        tags = Tags()

        raw_post = request.get_json()
        raw_category = raw_post["category"]
        editing_tags = raw_post["tags"]
        raw_summary = raw_post["summary"]

        existing_tags = posts.get_tags()
        new_tags_to_added = find_modified_tags(editing_tags, existing_tags)


        tag_keys = tags.add(new_tags_to_added)

        if raw_category not in categories:
            category_key = categories.add(raw_category)
        else:
            category_key = categories.get_key(raw_category)

        post_id = posts.add(raw_title=raw_post["title"],
                            raw_body=raw_post["body"],
                            category_key=category_key,
                            tags_ids=tag_keys,
                            summary=raw_summary).id()
        post = BlogPost.get(post_id)
        return jsonify(post.to_json()) #  Needs check


@app.route('/api/posts/<id>', methods=['GET'])
def get_post(id):


    asked_post = BlogPost.get(id)

    category_id = str(asked_post.category.id())

    post_tag_names = asked_post.get_tag_names()

    requested_post =  {"title": asked_post.title, "body": asked_post.body, "category":
                 asked_post.category.get().category,
              "catid":  category_id, "id": str(asked_post.key.id()), \
              "tags": post_tag_names, "date": asked_post.timestamp,"updated":asked_post.updated}

    return jsonify(requested_post)  # dangerous


@app.route('/api/posts/<id>', methods=['PUT'])
def edit_post(id):
    data = []

    if users.is_current_user_admin():
        posts = Posts()
        tags = Tags()
        categories = Categories()

        updating_post = BlogPost.get(int(id))

        title = request.json['title']
        body = request.json['body']

        raw_category = request.json['category']
        editing_tags = request.json['tags']

        remaining_tags = posts.get_other_tags(int(id))

        old_post_tags = updating_post.get_tag_names()

        non_modified_tags = set(editing_tags) & set(old_post_tags )

        tags_to_be_removed = find_tags_to_be_removed(old_post_tags, non_modified_tags, remaining_tags)
        tags_to_be_added = find_tags_to_be_added(editing_tags, non_modified_tags, remaining_tags)

        tags.add(tags_to_be_added)
        tags.delete(tags_to_be_removed)

        tags_keys = tags.get_keys(editing_tags)

        updating_post.edit(title, body, datetime.now(), tags_keys, categories.get_key(raw_category))

        post_tag_names = updating_post.get_tag_names()

        modified_post = {"title": updating_post.title, "body": updating_post.body, "category":
                 updating_post.category.get().category,
              "catid": str(categories.get_key(raw_category).id()).decode('utf8'), "id": str(updating_post.key.id()), \
              "tags": post_tag_names , "date": updating_post.timestamp ,"updated": updating_post.updated}

        return jsonify(modified_post)  # dangerous


@app.route('/api/posts/<id>', methods=['DELETE'])
def delete_post(id):

    if users.is_current_user_admin():
        posts = Posts()

        tags = Tags()

        categories = Categories()

        updating_post = BlogPost.get(int(id))

        remaining_tags = posts.get_other_tags(int(id))

        post_tags = updating_post.get_tag_names()

        non_used_tags = find_modified_tags(post_tags, remaining_tags)

        categories.delete(updating_post.category)

        posts.delete(updating_post.key)
        tags.delete(non_used_tags)

    return jsonify(msg="OK")

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
     #                tagid=db.get(existingTagskeys[existingTags.index(tag)]).key.id()
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
        #             returnedTags.append({"tag": tagobj.tag, "tagid": tagobj.key.id()})
        #         self.obj.tags.append(tagobj.key)
        # if isinstance(self.postcategory, list): self.postcategory = self.postcategory[0]
        # logging.info([self.catdict.values()])
        # self.obj.title = self.title
        # self.obj.body = self.body
        # self.obj.category = self.catdict.keys()[self.catdict.values().index(self.postcategory)]
        # self.obj.updated = datetime.now()
        # self.obj.put()
        # createIndex([self.obj])
        # tags = []
        # [tags.append({"tag": db.get(key).tag, "tagid": db.get(key).key.id()}) for key in self.obj.tags]
        #
        #data = []
        # updated = str(self.obj.updated.day) + " " + str(months[self.obj.updated.month]) + " " + str(
        #     self.obj.updated.year)
        # dateposted = str(self.obj.timestamp.day) + " " + str(months[self.obj.timestamp.month]) + " " + str(
        #     self.obj.timestamp.year)
        #logging.info("afte {}".format(editing_tags))

        # self.deleteMemcache(self)
        # self.refetch(self)
    #    return(data, raw_post_tags)

     #   (data,returnedTags)=apost.update()
       
            
       

    

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
                [Categories.append([categoryobj.category,categoryobj.key.id()]) for categoryobj in categories]
                Categories=map(lambda category:{"category":category[0],"catid":category[1]} ,Categories)
                logging.info(Categories)
      
  
                return jsonify(msg="OK",categories=Categories,header="Categories",type="categories")


#@app.route('/random',methods=['GET'])
@app.route('/<category>/<year>/<month>/<title>', methods=['GET'])
def view_a_post(category, year, month, title):
    passed_days, remaining_days = calculate_work_date_stats()

    posts = Posts()
    tags = Tags()
    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))

    # if title:
    #
    #     current_post = posts.get_by_title(title)
    #
    # else:
    #
    #     try:
    #         Post=posts[randint(0,action.nofposts-1)]
    #     except ValueError:
    #
    #         return render_template('singlepost.html',user_status=users.is_current_user_admin(),siteupdated=siteupdated,\
    #                        daysleft=daysleft,finaldate=tz,dayspassed=dayspassed.days,RelatedPosts=None,\
    #                        Post=None,codeversion=CODEVERSION)

    current_post = posts.get_by_title(title)

    post_tag_names = current_post.get_tag_names()

    other_posts_tags = posts.get_other_tags(current_post.key.id())

    related_posts = []

    for post in posts:
        if post.key != current_post.key:
            for tag in post.tags:
                if tag in other_posts_tags:
                    related_posts.append(post)

    category = post.category.get().category

    return render_template('singlepost.html', user_status=users.is_current_user_admin(), siteupdated='NA', \
                                        daysleft=remaining_days, dayspassed=passed_days, RelatedPosts=related_posts, \
                                        Post=current_post, posttagnames=post_tag_names, category=category)

@app.route('/edit',methods=['GET'])
@app.route('/edit/<postkey>',methods=['GET'])
def edit_a_post_view(postkey=None):

    form = PostForm()
    posts = Posts()
    passed_days, remaining_days = calculate_work_date_stats()
    site_updated = find_update_of_site(posts[len(posts) - 1])

    return render_template('posts.html',user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days, posts=posts.to_json(),
                           codeversion=CODEVERSION, form=form)



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
        catname=[catobj.category for catobj in categories if catobj.key==article.category.key][0]
        feed.add(article.title, unicode(article.body),
                 content_type='html',
                 author='Armen',
                 url=make_external("#!/"+str(catname)+str(article.key.id())),
                 updated=article.updated,
                 published=article.timestamp)
    return feed.get_response()


@app.route('/search',methods=['GET'])
def searchsite():

    query_string = request.args.get('query', '')
    try:

        results = query_search_index(query_string)
        posts_ids = find_posts_from_index(results)
        posts = Posts()
        posts.filter_matched(posts_ids)
        data = posts.to_json()
    except Exception as e:
        print "ERR",e
        data = "something went wrong while searching"

    return jsonify(data=data)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')
