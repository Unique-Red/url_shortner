from . import db
from flask_login import UserMixin

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(500))
    short_url = db.Column(db.String(10), unique=True)
    custom_url = db.Column(db.String(50), unique=True, default=None)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return '<Url %r>' % self.short_url
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String)
    password = db.Column(db.String)
    confirmed = db.Column(db.Boolean, default=False)