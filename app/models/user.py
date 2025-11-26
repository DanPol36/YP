from flask_login import UserMixin
from .. import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')

    documents = db.relationship('Document', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'