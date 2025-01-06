import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///to_read.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/toread", methods=["GET", "POST"])
def to_read():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        date = request.form.get("date")
        db.execute("INSERT INTO to_read (title, author, date) VALUES(?, ?, ?)", title, author, date)
        return redirect("/toread")

    else:
        to_read = db.execute(f"SELECT * FROM to_read")
        return render_template("pageOne.html", books=to_read)

@app.route("/del", methods=["POST"])
def delete():
    del_title = request.form.get("del_title")
    db.execute(f"DELETE FROM to_read WHERE title = '{del_title}'")
    return redirect("/toread")

@app.route("/read", methods=["GET", "POST"])
def read():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        date = request.form.get("date")
        db.execute("INSERT INTO read (title, author, date) VALUES(?, ?, ?)", title, author, date)
        return redirect("/read")

    else:
        read = db.execute(f"SELECT * FROM read")
        return render_template("pageTwo.html", books=read)

@app.route("/reviews", methods=["GET", "POST"])
def review():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        date = request.form.get("date")
        review = request.form.get("review")
        db.execute("INSERT INTO reviewed (title, author, date, review) VALUES(?, ?, ?, ?)", title, author, date, review)
        if db.execute(f"SELECT COUNT(1) FROM read WHERE title = '{title}'") == [{'COUNT(1)':0}]:
            db.execute("INSERT INTO read (title, author, date) VALUES(?, ?, ?)", title, author, date)
        return redirect("/reviews")

    else:
        reviewed = db.execute(f"SELECT * FROM reviewed")
        return render_template("pageThree.html", books=reviewed)

@app.route("/delete", methods=["POST"])
def delete_review():
    del_title = request.form.get("bookTitle")
    db.execute(f"DELETE FROM reviewed WHERE title = '{del_title}'")
    return redirect("/reviews")

@app.route("/switch", methods=["POST"])
def switch():
    switch_title = request.form.get("bookTitle")
    author = db.execute(f"SELECT author FROM to_read WHERE title = '{switch_title}'")
    date = db.execute(f"SELECT date FROM to_read WHERE title = '{switch_title}'")
    db.execute("INSERT INTO read (title, author, date) VALUES(?, ?, ?)", switch_title, author[0]['author'], date[0]['date'])
    db.execute(f"DELETE FROM to_read WHERE title = '{switch_title}'")
    return redirect("/toread")

@app.route("/search", methods=["POST"])
def search():
    search_title = request.form.get("title")
    if db.execute(f"SELECT COUNT(1) FROM reviewed WHERE title = '{search_title}'") == [{'COUNT(1)':1}]:
        spec = db.execute(f"SELECT * FROM reviewed WHERE title = '{search_title}'")
        reviewed = db.execute(f"SELECT * FROM reviewed")
        return render_template("pageThree.html", review=spec, books=reviewed)
    else:
        print(db.execute(f"SELECT COUNT(1) FROM reviewed WHERE title = '{search_title}'"))
        return redirect("/reviews")

@app.route("/quiz")
def quiz():
    return render_template("pageFour.html")

@app.route("/find", methods=["GET", "POST"])
def books():
    if request.method == "POST":
        genre = request.form.get("genre")
        length = request.form.get("length")
        level = request.form.get("level")
        series = request.form.get("series")
        books = select_series(series)
        books = select_level(level, books)
        books = select_length(length, books)
        books = select_genre(genre, books)
        return render_template("pageFour.html", recs=books)
    else:
        return redirect("/quiz")

def select_series(series):
    if series == "none":
        return db.execute("SELECT * FROM books")
    elif series == "yes":
        return db.execute("SELECT * FROM books WHERE series = 'true'")
    return db.execute("SELECT * FROM books WHERE series = 'false'")

def select_level(level, books):
    toreturn = []
    if level == "none":
        return books
    elif level == "one":
        for i in books:
            if i["level"] == 1:
                toreturn.append(i)
    elif level == "two":
        for i in books:
            if i["level"] == 2:
                toreturn.append(i)
    elif level == "three":
        for i in books:
            if i["level"] == 3:
                toreturn.append(i)
    else:
        for i in books:
            if i["level"] == 4:
                toreturn.append(i)
    return toreturn

def select_length(length, books):
    toreturn = []
    if length == "none":
        return books
    elif length == "short":
        for i in books:
            if i["pages"] < 300:
                toreturn.append(i)
    elif length == "medium":
        for i in books:
            if i["pages"] < 500 and i["pages"] >= 300:
                toreturn.append(i)
    else:
        for i in books:
            if i["pages"] >= 500:
                toreturn.append(i)
    return toreturn

def select_genre(genre, books):
    toreturn = []
    if genre == "none":
        return books
    else:
        for i in books:
            if genre in i["genre"]:
                toreturn.append(i)
    return toreturn
