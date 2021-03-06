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
get_all_users, insert_user_circlets, get_users_for_circlet, set_user_circlet_info,
get_user_circlets, get_user_circlet, set_confirmed)

from model import User, Circlets, UserCirclets
import random

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


## Route not uisng:
# @app.route('/check-user', methods=["POST", "GET"])
# def check_user():
#     """allow a new user to register email address and password
#     """

#     print "I am in check-user route"
#     if ("email" in session) == None:
#             print "didn't get email"

#     email = request.form.get("email")

#     password = request.form.get("password")

#     print email
#     print password

#     reference_email = Givr.query.filter_by(email=email).first()

#     # user_email = reference_email.email

#     if reference_email:
#         print
#         print "Email address matches GivrR in database"
#         print
#         session.clear()
#         session['email'] = email
#         session['password'] = password

#         return redirect("/log_in")
#     else:
#         return redirect("/preferences-small-giv")



@app.route('/log_in')
def log_in():
    """Allows user to log in
    """
    return render_template('log_in.html')

@app.route("/log_out")
def log_out():
    """allow user to log out of Givr."""
    session.clear()

    return redirect("/")

@app.route('/log_in', methods=["POST"])
def log_me_in():

    login_email = request.form.get("email")
    login_password = request.form.get("password")

    print login_email, login_password

    # Get user object
    existing_user = User.query.filter(User.email == login_email).all()

    # In DB?
    if len(existing_user) == 1:
        print "Email in DB"
        existing_password = existing_user[0].password

        # Correct password (hashed)?
        if bcrypt.hashpw(login_password.encode('utf-8'), existing_password.encode('utf-8')) == existing_password:
            if 'login' in session:
                flash("You are already logged in!")
                return redirect('/')
            else:
                #Add to session
                session['user_id'] = existing_user[0].user_id
                flash("Hi {}, you are now logged in!".format(existing_user[0].first_name))
                return redirect('/')
        else:
            flash("Incorrect password. Please try again.")
            return redirect('/log_in')

    # Not in DB
    elif len(existing_user) == 0:
        print "Email not in DB"
        flash("That email couldn't be found. Please try again.")
        return redirect('/log_in')

    else:
        print "MAJOR PROBLEM!"
        flash("You have found a website loophole... Please try again later.")
        return redirect("/")


@app.route('/settings/<id>')
def setting(id):
    """Render Circlet status and current Circlet attribute"""
    return render_template('settings.html', user=get_user(id))

# Donut chart number 1 profile page


def find_harvest_one(user):
    """Will find the harvests,
      will return the total harvest,
      and will find the remaining harvest"""
    

    remaining_harvest = .20
    harvested = .80

    return remaining_harvest, harvested

def give_financial_tips():

    tips = ["If you are living paycheck-to-paycheck, before you do anything else, stop that. Figure out where you can cut costs, even if it is by a few dollars a week. The best way to do this is to start tracking where you are spending your money. That way you can make changes and set goals around your spending. That will enable you to begin saving right away without having to make more money. - Sharon Compton Game",
            "With the recent surge in equity values, remember that long-term performance, particularly for the portfolios of retirees, is better when the stock allocation is returned to the target allocation on a regular basis. In simple words, with the elevated values of equities we are currently seeing, it is a good time to lighten the equity load and add to the bond allocation. -Walt Woerheide, PhD, ChFC, CFP, RFC, Professor of Investments",
            "Without a strategic debt management plan, you will likely continue to accrue debt which puts you further behind and makes it harder to escape. Debt management includes strategically paying down the most expensive debt first, like credit card debt, then personal loans, then student loans, and then housing debt. However, debt management is also just as much about avoiding future debt and looking for areas to cut back spending or at least, spend smarter. If you find yourself buying coffee every day or eating out at lunch, think about packing lunches or buying a coffee machine, which could save you money in the long term. -Ajamu Loving, PhD, Professor of Finance"
]

    financial_tips = random.choice(tips);

    return financial_tips

