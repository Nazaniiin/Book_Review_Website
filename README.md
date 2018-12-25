# Book Review Website

## About
Web Programming with Python and HTML

In this project I built a book review website. I used Goodreads API to pull in the ratings from a broader audience. I also used OpenLibrary to pull in book covers to the website.

## Technologies
- Python 3
- HTML
- CSS
- Flask Framework
- Jinja2
- SQLAlchemy

## APIs

- [Goodreads API](https://www.goodreads.com/api)
- [OpenLibrary API](https://openlibrary.org/dev/docs/api/covers)

## Features
In the website:
- Users are able to register and create a new account
- Users are able to log in to the website using their username and password
- Logged in users can search for books, leave reviews for books, and read reviews made by other people

## How to Run
### Dependencies

In order to run this application, you need the following dependencies:

- Python 3
- Flask 
- SQLAlchemy
- PostgreSQL database
    - For this application I have used Heroku database. 
      Navigate to https://www.heroku.com/, and create an account if you don’t already have one.
    - You are free to set up PostgreSQL database on your local computer.
- Goodreads API
    - You need to create a Goodreads account if you don't already have one.
      Navigate to https://www.goodreads.com/api/keys, and apply for an API key.

You also need to install a couple of other python packages. Those can be found and installed from `requirements.txt` file.

### Configure Database

There are two python scripts provided under `utils/` directory. Using these two scripts you can:
- `database.py`: Creates all the databases needed to run the application. It creates the following tables:
    - **Users** : Stores user information such as name, username, password, and email address.
    - **Books** : Stores book information such as book title, author, isbn number, and year of publish.
    - **Reviews** : Stores all the reviews given by users to books in our database.
    - **Message** : Stores all the messages sent to us from the Contact page.
- `import.py`: Imports all the data from `books.csv` to the database `books`. This is the database users use later to query books from.

### Run
#### Set up Environment Variables
- `export FLASK_APP=application.py`
- `export FLASK_DEBUG=1`
- `export DATABASE_URL=HEROKU_DATABASE_LINK` (Do this if you use Heroku as your PostgreSQL database)

In you terminal run `flask run`, which will run the `application.py` set on your environment. You can visit the app by visiting: http://localhost:5000/

## Functionality
### Operations

#### Homepage
`/` 
- Not logged in
![main-page-before-login](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/main-page-before-login.png)

- Logged in
![main-page-after-login](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/main-page-after-login.png)

`/home` (For logged in users)

![home-page-after-login](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/home-page-after-login.png)

`/account`

- Not logged in
![account-page-before-login](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/account-page-before-login.png)

- Logged in
![account-page-after-login](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/account-page-after-login.png)

`/search` (For logged in users)

- After search
![search-page-after-search](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/search-page-after-search.png)

`book/<isbn>` (For logged in users)

- Before review submission
![book-page-before-review-submission](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/book-page-before-review-submission.png)

- After review submission (New review by Paul is added to the list of reviews)
![book-page-after-review-submission](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/book-page-after-review-submission.png)

`/contact`
![contact-page](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/contact-page.png)

`/about`
![about-page](https://github.com/Nazaniiin/Book_Review_Website/blob/master/screenshots/about-page.png)

### Handling Special Cases in User Interactions

An error is given to users in the following situations:

- If users enter invalid username and password
- If users do not use unique username or email address
- If users leave username, password, or email fields empty upon registration
- If no result is found for user's book search
- If users want to submit more than one review for a book
