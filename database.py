from __init__ import *


class Photos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text(200), nullable=False)
    tag = db.Column(db.Text(200))
    update_time = db.Column(db.Integer)

    def __repr__(self):
        return f"<Photo {self.id}>"


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    update_time = db.Column(db.Integer)