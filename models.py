from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import extract

db = SQLAlchemy()

class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    cin = db.Column(db.String, nullable=False)
    request_limit = db.Column(db.Integer, nullable=False)
    subscription_start = db.Column(db.DateTime, nullable=True)
    users = db.relationship('User', backref='organisation', lazy=True)

    def __init__(self, name, request_limit):
        self.name = name
        self.request_limit = request_limit

    def __repr__(self):
        return f'<Organisation {self.name}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auth0_id = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    profile_photo = db.Column(db.String, nullable=True)
    role = db.Column(db.String, nullable=True)
    query_limit = db.Column(db.Integer, nullable=True)
    queries = db.relationship('Query', backref='user', lazy=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    subscription_start = db.Column(db.DateTime, nullable=True)


    def __init__(self, auth0_id, name, email, profile_photo, role=None, query_limit=None, organisation_id=None, created_at=None):
        self.auth0_id = auth0_id
        self.name = name
        self.email = email
        self.profile_photo = profile_photo
        self.role = role
        self.query_limit = query_limit
        self.organisation_id = organisation_id
        self.created_at = created_at


class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    auth0_id = db.Column(db.String, db.ForeignKey('user.auth0_id'), nullable=False)
    user_input = db.Column(db.String, nullable=True)
    assistant_output = db.Column(db.String, nullable=True)
    thread_id = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<Query {self.id}>'


class ContactForm(db.Model):
    __tablename__ = 'contact_form'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    privacy_policy = db.Column(db.Boolean, nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))