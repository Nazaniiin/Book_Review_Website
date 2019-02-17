import os
import requests

from flask_session import Session
from flask import Flask, session, render_template, request, jsonify, redirect

from sqlalchemy.sql import exists
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import scoped_session, sessionmaker

from utils.database import *

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
db.init_app(app)

def create_session(user):
    session['logged_in'] = True
    session['username'] = user

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/account", methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        # User registration
        if request.form.get('submit') == 'register':
            user = User(username = request.form['username'],
                        email = request.form['email'],
                        password = request.form['password'],
                        fname = request.form['fname'])

            user_exists = User.query.filter_by(username = user.username).first()
            if user_exists is not None:
                error = "Username is already taken."
                return render_template("error.html", error=error)
                
            email_exists = User.query.filter_by(email = user.email).first()
            if email_exists is not None:
                error = "There is an account associated with this email address."
                return render_template("error.html", error=error)

            else:
                if not request.form['username']:
                    error = 'Username cannot be empty.'
                    return render_template("error.html", error=error)
                elif not request.form['password']:
                    error = 'Password cannot be empty.'
                    return render_template("error.html", error=error)
                elif not request.form['email']:
                    error = 'Email address cannot be empty.'
                    return render_template("error.html", error=error)
                else:
                    user.add_to_db()
                    create_session(user.username)
                    name = user.username.capitalize()
                    return render_template("home.html", name=name)

        # User login
        elif request.form.get('submit') == 'login':
            if not request.form['username']:
                error = 'Please enter your username.'
                return render_template("error.html", error=error)
            if not request.form['password']:
                error = 'Please enter your password.'
                return render_template("error.html", error=error)

            else:
                POST_USERNAME = str(request.form['username'])
                POST_PASSWORD = str(request.form['password'])
                user_ok = User.query.filter(and_(User.username==POST_USERNAME,
                                                 User.password==POST_PASSWORD)).first()
                if user_ok:
                    create_session(POST_USERNAME)
                    name = POST_USERNAME.capitalize()
                    return render_template("home.html", name=name)
                else:
                    error = 'Invalid user name or password.'
                    return render_template("error.html", error=error)
            
    if request.method == 'GET':
        return render_template("account.html")

@app.route("/search", methods=['POST'])
def search():
    if request.method == 'POST':
        req = request.form.get('search')
        req = '%' + req + '%'    
        books = Book.query.filter(or_(Book.title.ilike(req),
                                      Book.author.ilike(req),
                                      Book.isbn.ilike(req),
                                      Book.years.ilike(req))).all()
        if books:
            book_list = []
            for book in books:
                book_list.append({"isbn":book.isbn,
                                  "title":book.title, 
                                  "author":book.author,
                                  "year":book.years})
            name = session['username'].capitalize()
            return render_template("home.html", name=name, book_list=book_list)
        else:
            error = "No result found for your search."
            return render_template("error.html", error=error)

@app.route("/book/<isbn>", methods=['GET','POST'])
def book(isbn):
    # Retreive data from GoodReads database
    key = "zj0DvhfIpMlJesiHiXjAA"
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                        params={"key": key, "isbns": isbn})
    req_result = res.json()

    book_isbn = req_result['books'][0]['isbn']
    reviews_count = req_result['books'][0]['reviews_count']
    average_rating = req_result['books'][0]['average_rating']

    # Retrieve data from our own database
    books = Book.query.filter_by(isbn=isbn).all()
    if books:
        book_info = []
        for book in books:
            book_info.append({"title":book.title, "author":book.author, 
                              "isbn":book.isbn, "year":book.years,
                              "reviews": reviews_count, "rating": average_rating})
    
    # Retreive book cover from OpenLibrary cover database
    cover = "http://covers.openlibrary.org/b/isbn/" + book_isbn + "-M.jpg"

    # Add review for a book
    if request.form.get('submit') == 'review':
        book_review = Review.query.filter(and_(Review.user_id==session['username'],
                                               Review.book_id==book_isbn)).all()
        if book_review:
            error = "You have already submitted a review for this book."
            return render_template("error.html", error=error)
        
        app.logger.info("Adding a new review")
        new_review = Review(book_id = book_isbn,
                            user_id = session['username'],
                            review = request.form['review'],
                            rating = request.form['rating'])
        new_review.add_to_db()

    # Display book reviews from other users
    reviews = Review.query.filter_by(book_id=book_isbn).all()
    if reviews:
        all_reviews = []
        for review in reviews:
            all_reviews.append({"user": review.user_id,
                                "review": review.review,
                                "rating": review.rating})
    else:
        all_reviews = []

    return render_template("book.html", book_info=book_info,
                            all_reviews=all_reviews, cover=cover)

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return render_template("index.html")

@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.form.get('submit') == 'message':
        app.logger.info("Sending a new message")
        new_message = Message(name = request.form['name'],
                              email = request.form['email'],
                              message = request.form['message'])

        db.add(new_message)
        db.commit()
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")
