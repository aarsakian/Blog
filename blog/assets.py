from os import path

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



        js = Bundle(
            "js/general.js","js/libs/showdown.js",
            filters="jsmin", output="js/markdown.min.js")
        env.register('js', js)

        bundles = [css, js]
        return bundles


if __name__ == '__main__':
    bundles = init()
    for bundle in bundles:
        bundle.build()