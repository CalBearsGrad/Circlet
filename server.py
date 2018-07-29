""" Circlet """


#########################################################################
##### Imports #####
import os

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
import sendgrid
from sendgrid.helpers.mail import *
from model import connect_to_db, get_circlet, get_user, create_goal_circlet

app = Flask(__name__)

with open('hackathon-api-key.txt') as f:
    sendgrid_api_key = f.read().strip()

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ['APP_KEY']

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

#########################################################################
##### Routes #####

@app.route('/')
def index():
    """ Homepage """
    session['user_id'] = "1"
    return render_template('homepage.html')


@app.route('/register')
def register():
    """ Homepage """
    email = request.form.get('email')
    password = request.form.get('password')
    user = create_user(email, password)
    return render_template('profile.html', user=user)


@app.route('/profile/<id>')
def profile(id):
    return render_template('profile.html', user=get_user(id))

@app.route('/circlet/<id>')
def circlet(id):
    return render_template('circlet.html', circlet=get_circlet(id))

@app.route('/create-goal')
def create_goal():
    if 'user_id' not in session:
        return "you must log in to create a goal"
    user_id = session["user_id"]
    user = get_user(user_id)
    return render_template('create_goal.html', user=user)

@app.route('/create_goal', methods=['POST'])
def create_goal_post():
    if 'user_id' not in session:
        return "you must log in to create a goal"
    user_id = session["user_id"]
    user = get_user(user_id)
    print(request.form)
    create_goal_circlet(request.form.get('goal_name'), request.form.get('description'), request.form.get('goal'), request.form.get('due_date'))
    return render_template('invite_to_circlet.html', user=user)


def create_user(email, password):
    return "1"

@app.route('/sendemail')
def send():
    sendemail("""
        <html>
            <head>
            </head>
            <body>
                <h1>Sent from Python</h1>
                I like python.
            </body>
        </html>
    """)
    return "ok"

def sendemail(recipient, alertbody):
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api_key)
    from_email = Email("davidvgalbraith@gmail.com")
    to_email = Email(recipient)
    subject = "Sending with SendGrid is Fun"
    content = Content("text/html", alertbody)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())



#########################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
