from app import db

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    email = db.Column(db.String(128))
    image = db.Column(db.String(255))
    role = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)