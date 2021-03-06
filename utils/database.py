# Create all the tables needed in this project
import os

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy import create_engine

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fname = db.Column(db.String(80), nullable=True)
    reviews = db.relationship('Review', backref='users', lazy=True)

    def __init__(self, username, password, email, fname):
        self.username = username
        self.password = password
        self.email = email
        self.fname = fname

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

class Book(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String(15), primary_key=True)
    title = db.Column(db.String(30), nullable=True)
    author = db.Column(db.String(30), nullable=True)
    years = db.Column(db.String(10), nullable=True)
    reviews = db.relationship('Review', backref='books', lazy=True)

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(15), db.ForeignKey('books.isbn'))
    user_id = db.Column(db.String(50), db.ForeignKey('users.username'))
    review = db.Column(db.String(10000), nullable=True)
    rating = db.Column(db.String(1), nullable=True)

    def __init__(self, book_id, user_id, review, rating):
        self.book_id = book_id
        self.user_id = user_id
        self.review = review
        self.rating = rating

    def add_to_db(self):
        db.session.add(self)
        db.session.commit()

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    message = db.Column(db.String(10000), nullable=True)

    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message

db.create_all()
db.session.commit()
