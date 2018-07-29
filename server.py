""" Circlet """


#########################################################################
##### Imports #####
import os

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
import sendgrid
from sendgrid.helpers.mail import *

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

def create_user(email, password):
    return "1"

def get_user(id):
    return None

@app.route('/sendemail')
def send():
    sendalert("""
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

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
