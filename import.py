import csv
import credentials
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(credentials.postgre_url)
                                        
db = scoped_session(sessionmaker(bind=engine)) 

db.execute('CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL UNIQUE, password VARCHAR NOT NULL UNIQUE)')
db.execute('CREATE TABLE reviews (username VARCHAR PRIMARY KEY, isbn VARCHAR NOT NULL, rating INTEGER, review VARCHAR)')

db.execute("CREATE TABLE books (isbn VARCHAR PRIMARY KEY, title VARCHAR NOT NULL, author VARCHAR NOT NULL)")

f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, date in reader: 
    db.execute("INSERT INTO books (isbn, title, author, date) VALUES (:isbn, :title, :author, :date)",
                {"isbn":isbn, "title":title, "author":author, "date":date}) 

db.commit() 
