import os
import site
import sys

# virtualenv for the app.
site.addsitedir('/var/www/buses-near-me/.env/lib/python2.7/site-packages')

# Location of the app files.
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application
