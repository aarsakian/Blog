from os import path

import os

from flask_assets import Bundle, Environment
from flask import Flask



def init(app=None):
    app = app or Flask(__name__)

    with app.app_context():
        env = Environment(app)
        env.load_path = [path.join(path.dirname(__file__), 'static')]
        # env.append_path('assets')
        # env.set_directory(env_directory)
        # App Engine doesn't support automatic rebuilding.
        env.auto_build = False
        # This file needs to be shipped with your code.
        env.manifest = 'file'

        css = Bundle(
            'css/style.css',
            filters="cssmin", output="css/style.min.css")
        env.register('css', css)


        #jsfiles = bundle_js_files(env.load_path[0])
        jsfiles = [path.join(env.load_path[0], 'js/general.js'),
        path.join(env.load_path[0], 'js/libs/underscore/underscore-min.js'),
        path.join(env.load_path[0], 'js/libs/backbone/backbone-min.js'),
        path.join(env.load_path[0], 'js/libs/backbone/backbone-nested.js'),
        path.join(env.load_path[0], 'js/libs/handlebars/handlebars-v4.0.11.js'),
        path.join(env.load_path[0], 'js/app.js')]

        jsfiles2 = [path.join(env.load_path[0], 'js/common.js'),


        path.join(env.load_path[0], 'js/apps/posts/models/post.js'),
        path.join(env.load_path[0], 'js/apps/posts/models/answer.js'),
        path.join(env.load_path[0], 'js/apps/posts/postList.js'),
        path.join(env.load_path[0], 'js/apps/posts/collections/answerscollection.js'),
        path.join(env.load_path[0], 'js/apps/posts/collections/postscollection.js'),
        path.join(env.load_path[0], 'js/apps/posts/postAnswers.js'),
        path.join(env.load_path[0], 'js/apps/posts/app.js'),
        path.join(env.load_path[0], 'js/routes.js'),
        path.join(env.load_path[0], 'js/apps/posts/postEditor.js')]
        js1 = Bundle(jsfiles,
            filters="jsmin", output="js/everything.min.js")
        env.register('js', js1)



        bundles = [css, js1]
        return bundles


def bundle_js_files(location):
    jsfiles = []
    for root, dirs, files in os.walk(location):
        for fname in files:
            if path.basename(root) != "notinuse" and\
                fname != "everything.min.js" and fname.endswith(".js"):
                print (fname)
                jsfiles.append(path.join(root, fname))
    return jsfiles

if __name__ == '__main__':
    bundles = init()
    for bundle in bundles:
        bundle.build()
