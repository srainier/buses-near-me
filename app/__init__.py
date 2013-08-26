from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.routing import BaseConverter

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

class CoordinateConverter(BaseConverter):
    def __init__(self, url_map):
        super(CoordinateConverter, self).__init__(url_map)
        self.regex = '[+-]?[0-9]+\.[0-9]+'

    def to_python(self, value):
        return float(value)

app.url_map.converters['coord'] = CoordinateConverter


from app.busesnearme import api, models, views
