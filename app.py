import os
import flask
from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import credentials


app = Flask(__name__)

# Check for environment variable
# if not os.getenv("DATABASE_URL"):
    # raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(credentials.postgre_url)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login", methods=['GET','POST'])
def login():
    if flask.request.method == 'POST':
        new_username = request.form.get("new_username")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        if new_password != confirm_password:
            return render_template('error.html', message = "Passwords don't match, please try again")
        if db.execute("SELECT * FROM users WHERE username = :username OR password = :password", {"username": new_username, "password": new_password}).rowcount != 0:
            return render_template('error.html', message = 'Error, Username or password already exist')
        db.execute("INSERT INTO users (username, password) VALUES (:username,:password)", {"username": new_username, "password": new_password})
        db.commit()
    return render_template('login.html')


@app.route("/signup")
def signup():
    return render_template('signup.html')


@app.route("/home", methods=['POST'])
def home():
    username = request.form.get("username")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 0:
        return render_template('error.html', message = 'Invalid username or password')
    uid = db.execute("SELECT username FROM users WHERE username = :username AND password = :password", {"username": username, "password": password})
    db.commit()
    session["username"] = [row[0] for row in uid][0]
    return render_template('home.html', username = username)


@app.route("/home/search", methods=['POST'])
def search():
    book = request.form.get("book")
    if db.execute("SELECT * FROM books WHERE isbn LIKE :book OR title LIKE :book OR author LIKE :book", {"book":'%'+ book +'%'}).rowcount != 0:
        results = db.execute("SELECT * FROM books WHERE isbn LIKE :book OR title LIKE :book OR author LIKE :book", {"book":'%'+ book +'%'}).fetchall()
        return render_template('search.html', results = results, book = book)
    else:
        return render_template('error.html', message = 'Error for search: Nothing found')


@app.route("/home/<isbn>")
def book(isbn): 
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": credentials.goodreads_api, "isbns": isbn})
    rating = res.json()['books'][0]['average_rating']
    numrating = res.json()['books'][0]['work_ratings_count']
    if db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0:
        reviewsnone = 'Sorry, there are no reviews for this book at the moment'
    else:
        reviewsnone = ''
    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    book_details = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    return render_template('book.html', rating = rating, numrating = numrating, reviews = reviews, reviewsnone = reviewsnone, book_details = book_details)


@app.route("/home/<isbn>/review")
def review(isbn):
    book_details = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    name = book_details.title
    return render_template('review.html', isbn = isbn, booktitle = name)


@app.route("/home/<isbn>/review/success", methods=['POST'])
def success(isbn):
    rating = request.form.get("rating")
    review = request.form.get("review")
    username = session['username']
    if (db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND username = :username", {"isbn":isbn, "username":username}).rowcount != 0) or (len(rating) != 1) or (int(rating) not in range(0,6)):
        return render_template('errorreview.html')
    else:
        db.execute("INSERT INTO reviews (username, isbn, rating, review) VALUES (:username, :isbn, :rating, :review)", {"username": username, "isbn": isbn, "rating": int(rating), "review": review})
        db.commit()
        return render_template('success.html', isbn = isbn)


@app.route("/api/<isbn>")
def api(isbn):
    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).rowcount == 0:
        return jsonify({"error": "Invalid book isbn"}), 404
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": credentials.goodreads_api, "isbns": isbn})
    rating = res.json()['books'][0]['average_rating']
    numrating = res.json()['books'][0]['work_ratings_count']
    return jsonify({
              "title": book.title,
              "author": book.author,
              "isbn": book.isbn,
              "date": book.date,
              "review_count": numrating,
              "average_score": rating
          })
