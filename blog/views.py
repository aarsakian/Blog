import logging, base64, io, os, requests
from urllib.parse import urlparse
from blog import app, csrf
from flask_login import login_user, login_required, logout_user, current_user
from .models import Posts, Tags, Categories, BlogPost, ViewImageHandler, User
from flask import render_template,request,jsonify,\
    redirect,url_for, flash, session, make_response, send_file, abort, escape
from werkzeug.utils import secure_filename
from .errors import InvalidUsage
import google.oauth2.id_token
import datetime
from functools import wraps


from .forms import PostForm, AnswerRadioForm
from .utils import datetimeformat, calculate_work_date_stats,  to_markdown, generate_uid_token, allowed_file



import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# The path to the client-secrets.json file obtained from the Google API
# Console. You must set this before running this application.
CLIENT_SECRETS_FILENAME = os.environ['GOOGLE_CLIENT_SECRETS']
# The OAuth 2.0 scopes that this application will ask the user for. In this
# case the application will ask for basic profile information.
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 
'https://www.googleapis.com/auth/userinfo.profile', 'openid']


KEY="posts"
TAG="tags"
CATEGORY="categories"
CODEVERSION=":v0.7"

headerdict={"machine_learning":"Gaussian Graphical Models","programming":"Programming","about":"About Me"}

MSG = 'This website uses Cookies and Google Analytics (GA) to help analyse how users use the site. ' \
      'By declining you opt out from the collection of anonymized data using GA services. ' \
      'By accepting you agree to the collection of anonymized data, no data is shared with third parties.'

REMAINING_ATTEMPTS = 1




@app.before_request
def redirect_nonwww():
    """Redirect non-www requests to www."""
    urlparts = urlparse(request.url)
    if urlparts.netloc == 'arsakian.com':
        urlparts_list = list(urlparts)
        urlparts_list[1] = 'www.arsakian.com'
        return redirect(urlunparse(urlparts_list), code=301)


#@app.before_request
# def accept_google_analytics():
#     app.jinja_env.globals['ga_accepted'] = False

#     if request.path not in (url_for('login'), url_for('logout'), url_for('edit_a_post_view')):
#         accept_google_analytics = request.cookies.get('ga_accepted')

#         if not accept_google_analytics and app.static_url_path not in request.path:

#             msgs = [msg for _, msg in session.get('_flashes', [])]
#             if MSG not in msgs:
#                 flash(MSG)
                
#         elif accept_google_analytics == 'False':
#             app.jinja_env.globals['ga_accepted'] = False

#         elif accept_google_analytics == 'True':
#             app.jinja_env.globals['ga_accepted'] = True


def fetch_everything_from_db():
    return Posts(), Tags(), Categories()


@app.before_request
def discover_anonymous_uid(*args):
    if request.path == url_for("answers", title=""):

        if not current_user.is_admin and not session.get('current_user_uid'):
            session['current_user_uid'] = generate_uid_token()



@app.route('/login', methods=['GET'])
def login():
    """
    uses gae api to get information about current user
    if not connected redirected him to login page
    otherwise redirect him to index
    """
   

    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
    # steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILENAME, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        # This parameter enables offline access which gives your application
        # an access token and a refresh token for the user's credentials.
        access_type='offline',
        # This parameter enables incremental auth.
        include_granted_scopes='true')

    # Store the state in the session so that the callback can verify the
    # authorization server response.
    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILENAME, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    client = googleapiclient.discovery.build(
        'oauth2', 'v2', credentials=credentials)

    
    auth_obj = client.userinfo().v2().me().get().execute()
    if auth_obj['email'] == os.environ['ADMIN_EMAIL'] and auth_obj['verified_email']:
       
        user_key = User(email=auth_obj['email'], name=auth_obj['name'], is_admin=True).put()
        user = user_key.get() 
        login_user(user)
        next = request.args.get('next')
        if not escape(next):
            return abort(400)

        return redirect(url_for('edit_a_post_view'))



def revoke():
    if 'credentials' not in session:
        flash ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        flash('Credentials successfully revoked.')
    else:
        app.logger.error("error clearing credentials")


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    """uses api to get information about current user
    if connected redirected him to logout page
    otherwise redirect him to index"""
    revoke()
    logout_user()
    return redirect(url_for('index'))


@app.route('/ga-accept', methods=['POST'])
@csrf.exempt
def ga_accept():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('ga_accepted', 'True', max_age=30 * 24 * 60 * 60)
    return resp



@app.route('/ga-decline', methods=['POST'])
@csrf.exempt
def ga_decline():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('ga_accepted', 'False', max_age=30 * 24 * 60 * 60)
    return resp


