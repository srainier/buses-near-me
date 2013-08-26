import os

from flask.ext.assets import Environment, Bundle

from app import app

# Assets - bundling javascript and css files into single files.
assets = Environment(app)
js = Bundle(
    'js/vendor/underscore.js',
    'js/vendor/jquery-1.10.1.js',
    'js/vendor/backbone.js',
    'js/plugins.js',
    'js/main.js',
    output='compiled/app.js')

css = Bundle(
    'css/normalize.min.css',
    'css/pure-skin-bluish.css',
    'css/h5bp.css',
    'css/main.css',
    output='compiled/app.css')

assets.register('js_all', js)
assets.register('css_all', css)
ASSETS_DEBUG = False

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
