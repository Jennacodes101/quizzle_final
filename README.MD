# QUIZZLE quiz game by Jenna Castillo

## Video Demo:

<https://youtu.be/RA16_4dTG5c>

## Description:

My project is a web application written in python, SQLite, and javascript. My web application, Quizzle, is a daily quiz game. Each user can log into their profile every day and complete a new auto-generated quiz from a database of questions. At the beginning of each day, a new list of questions is selected, and the user will have the ability to complete the quiz once. On the index page is a ranks board that ranks users to instill a competitive aspect of the application.

**Primary application features:**

- quiz game with js dynamism
- users/ sessions with login validations
- user streaks
- auto-generated questions of the day
- user profile page with user information and statistics
- index page with 3 different rank tables

### quizzle.db

In this file there are several sqlite3 tables:

  -Users: Stores user information such as username, email, password hash
  -Streaks: current streak, longest streak, boolean played_today
  -Questions: 100 a-d multi-choice questions
  -todays_questions: 10 chosen question uses foreign key questions.id
  -plays: tracks scores, playtime, and has foreign key user_id

#### helpers.py

This file hosts the login required function.

#### layout.html

This HTML page hosts the head, navbar, and footer for all the other pages.

#### app.py

app.py is the most robust file in the application. It handles sessions and routes. At the top of the file, there are required libraries, the configured flask application, and the configured database. I used the base from the finance pset9  web application for these features.

@app.route and GET/POST are used to define behaviors and functions for each HTML template:

##### login.html & "/login" app.py

Login.html hosts an HTML form. In this form I use CSS to indicate whether the form is filled or empty- indicated by an orange border. This form requires a username and input. In /login, it checks the validations and if there are any errors then it will re-render the template with an error message via jinja conditional statement.

#### register.html & "/register" app.py

Register.html includes the features of login.html as well as an email and password-confirmation input. Initially, I tried to implement these validations via the backend, but after further research in HTML forms, I discovered that I can use regex as a requirement for both the email and password inputs.

In /register via POST it receives the form information and then checks the database to assure the user or email does not already exist. If they do, it will re-render the template with the appropriate error message. If all validations pass then the input is inserted into the database and app.py and redirects to "/"

#### index.html & "/" app.py

When "/" is called,it calls check_date() to assure that todays_questions.date = date.today (explained in start_day.py). After, there are 4 SQLite queries. Three of them are to receive data on different user activities to be displayed as a ranked list in index.html. These queries are complex the join tables, complete mathematic operations, and insert a row number. The last query checks to see if the user has completed today's game and returns a boolean

Index.html receives the data through render_template. The page is designed with bootstrap and creates 3 different tables that adjust to the device width. The data from the last query is converted to a JSON object in javascript. The JS code then checks the condition and either displays a link to play the game or a bootstrap alert notifying them they have already played.

#### play.html & "/play" app.py

-user's id gets  placed in a variable
-user streak is checked. If they have already played today, they are redirected to their profile. While we've seen this protective behavior in "/", this repetitive step protects against malicious behavior from the user. If the user passes the security, then play.html is rendered with a list of today's questions.

unlike the other templates, play.html does not rely on the bootstraps framework. It is a javascript-forward template that houses the entirety of the quiz game. I decided to do this to make the user experience more enjoyable and concise. The HTML is defined by different divs:
  -Start div
  -quiz
    - question
    - choices A-D (on click calls js function checkAnswer with the choice letter as a parameter)
  -timer
  -progress
  -score counter
  -home button

Through the use of display: none of these elements are hidden until they are needed.
In the script tag, I created constant variables for these elements, so I can insert data into them as needed. The questions (python list of dictionaries) are converted to a JSON object. Once the start quiz button is clicked, the event listener will call upon startQuiz function which will hide start, load the current question, and display quiz div, timer div, and progress div. As well as start the TIMER. Once the user clicks their chosen answer, the checkAnswer function will call either answerIsCorrect or answerIsWrong- these functions will change the background color of the progress indicator to display either green = correct or red = wrong. Then checkAnswer will check the condition that the running question != the last question if it does then it will call scoreRender. If it does not then it will call renderQuestion and the process will continue. Once the score render is called he quiz div is hidden and the final score is calculation based on answers correct and time. These values are concatenated into a string and displayed within the score div. The home button is displayed. Which will lead the user back to "/". And finally the data is passed from js to python. This was a difficult process for me to implement. But it is implemented through a XMLHttpRequest that passed a js dictionary as a JSON object and opens route 'processUserResults'
`request.open('POST',`/processUserResults/${JSON.stringify(userResults)}`)`

#### "/processUserResults" app.py

converts JSON object from play.html and loads the information into the play table and updates users streak in the streaks table.

#### profile.html & "/profile"

"/profile" checks the user is logged in and then completes 3 SQLite select queries to get username, load user play history, and check if they have played today. The data passed through render template to profile.html

In profile.html at the top, the user's username, current streak, longest streak, and the playedtodayDiv. A condition is checked within the script tag where depending if the user has played today is true or false, different code is inserted into the playedTodayDiv.

below, there is a bootstrap table that displays the users play history. This is enabled by a jinja for loop

### about.html

about.html displays some basic information about myself and links to my social media.

### start_day.py

When I initially came up with the idea, I wanted new questions and streaks to be updated automatically at 12:00 UTC time. However, the more I looked into it the more I did not understand. Instead, I created this file to serve an "almost automation" when the index is loaded. It will always call check_date(). In which, the SQLite query is called:
`question_date = db.execute("SELECT date FROM todays_questions GROUP BY date")`
If the date != today.date
then start_day() is called which hosts two other methods. query_new_questions() deletes everything from todays_question table and inserts 10 new random question into the table. update_streaks() iterates through all the users and checks whether they played yesterday, if they did not then it checks if their current streak was longer than their previous streaks. It then resets their streak to 0 and played_today to false.

#### final note:

I deeply enjoyed the challenge of making this project. It was difficult and rewarding. Thank you for reading.