@app.route('/profile/<id>')
def profile(id):
    """Render Circlet status and current Circlet attribute"""
    # user = get_user(id)

    # user = User.query.filter_by(email=email).first()
    # user_id = User.query.filter_by(user_id=id).first()
    # first_name = user.first_name.first()

    # user = User.query.filter_by(email=email).first()
    # first_name = user.first_name.first()
    financial_tips = give_financial_tips()
    user = get_user(id)
    print user


    return render_template('profile.html', user=user, financial_tips=financial_tips)

    # return render_template('profile.html', user=get_user(id), first_name=first_name(id))

@app.route('/giv_donut.json')
def giv_donut():
    print("GIVE ME A DONUT DOT JSON")
    """Return data about Circlet."""

    user_id = session["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    print "defined user id"
    remaining_harvest, harvested = find_harvest_one(user)

    print "found harvest"

    # print remaining harvest, harvest
    data_dict = {
                "labels": [
                    "Harvested",
                    "Remaining Harvest",
                ],
                "options": {
                "cutoutPercentage": 95,
                },
                "datasets": [
                    {
                        "data": [harvested, remaining_harvest],
                        "backgroundColor": [
                            "#0c7d96",
                            "#D2D4D3",
                        ],
                        "hoverBackgroundColor": [
                            "#084c5b",
                            "#D2D4D3",
                        ]
                    }]
                }
    print "OH WO WOW WOWOWOWO OWOWOW ", jsonify(data_dict)
    return jsonify(data_dict)


# Donut chart number 2 profile page


# def find_harvest_two(user):
#     """Will find the harvests,
#       will return the total harvest,
#       and will find the remaining harvest"""


#     remaining_harvest = .25
#     harvested = .75

#     return remaining_harvest, harvested

# @app.route('/giv_donut_2.json')
# def giv_donut_2():
#     """Return data about Circlet."""

#     # print remaining harvest, harvest
#     data_dict = {
#                 "labels": [
#                     "Remaining Harvest",
#                     "Harvested",
#                 ],
#                 "datasets": [
#                     {
#                         "data": [remaining_harvest, harvested],
#                         "backgroundColor": [
#                             "#20993A",
#                             "#D2D4D3",
#                         ],
#                         "hoverBackgroundColor": [
#                             "#1B7F31",
#                             "#787A79",
#                         ]
#                     }]
#                 }

#     return jsonify(data_dict)

# # Donut chart number 3 profile page

# def find_harvest_three(user):
#     """Will find the harvests,
#       will return the total harvest,
#       and will find the remaining harvest"""


#     remaining_harvest = .25
#     harvested = .75

#     return remaining_harvest, harvested

# @app.route('/giv_donut_3.json')
# def giv_donut_3():
#     """Return data about Circlet."""

#     # print remaining harvest, harvest
#     data_dict = {
#                 "labels": [
#                     "Remaining Harvest",
#                     "Harvested",
#                 ],
#                 "datasets": [
#                     {
#                         "data": [remaining_harvest, harvested],
#                         "backgroundColor": [
#                             "#20993A",
#                             "#D2D4D3",
#                         ],
#                         "hoverBackgroundColor": [
#                             "#1B7F31",
#                             "#787A79",
#                         ]
#                     }]
#                 }

#     return jsonify(data_dict)


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
    user_circlets = get_user_circlets(circlet_id)
    for uc in user_circlets:
        if not uc.monthly_payment:
            return render_template('confirmation_pending.html', user_circlets=user_circlets)
    return render_template('confirm.html', user_circlets=user_circlets, circlet_id=circlet_id)

@app.route('/post_final_confirmation/<circlet_id>', methods=['POST'])
def post_final_confirmation(circlet_id):
    if 'user_id' not in session:
        return 'you need to be logged in to post final confirmation'
    set_confirmed(session['user_id'], circlet_id)
    user_circlets = get_user_circlets(circlet_id)
    for uc in user_circlets:
        print(uc)
        if not uc.is_confirmed:
            return render_template('confirm.html', user_circlets=user_circlets, circlet_id=circlet_id)
    return redirect('/circlet/{}'.format(circlet_id))



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
