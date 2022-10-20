import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from jinja2 import Template
from datetime import date
from start_day import check_date
import sys
import json
import time
import datetime

from helpers import login_required

# Configure application, self == app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Configure questions library
db = SQL("sqlite:///quizzle.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username - serverside
        if username is None:
            return render_template("login.html", error_message="Must include username")

        # Ensure password - serverside
        elif password is None:
            return render_template("login.html", error_message="Must include password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # if username and password do not match
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            error_message = " Invalid Username or Password"
            return render_template("login.html", error_message="Invalid Username or Password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    # log out



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return render_template("login.html")
# register

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # verify form
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # query db for username or email
        username = str(username)
        email = str(email)
        rows_user = db.execute("SELECT COUNT(*) FROM users WHERE username = ? ", username)
        rows_email = db.execute("SELECT COUNT(*) FROM users WHERE email = ? ", email)

        # check if input is valid
        if rows_email[0]['COUNT(*)'] == 1 or rows_user[0]['COUNT(*)']  == 1:
            return render_template("register.html", error_message="Username or email already exists")
        elif username is None or password is None or confirmation is None or email is None:
            return render_template("register.html", error_message="Please enter a valid username and password")
        elif password != confirmation:
            return render_template("register.html", error_message="Password and confirmation does not match")
        else:
            # check if password has at least one letter and special character
            num = 0
            splchar = 0
            cnt = 0
            for i in password:
                # iterate through letters counting special characters and numbers
                if i.isdigit():
                    num += 1
                    cnt += 1
                if i == '?' or i == '.' or i == '!' or i == "$" or i == "-":
                    splchar += 1
                    cnt += 1
                else:
                    cnt += 1
            if num < 1 or cnt < 8 or splchar < 1:
                return render_template("register.html", error_message="Password must meet requirements")
            # send_welcome(email, username)
            pass_hash = generate_password_hash(password)
            db.execute("INSERT INTO users(username, email, password_hash) VALUES(?, ?, ?)", username, email, pass_hash)
            rows = db.execute("SELECT id FROM users WHERE username = ?", username)
            db.execute("INSERT INTO streaks(user_id) VALUES (?)", rows[0]["id"] )
            session['user_id'] = rows[0]["id"]

            return redirect("/")

    # If request method is get
    if request.method == "GET":
        return render_template("register.html")


# homepage (index)
@app.route("/")
@login_required
def index():
    check_date()
    # get rank - join call usernames &
    today = date.today()
    id = session["user_id"]

    today_ranks = db.execute("SELECT ROW_NUMBER() OVER(ORDER BY plays.total_score DESC) as rank, plays.total_score, plays.time_count, users.username FROM users \
        INNER JOIN plays ON users.id = plays.user_id WHERE plays.date = ? LIMIT 10", today)

    total_ranks = db.execute("SELECT ROUND(SUM(plays.total_score), 2) as total,\
        ROW_NUMBER() OVER(ORDER BY SUM(plays.total_score) DESC) as rank, users.username \
        FROM users \
        INNER JOIN plays ON users.id = plays.user_id \
        GROUP BY users.id \
        LIMIT 5")

    # for rank in total_ranks:
    #     rank['total'] = round(rank['total'], 2)
    #check if user has played today

    top_streaks = db.execute("SELECT ROW_NUMBER() OVER(ORDER BY streaks.streak DESC) as rank, streaks.streak, users.username FROM users\
        INNER JOIN streaks ON streaks.user_id = users.id GROUP BY users.id LIMIT 5")

    usract = db.execute("SELECT CASE WHEN EXISTS(SELECT * FROM plays WHERE user_id = ? AND date = ?) \
        THEN CAST(1 AS BIT)\
            ELSE CAST(0 AS BIT) END",id, today)
    user_played_today = list(usract[0].values())

    return render_template("index.html", today_ranks=today_ranks, total_ranks=total_ranks, top_streaks=top_streaks, user_played_today=user_played_today)

# play game
@app.route("/play", methods=["GET"])
@login_required
def play():
    if request.method == "GET":
        # loading the information
        id = session["user_id"]

        # check user has not played today from streak-
        user_streak = db.execute("SELECT played_today FROM streaks WHERE user_id = ?", id)

        if user_streak[0]["played_today"] == 1:
            return redirect("/profile")
        else:
            # begin play session
            t_questions = db.execute("SELECT * FROM questions JOIN todays_questions ON todays_questions.question_id = questions.id;")
            return render_template("play.html", t_questions=t_questions)

# store user results
@app.route('/processUserResults/<string:userResults>', methods=['POST'])
@login_required
def process_results(userResults):
    id = session["user_id"]
    user_results = json.loads(userResults)
    # convert time from seconds to datetime minutes
    time_converted = str(datetime.timedelta(seconds = user_results["time"]))
    db.execute("INSERT INTO plays(answers_correct, time_count, total_score, user_id)\
        VALUES(?, ?, ?, ?)",user_results["score"], time_converted , user_results["finalScore"], id)

    user_streak = db.execute("SELECT * FROM streaks WHERE user_id = ?", id )
    streak_new = int(user_streak[0]["streak"]) + 1
    db.execute("UPDATE streaks SET streak = ?, played_today = ?  WHERE user_id = ? ", streak_new, 1, id,)

    return 0



@app.route("/profile")
@login_required
def profile():
    # obtain user information
    user_id = session["user_id"]
    if user_id is None:
        return redirect("/login")

    # Load user info:
    stats = db.execute("SELECT * FROM plays WHERE user_id = ? ORDER BY date DESC", user_id)
    username = db.execute("SELECT username FROM users WHERE id = ?", user_id)
    streak_info = db.execute("SELECT * FROM streaks WHERE user_id = ?", user_id)
    today = date.today

    return render_template("profile.html", stats=stats, username=username, streak_info=streak_info, today=today)

@app.route("/about")
def about():
    return render_template("about.html")
# load highest rated players

# check if person has played, if so display their rating
# if the user has not played then they will see a route that will display play

# quiz
# @app.route("/play")
# load in questions
# start timer for play
# collect user input
# once finished
# calculate score and save results in plays

# profile
# @app.route("/profile")
# display username
# display history
# display streak

# @app.route("/results")
# display user results


# @app.route("/about")
