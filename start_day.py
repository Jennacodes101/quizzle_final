import os
from datetime import date
import sqlite3
from cs50 import SQL
from random import randint
import re
import sys

db = SQL("sqlite:///quizzle.db")

def check_date():
    #check if questions are updated
    question_date = db.execute("SELECT date FROM todays_questions GROUP BY date")
    if question_date[0]["date"] != str(date.today()):
        start_day()

def start_day():
    # scrub today's questions
    query_new_questions()
    update_streaks()

def query_new_questions():
    db.execute("DELETE FROM todays_questions")

    # rand 10 times an index for a question, store that question in a dictionary, return the dictionary
    for i in range(10):
        id = randint(1, 100)
        db.execute("INSERT INTO todays_questions(question_id) SELECT id FROM questions WHERE id = ?",id)

def update_streaks():
    db = SQL("sqlite:///quizzle.db")
    # get all user ids
    user_ids = db.execute("SELECT id FROM users")

    for id in user_ids:
        print(id["id"])
        # query streaks
        user_actvy = db.execute("SELECT * FROM streaks WHERE user_id = ?", id["id"])
        print(user_actvy)
        if int(user_actvy[0]["played_today"]) == 1:
            # add to current streak
            db.execute("UPDATE streaks SET played_today = ? WHERE user_id = ? ", 0, id["id"])

        else:
            # update longest streak if current streak is longer
            if int(user_actvy[0]["longest_streak"]) < int(user_actvy[0]["streak"]):
                longest_streak = int(user_actvy[0]["streak"])
            else:
                longest_streak = int(user_actvy[0]["longest_streak"])

            print("longest streak")
            print(longest_streak)
            db.execute("UPDATE streaks SET played_today = ?, streak = ?, longest_streak = ? WHERE user_id = ?", 0, 0, longest_streak, id["id"])
    print(db.execute("SELECT * FROM streaks"))
