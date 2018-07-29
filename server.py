""" Circlet """


#########################################################################
##### Imports #####
import os

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from model import User, CreditCards, Circlets, UserCirclets

from model import connect_to_db, db

from flask_debugtoolbar import DebugToolbarExtension

import bcrypt

import sendgrid
from sendgrid.helpers.mail import *
from model import (connect_to_db, get_circlet, get_user, create_goal_circlet,
get_all_users, insert_user_circlets, get_users_for_circlet, set_user_circlet_info)

from model import User, Circlets, UserCirclets

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


@app.route("/verify-registration", methods=['POST'])
def verify_registration():
    """ Verify registration form """

    print "User Registration"

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")

    cc_number = request.form.get("cc-number")
    exp_month = request.form.get("cc-month")
    exp_year= request.form.get("cc-year")
    cc_cvc = request.form.get("cc-cvc")


    # Hash the password because security is important
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    print "First:", first_name
    print "Last:", last_name
    print "Email:", email
    print "PW:", hashed_pw

    # Look for the email in the DB
    existing_user = User.query.filter(User.email == email).all()

    if len(existing_user) == 0:
        print "new CC added"
        cc = CreditCards(number=cc_number, exp_month=exp_month, exp_year=exp_year, cvc=cc_cvc)
        db.session.add(cc)
        db.session.commit()


        new_cc = CreditCards.query.filter(CreditCards.number == cc_number).one()
        print new_cc

        print "New User"
        user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=new_cc.credit_card_id)
        print user

        db.session.add(user)
        db.session.commit()

        flash("You are now registered!")
        return redirect('/profile')

    elif len(existing_user) == 1:
        print "Existing user"
        flash("You're already registered!")
        return redirect('/')

    else:
        print "MAJOR PROBLEM!"
        flash("You have found a website loophole... Please try again later.")
        return redirect("/")

@app.route('/check-user', methods=["POST", "GET"])
def check_user():
    """allow a new user to register email address and password
    """

    print "I am in check-user route"
    if ("email" in session) == None:
            print "didn't get email"

    email = request.form.get("email")

    password = request.form.get("password")

    print email
    print password

    reference_email = Givr.query.filter_by(email=email).first()

    # user_email = reference_email.email

    if reference_email:
        print
        print "Email address matches GivrR in database"
        print
        session.clear()
        session['email'] = email
        session['password'] = password

        return redirect("/log_in")
    else:
        return redirect("/preferences-small-giv")

@app.route('/profile/<id>')
def profile(id):
    """Render Circlet status and current Circlet attribute"""

    user = User.query.filter_by(email=email).first()
    first_name = user.first_name.first()

    return render_template('profile.html', user=get_user(id), first_name=first_name(id))

@app.route('/log_in')
def log_in():
    """Allows user to log in
    """
    return render_template('log_in.html')

@app.route('/settings/<id>')
def setting(id):
    """Render Circlet status and current Circlet attribute"""
    return render_template('settings.html', user=get_user(id))


def find_harvest_one(user):
    """Will find the harvests,
      will return the total harvest,
      and will find the remaining harvest"""


    remaining_harvest = .25
    harvested = .75

    return remaining_harvest, harvested

@app.route('/giv_donut.json')
def giv_donut():
    """Return data about Circlet."""

    # print remaining harvest, harvest
    data_dict = {
                "labels": [
                    "Remaining Harvest",
                    "Harvested",
                ],
                "datasets": [
                    {
                        "data": [remaining_harvest, harvested],
                        "backgroundColor": [
                            "#20993A",
                            "#D2D4D3",
                        ],
                        "hoverBackgroundColor": [
                            "#1B7F31",
                            "#787A79",
                        ]
                    }]
                }

    return jsonify(data_dict)


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
    session['circlet'] = create_goal_circlet(request.form.get('goal_name'), request.form.get('description'), request.form.get('goal'), request.form.get('due_date')).asdict()
    return redirect('/invite-to-circlet')

@app.route('/invite-to-circlet')
def invite_to_circlet():
    if 'user_id' not in session or 'circlet' not in session:
        return "you need to be logged in and creating a circlet to invite users"
    all_users = get_all_users()
    all_other_users = []
    for user in all_users:
        if user.user_id != int(session['user_id']):
            all_other_users.append(user)
    return render_template('invite_to_circlet.html', users=all_other_users)

@app.route('/invite_to_circlet', methods=['POST'])
def invite_to_circlet_post():
    if 'user_id' not in session or 'circlet' not in session:
        return "you need to be logged in and creating a circlet to invite users"
    circlet_id = session['circlet']['circlet_id']
    users = request.form.keys()
    users.append(session['user_id'])
    insert_user_circlets(circlet_id, users)
    logged_in_user = get_user(session['user_id'])
    for user in users:
        user = get_user(user)
        if user.user_id == logged_in_user.user_id:
            continue
        content = """
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <h1>You are invited to a Circlet!</h1>
        Hey! {} {} has invited you to a Circlet! The goal is <strong>${}</strong>. Click <a href="http://localhost:5000/toggle/{}/{}" style="color:blue;">here</a> to join!
    </body>
</html>
            """.format(logged_in_user.first_name, logged_in_user.last_name,
            session['circlet']['total_amount'], session['circlet']['circlet_id'], user.user_id)
        print("contentment", content)
        sendemail(user.email, content)
    return redirect('/toggle/{}'.format(circlet_id))

@app.route('/toggle/<circlet_id>')
def toggle(circlet_id):
    if 'user_id' not in session:
        return 'you need to be logged in to toggle'
    users = get_users_for_circlet(circlet_id)
    return render_template('/toggle.html', users=users, circlet_id=circlet_id)

@app.route('/toggle/<circlet_id>/<user_id>')
def toggle_terrible_hack(circlet_id, user_id):
    # XXX EXTREMELY DANGEROUS HACK - this lets anyone log in as any user without authenticating
    # Instead we should redirect a logged out user to the login page and redirect from there to
    # /toggle/<circlet_id> when they finish logging in
    session['user_id'] = user_id
    users = get_users_for_circlet(circlet_id)
    return render_template('/toggle.html', users=users, circlet_id=circlet_id)

@app.route('/toggle/<circlet_id>', methods=['POST'])
def toggle_post(circlet_id):
    if 'user_id' not in session:
        return 'you need to be logged in to toggle'
    set_user_circlet_info(session['user_id'], circlet_id, request.form.get('monthly_payment'))
    return redirect('/confirm/{}'.format(circlet_id))

@app.route('/confirm/<circlet_id>')
def confirm(circlet_id):
    if 'user_id' not in session:
        return 'you need to be logged in to confirm'
    return render_template('confirm.html')


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
    print("SENDING EMAIL TO", recipient, "BODY", alertbody)
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api_key)
    from_email = Email("davidvgalbraith@gmail.com")
    to_email = Email(recipient)
    subject = "Message from Circlet"
    content = Content("text/html", alertbody)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print("SEND EMAIL RESPONSE")
    print(response.status_code)
    print(response.body)
    print(response.headers)



#########################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
