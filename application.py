import os
import requests

from flask import Flask, session, render_template, request, jsonify, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import exists

app = Flask(__name__)

# Check for environment variable 
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

from utils.database import User, Review, Message

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/account", methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        # User registration
        if request.form.get('submit') == 'register':
            new_user = User(username = request.form['username'],
                             email = request.form['email'],
                             password = request.form['password'],
                             fname = request.form['fname'])

            # Check if username already exists
            user_exists = db.query(User.id).filter_by(username = new_user.username).scalar()
            if user_exists is not None:
                error = "Username is already taken."
                return render_template("error.html", error=error)
                
            # Check if email address is already used with another user
            email_exists = db.query(User.id).filter_by(email = new_user.email).scalar()
            if email_exists is not None:
                error = "There is an account associated with this email address."
                return render_template("error.html", error=error)

            else:
                # Do not allow empty username, password, or email fields
                if not request.form['username']:
                    error = 'Username cannot be empty.'
                    return render_template("error.html", error=error)
                elif not request.form['password']:
                    error = 'Password cannot be empty.'
                    return render_template("error.html", error=error)
                elif not request.form['email']:
                    error = 'Email address cannot be empty.'
                    return render_template("error.html", error=error)

                # Register a new user and add them to the database
                else:
                    db.add(new_user)
                    db.commit()
                    session['logged_in'] = True
                    session['username'] = new_user.username
                    name = new_user.username.capitalize()
                    return render_template("home.html", name=name)

        # User login
        elif request.form.get('submit') == 'login':
            # Do not allow empty username or password fields
            if not request.form['username']:
                error = 'Please enter your username.'
                return render_template("error.html", error=error)
            if not request.form['password']:
                error = 'Please enter your password.'
                return render_template("error.html", error=error)

            else:
                # Check user information for correct username and password
                POST_USERNAME = str(request.form['username'])
                POST_PASSWORD = str(request.form['password'])
                user_ok = db.execute(
                    'SELECT username, password FROM users WHERE username = :username and password = :password',
                    {"username": POST_USERNAME, "password": POST_PASSWORD}).fetchone()
                if user_ok:
                    session['logged_in'] = True
                    session['username'] = POST_USERNAME
                    name = POST_USERNAME.capitalize()
                    return render_template("home.html", name=name)
                else:
                    # Do not log in if username and password do not match
                    error = 'Invalid user name or password.'
                    return render_template("error.html", error=error)
            
    if request.method == 'GET':
        return render_template("account.html")

@app.route("/search", methods=['POST'])
def search():
    if request.method == 'POST':
        req = request.form.get('search')
        req = '%' + req + '%'
        book_result = db.execute('SELECT * FROM books WHERE upper(title) LIKE upper(:req) OR upper(author) LIKE upper(:req) OR isbn LIKE :req',
                                {"req": req}).fetchall()
        if len(book_result) > 0:
            book_list = []
            for row in book_result:
                book_list.append({"isbn":row[0], "title":row[1], 
                                  "author":row[2], "year":row[3]})
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
    book = db.execute('SELECT * FROM books WHERE isbn = :isbn',
                        {"isbn": isbn}).fetchall()
    if len(book) > 0:
        book_info = []
        for row in book:
            book_info.append({"title":row[1], "author":row[2], 
                            "isbn":row[0], "year":row[3],
                            "reviews": reviews_count, "rating": average_rating})
    
    # Retreive book cover from OpenLibrary cover database
    cover = "http://covers.openlibrary.org/b/isbn/" + book_isbn + "-M.jpg"

    # Add review for a book
    if request.form.get('submit') == 'review':
        book_review = db.execute('SELECT * FROM reviews WHERE user_id = :username and book_id = :isbn',
                                 {"username": session['username'], "isbn": book_isbn}).fetchall()
        if book_review:
            error = "You have already submitted a review for this book."
            return render_template("error.html", error=error)
        
        app.logger.info("Adding a new review")
        new_review = Review(book_id = book_isbn,
                             user_id = session['username'],
                             review = request.form['review'],
                             rating = request.form['rating'])
        
        db.add(new_review)
        db.commit()

    # Display book reviews from other users
    reviews = db.execute('SELECT * FROM reviews WHERE book_id = :isbn',
                             {"isbn": book_isbn}).fetchall()
    if len(reviews) > 0:
        for row in reviews:
            all_reviews = []
            for row in reviews:
                all_reviews.append({"user": row[2], "review": row[3], "rating": row[4]})
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