@app.route('/images/<file_name>')
def send_image_file(file_name):
    view_image_handler = ViewImageHandler()

    return send_file(io.BytesIO(view_image_handler.read_blob_image(file_name)),
              mimetype=(view_image_handler.get_mime_type(file_name)))






@app.route('/<entity>/user',methods=['GET'])
@app.route('/user',methods=['GET'])
def findUser(entity=None):
    return jsonify(user_status=current_user.is_admin)




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
    return render_template('tags.html',user_status=current_user.is_admin,siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags.to_json(),
                           codeversion=CODEVERSION)



@app.route('/categories',methods=['GET'])
@boilercode
def view_all_categories(posts, tags, categories,  passed_days,
          remaining_days):

    site_updated = posts.site_last_updated()
    return render_template('categories.html',user_status=current_user.is_admin,siteupdated=site_updated,\
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

    return render_template('posts.html', user_status=current_user.is_admin, siteupdated=site_updated, \
                           daysleft=remaining_days, dayspassed=passed_days,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION, form=form)


@app.route('/built with',methods=['GET'])
@app.route('/about',methods=['GET'])
@boilercode
def about(posts, tags, categories, passed_days,
                    remaining_days, postkey=None):
    requested_post = posts.get_by_title("about")

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))
    site_updated = posts.site_last_updated()

    return render_template('about.html',user_status=current_user.is_admin,siteupdated=site_updated,\
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

    form = PostForm()

    return render_template('posts.html', user_status=current_user.is_admin, siteupdated=site_updated, \
                           daysleft=remaining_days, dayspassed=passed_days, tags=tags, categories=categories,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION, title="Welcome to my page",
                           form=form)


@app.route('/archives',methods=['GET'])
@boilercode
def archives(posts, tags, categories, passed_days,
                    remaining_days):
    """general url routing for template usage"""

    if request.args.get('q'):return redirect(url_for('searchresults',q=request.args.get('q')))

    form = PostForm()

    site_updated = posts.site_last_updated()

    return render_template('archives.html',user_status=current_user.is_admin,siteupdated=site_updated,\
                           daysleft=remaining_days,dayspassed=passed_days,tags=tags,categories=categories,
                           posts=posts.to_json(),
                           codeversion=CODEVERSION, form=form)



@app.route('/questions/<category>', methods=['GET'])
@boilercode
def subject_questions(posts, tags, categories, passed_days,
                    remaining_days, category):

    site_updated = posts.site_last_updated()
    posts.filter_by_category(category)

    posts.to_answers_form()


    return render_template('questions.html', user_status=current_user.is_admin, siteupdated=site_updated, \
                           daysleft=remaining_days, dayspassed=passed_days, tags=tags, categories=categories,
                           posts=posts,
                           codeversion=CODEVERSION)


@app.route('/api/tags/<tagid>', methods=['PUT'])
def updateTags(tagid):
    tag = request.json['tag']
    if current_user.is_admin:
        tags = Tags()
        tags.update_with_id(tagid, tag)
    return jsonify({})


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

        if not session.get('posts'):
            session['posts'] = []
        if title not in session.get('posts'):
            remaining_attempts =  REMAINING_ATTEMPTS \
                if len(current_post.answers) != 2 else 0

            session['posts'].append(title)
            session[title] = remaining_attempts
        else:
            remaining_attempts = session.get(title) - 1
            session[title] = remaining_attempts


        answers_form = AnswerRadioForm()
        answers_form.r_answers.data = p_answer
        answers_form.r_answers.choices = [(answer.p_answer, answer.p_answer) for answer in current_post.answers]


        if answers_form.validate_on_submit():
            answers_stats = {}
            if  remaining_attempts < 0:
                result = False
                alert_type = "warning"
                msg = "Sorry, no attempts left!"

            else:
                current_post.set_selected_answer(p_answer)

                if current_post.is_answer_correct():
                    result = True
                    alert_type = "success"
                    msg = "Great!"
                    answers_stats = current_post.get_answers_statistics()
                elif remaining_attempts == 1:
                    result = False
                    alert_type = "danger"
                    msg = "You have one last attempt!"
                elif remaining_attempts == 0:
                    result = False
                    alert_type = "warning"
                    msg = "Sorry, no attempts left!"
                else:
                    result = False
                    alert_type = "warning"
                    msg = 'Please try again, {} attempts remaining.'.format(remaining_attempts)

            return jsonify(result=result,
                               msg=msg,
                               remaining_attempts=remaining_attempts,
                               answers_stats=answers_stats,
                               alert_type=alert_type)
        else:
            return jsonify({})


@app.route('/api/posts',methods=['GET'])
def main():
        posts = Posts()

        return jsonify(posts.to_json())


@app.route('/api/posts', methods=['POST'])
@login_required
def new_post():
    form = PostForm()
    if current_user.is_admin and form.validate_on_submit():  # new entity
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
        if "images" in raw_post.keys() and raw_post["images"]:
            for img in raw_post["images"]:
                image_base64 = img["url"].split("base64,")[-1]
                mime_type = img["url"].split("base64,")[0].replace('data:', '').replace(';', '')
                image_filename = img["filename"].split("\\")[-1]

                if allowed_file(image_filename):
                    image_filename = secure_filename(image_filename)
                    post.add_blob(base64.b64decode(image_base64), image_filename, mime_type)

        return jsonify(post.to_json())  # Needs check
    else:
        return jsonify(msg="missing token")



@csrf.exempt
@app.route('/api/posts/<id>/images', methods=['POST'])
@login_required
def get_post_images(id):
    """get images from a post with id"""
    if current_user.is_admin:
        asked_post = BlogPost.get(id)

        if 'image' not in request.files:
            abort(500)

        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            abort(500)
        if file and allowed_file(file.filename):
            image_filename = secure_filename(file.filename)
            mime_type = file.content_type

            image_key = asked_post.add_blob(file.read(), image_filename, mime_type)
            return jsonify(image_key=image_key)


@csrf.exempt
@app.route('/api/posts/<id>/images/<filename>', methods=['DELETE'])
def delete_post_images(id, filename):
    """get images from a post with id"""
    if current_user.is_admin:
        asked_post = BlogPost.get(id)

        if filename == '':
            flash('No selected file')
            abort(500)
        if file and allowed_file(filename):
            image_filename = secure_filename(filename)

            asked_post.delete_blob_from_post(image_filename)
            return jsonify(msg="file deleted")


@app.route('/api/posts/<id>', methods=['GET'])
def get_post(id):
    asked_post = BlogPost.get(id)
    return jsonify(asked_post.to_json())  # dangerous



@app.route('/api/posts/<id>', methods=['PUT'])
@login_required
def edit_post(id):

    form = PostForm()
    if form.validate_on_submit():
        try:
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

            updating_post.edit(title, body, datetime.datetime.now(), tags_keys,
                               category_key, raw_summary, raw_answers=request.json['answers'])
        except AttributeError as e:
            abort(500)

        return jsonify(updating_post.to_json())  # dangerous


@csrf.exempt
@app.route('/api/posts/<id>', methods=['DELETE'])
@login_required
def delete_post(id):

    if current_user.is_admin:
        posts = Posts()

        tags = Tags()

        categories = Categories()

        updating_post = BlogPost.get(int(id))

        categories.delete(updating_post.category)

        posts.delete(updating_post.key)

        tags.update([])

    return jsonify(msg="OK")



@app.route('/articles/<category>/<year>/<month>/<title>', methods=['GET'])
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

    answers_form.r_answers.choices = [(answer.p_answer, answer.p_answer) for answer in current_post.answers
                                      if answer.p_answer != u'']
    return render_template('singlepost.html', user_status=current_user.is_admin, siteupdated=site_updated, \
                                        daysleft=remaining_days, dayspassed=passed_days, RelatedPosts=related_posts, \
                                        Post=current_post.to_json(), posttagnames=post_tag_names, category=category,
                                        answers_field = answers_form)

@app.route('/edit',methods=['GET'])
@app.route('/edit/<postkey>',methods=['GET'])
@login_required
def edit_a_post_view(postkey=None):

    form = PostForm()
    posts = Posts()

    passed_days, remaining_days = calculate_work_date_stats()
    site_updated = posts.site_last_updated()
    return render_template('posts.html',user_status=current_user.is_admin, 
                           siteupdated=site_updated,
                           daysleft=remaining_days,dayspassed=passed_days,
                           codeversion=CODEVERSION, form=form)





# @app.route('/recent.atom')
# def recent_feed():
#     feed = AtomFeed('Recent Articles',
#                     feed_url=request.url, url=request.url_root)
#     posts = Posts()
#     feed = posts.add_to_feed(feed, request.url)

#     return feed.get_response()


@app.route('/rebuild_index', methods=['GET'])
def rebuild_index():
    if current_user.is_admin:
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
    logging.error("error! {}".format(error))
    if isinstance(error, InvalidUsage):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code

    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

