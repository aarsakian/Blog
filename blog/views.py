import logging, json
from blog import app
from models import Posts, Tags, Categories
from flask import render_template,request,jsonify,redirect,url_for, Markup, flash, session

from errors import InvalidUsage
from models import BlogPost,Tag,Category

from search import query_search_index, find_posts_from_index, delete_all_in_index

from google.appengine.api import users
from werkzeug.contrib.atom import AtomFeed

from functools import wraps

from jinja2.environment import Environment

from datetime import datetime

from forms import PostForm, AnswerRadioForm
from utils import datetimeformat, calculate_work_date_stats,  to_markdown


KEY="posts"
TAG="tags"
CATEGORY="categories"
CODEVERSION=":v0.7"

headerdict={"machine_learning":"Gaussian Graphical Models","programming":"Programming","about":"About Me"}

def fetch_everything_from_db():
    return Posts(), Tags(), Categories()


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




app.jinja_env.filters['datetimeformat'] = datetimeformat

app.jinja_env.filters['markdown'] = to_markdown




def boilercode(func):
    """accepts function as argument enhance with new vars"""
    @wraps(func)#propagate func attributes
    def wrapper_func(*args,**kwargs):
        posts, tags, categories = fetch_everything_from_db()
       # recentposts=posts[:3]


        passed_days, remaining_days = calculate_work_date_stats()

        return func(posts, tags, categories, passed_days,
                    remaining_days, *args, **kwargs)
    return wrapper_func





@app.route('/tags',methods=['GET'])
@boilercode
def view_all_tags(posts, tags, categories,  passed_days,
          remaining_days):

    site_updated = posts.site_last_updated()
    return render_template('tags.html',user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags.to_json(),
                           codeversion=CODEVERSION)



@app.route('/categories',methods=['GET'])
@boilercode
def view_all_categories(posts, tags, categories,  passed_days,
          remaining_days):

    site_updated = posts.site_last_updated()
    return render_template('categories.html',user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,categories=categories.to_json(),
                           codeversion=CODEVERSION)




@app.route('/searchresults',methods=['GET'])
@boilercode
def searchresults(posts, tags, categories,  passed_days,
          remaining_days):
    query_string = request.args.get('q')
    results = query_search_index(query_string)
    form = PostForm()
    if results:
        posts_ids = find_posts_from_index(results)
        posts.filter_matched(posts_ids)

    site_updated = posts.site_last_updated()

    return render_template('posts.html', user_status=users.is_current_user_admin(), siteupdated=site_updated, \
                           daysleft=remaining_days, dayspassed=passed_days,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION, form=form)


@app.route('/built with',methods=['GET'])
@app.route('/about',methods=['GET'])
@boilercode
def aboutpage(posts, tags, categories, passed_days,
                    remaining_days, postkey=None):

    requested_post = posts.get_by_title("about")

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))
    site_updated = posts.site_last_updated()

    return render_template('about.html',user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,Post=requested_post,
                           codeversion=CODEVERSION)


@app.route('/', methods=['GET'])
@app.route('/tags/<tag>')
@app.route('/categories/<category>')
@boilercode
def index(posts, tags, categories, passed_days,
          remaining_days, **kwargs):
    """
    general url routing for template usage
    """
    site_updated = posts.site_last_updated()

    if request.args.get('q'):
        return redirect(url_for('searchresults', q=request.args.get('q')))

    if "tag" in kwargs.keys():
        tag = kwargs["tag"]
        posts.filter_by_tag(tag)

    elif "category" in kwargs.keys():
        category = kwargs["category"]
        posts.filter_by_category(category)

    else:
        flash('This website uses Google Analytics to help analyse how users use the site.')
    form = PostForm()

    return render_template('posts.html', user_status=users.is_current_user_admin(), siteupdated=site_updated, \
                           daysleft=remaining_days, dayspassed=passed_days, tags=tags, categories=categories,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION,
                           form=form)


@app.route('/archives',methods=['GET'])
@boilercode
def archives(posts, tags, categories, passed_days,
                    remaining_days):
    """general url routing for template usage"""

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))

    form = PostForm()
    site_updated = posts.site_last_updated()
    flash('This website uses Google Analytics to help analyse how users use the site.')
    return render_template('archives.html',user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags,categories=categories,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION, form=form)



@app.route('/api/answers/<title>', methods=['POST','GET'])
def answers(title):
    posts = Posts()
    current_post = posts.get_by_title(title)

    if request.method == 'GET':  # all entitites


        return jsonify(current_post.strip_answers_jsoned())
    elif request.method == 'POST':
        raw_post = request.get_json()
        p_answer = raw_post["p_answer"]

        is_correct = raw_post["is_correct"]

        answers_form = AnswerRadioForm()
        answers_form.r_answers.data = p_answer
        answers_form.r_answers.choices = [(answer.p_answer, answer.p_answer) for answer in current_post.answers]


        if answers_form.validate_on_submit():

            return jsonify(result =current_post.is_answer_correct(p_answer, is_correct))
        else:
            return jsonify({})

