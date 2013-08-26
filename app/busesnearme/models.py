from app import db

class Stop(db.Model):
    __tablename__ = 'stops'
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    tag = db.Column(db.String)
    title = db.Column(db.String)
    stop_id = db.Column(db.Integer)

    def __init__(self, lat=0.0, lon=0.0, tag="", title="", stop_id=0):
        self.lat = lat
        self.lon = lon
        self.tag = tag
        self.title = title
        self.stop_id = stop_id