@app.route('/api/posts',methods=['POST','GET'])
def main():
    if users.is_current_user_admin():
        if request.method=='GET':  #all entitites
            posts = Posts()


            return jsonify(posts.to_json())


        elif request.method == "POST":

            form = PostForm()
            if form.validate_on_submit():  #new entity
                posts = Posts()
                categories = Categories()
                tags = Tags()

                raw_post = request.get_json()
                raw_category = raw_post["category"]
                editing_tags = raw_post["tags"]
                raw_summary = raw_post["summary"]


                tag_keys = tags.update(editing_tags)
                category_key = categories.update(raw_category)

                post_id = posts.add(raw_title=raw_post["title"],
                            raw_body=raw_post["body"],
                            category_key=category_key,
                            tags_ids=tag_keys,
                            summary=raw_summary,
                            answers=raw_post["answers"]).id()
                post = BlogPost.get(post_id)
                return jsonify(post.to_json()) #  Needs check

    else:
        return jsonify({})


@app.route('/api/posts/<id>', methods=['GET'])
def get_post(id):
    if users.is_current_user_admin():
        asked_post = BlogPost.get(id)

        return jsonify(asked_post.to_json())  # dangerous
    else:
        return jsonify({})


@app.route('/api/posts/<id>', methods=['PUT'])
def edit_post(id):

    form = PostForm()
    if users.is_current_user_admin() and form.validate_on_submit():

        tags = Tags()

        categories = Categories()

        updating_post = BlogPost.get(int(id))

        title = request.json['title']
        body = request.json['body']
        raw_category = request.json['category']
        editing_tags = request.json['tags']
        raw_summary = request.json['summary']

        tags_keys = tags.update(editing_tags, updating_post)

        category_key = categories.update(raw_category, updating_post.category)

        updating_post.edit(title, body, datetime.now(), tags_keys,
                           category_key, raw_summary, answers=request.json['answers'])

        return jsonify(updating_post.to_json())  # dangerous


@app.route('/api/posts/<id>', methods=['DELETE'])
def delete_post(id):

    if users.is_current_user_admin():
        posts = Posts()

        tags = Tags()

        categories = Categories()

        updating_post = BlogPost.get(int(id))

        categories.delete(updating_post.category)

        posts.delete(updating_post.key)

        tags.update(updating_post.get_tag_names())

    return jsonify(msg="OK")



       



@app.route('/<category>/<year>/<month>/<title>', methods=['GET'])
def view_a_post(category, year, month, title):
    passed_days, remaining_days = calculate_work_date_stats()

    posts = Posts()

    answers_form = AnswerRadioForm()

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))

    current_post = posts.get_by_title(title)

    post_tag_names = current_post.get_tag_names()

    related_posts = posts.get_related_posts(current_post.id)

    category = current_post.category.get().category
    site_updated = posts.site_last_updated()
    flash('This website uses Google Analytics to help analyse how users use the site.')


    answers_form.r_answers.choices = [(answer.p_answer, answer.p_answer) for answer in current_post.answers
                                      if answer.p_answer != u'']

    return render_template('singlepost.html', user_status=users.is_current_user_admin(), siteupdated=site_updated, \
                                        daysleft=remaining_days, dayspassed=passed_days, RelatedPosts=related_posts, \
                                        Post=current_post.to_json(), posttagnames=post_tag_names, category=category,
                                        answers_field = answers_form)

@app.route('/edit',methods=['GET'])
@app.route('/edit/<postkey>',methods=['GET'])
def edit_a_post_view(postkey=None):

    form = PostForm()
    posts = Posts()
    passed_days, remaining_days = calculate_work_date_stats()
    site_updated = posts.site_last_updated()
    return render_template('posts.html',user_status=users.is_current_user_admin(),siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,
                           codeversion=CODEVERSION, form=form)





@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url, url=request.url_root)
    posts = Posts()
    feed = posts.add_to_feed(feed, request.url)

    return feed.get_response()


@app.route('/rebuild_index', methods=['GET'])
def rebuild_index():
    if users.is_current_user_admin():
        delete_all_in_index()
        posts = Posts()
        posts.rebuild_index()
        return redirect(url_for('index'))



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
        logging.error("error while searching {}".format(e))
        data = "something went wrong while searching"

    return jsonify(data=data)


@app.errorhandler(InvalidUsage)
@app.errorhandler(404)
def page_not_found(error):
    if isinstance(error, InvalidUsage):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code

    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')
