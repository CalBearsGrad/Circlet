"""Models and database functions for Foraging Foodie project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions


class User(db.Model):
    """ Users of Circlet website. """

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(75), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    reliability = db.Column(db.Integer, nullable=False)
    ranking = db.Column(db.String(20), nullable=False)
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.credit_card_id'), nullable=False, unique=True)

    # Define a relationship
    credit_card = db.relationship("CreditCards", backref=db.backref("user"))
    circlet = db.relationship("Circlets", secondary="users_circlet", backref=db.backref("user"))



    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id={} first_name={} last_name={} email={}>".format(
                                                                        self.user_id,
                                                                        self.first_name,
                                                                        self.last_name,
                                                                        self.email
                                                                        )



class CreditCards(db.Model):

    __tablename__ = "credit_cards"

    credit_card_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    number = db.Column(db.String(30), nullable=False)
    exp_month = db.Column(db.String(2), nullable=False)
    exp_year = db.Column(db.String(2), nullable=False)
    cvc = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<CreditCards cc={} number={} exp_month={} exp_year={}>".format(
                                                                        self.credit_card_id,
                                                                        self.number,
                                                                        self.exp_month,
                                                                        self.exp_year
                                                                        )



class Circlets (db.Model):

    __tablename__ = "circlets"

    circlet_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    activated_at = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(50), nullable=True)
    goal_name = db.Column(db.String(50), nullable=True)
    total_amount = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Integer, nullable=False)
    payment_per_interval = db.Column(db.Integer, nullable=True)
    is_complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Circlet created_at={} description={} total_amount={} amount_paid={}, payment_per_interval={}>".format(
                                                                        self.created_at,
                                                                        self.description,
                                                                        self.total_amount,
                                                                        self.amount_paid,
                                                                        self.payment_per_interval
                                                                        )
    def asdict(self):
        return {
            'circlet_id': self.circlet_id,
            'created_at': self.created_at,
            'due_date': self.due_date,
            'activated_at': self.activated_at,
            'description': self.description,
            'goal_name': self.goal_name,
            'total_amount': self.total_amount,
            'amount_paid': self.amount_paid,
            'payment_per_interval': self.payment_per_interval,
            'is_complete': self.is_complete,
        }

class UserCirclets (db.Model):

    __tablename__ = "users_circlet"

    uc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    circlet_id = db.Column(db.Integer, db.ForeignKey('circlets.circlet_id'), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    monthly_payment = db.Column(db.Float, nullable=True)

    user = db.relationship("User", backref="user_circlets")
    circlet = db.relationship('Circlets', backref="user_circlets")

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<UserCirclets uc_id={} user_id={} circlet_id={} is_confirmed={}>".format(
            self.uc_id,
            self.user_id,
            self.circlet_id,
            self.is_confirmed
        )

def get_user(id):
    return db.session.query(User).get(id)

def get_circlet(id):
    return db.session.query(Circlets).get(id)

def create_goal_circlet(goal_name, description, goal_total, due_date):
    c = Circlets(
        description=description, goal_name=goal_name, total_amount=goal_total,
        due_date=due_date, created_at=datetime.now(), amount_paid=0
    )
    db.session.add(c)
    db.session.commit()
    return c

def get_all_users():
    return db.session.query(User).all()

def insert_user_circlets(circlet_id, user_ids):
    for user_id in user_ids:
        db.session.add(UserCirclets(user_id=user_id, circlet_id=circlet_id))
    db.session.commit()

def get_users_for_circlet(circlet_id):
    circlets = get_user_circlets(circlet_id)
    users = []
    for circlet in circlets:
        users.append(circlet.user)
    return users

def get_user_circlets(circlet_id):
    return db.session.query(UserCirclets).filter_by(circlet_id=circlet_id).all()

def set_user_circlet_info(user_id, circlet_id, monthly_payment):
    print("userId", user_id, "cirlcist", circlet_id)
    circlet = get_user_circlet(user_id, circlet_id)
    if not circlet:
        raise Exception("Missing circlet")
    circlet.monthly_payment = monthly_payment
    db.session.add(circlet)
    db.session.commit()

def set_confirmed(user_id, circlet_id):
    uc = get_user_circlet(user_id, circlet_id)
    uc.is_confirmed = True
    db.session.add(uc)
    db.session.commit()

def get_user_circlet(user_id, circlet_id):
    return db.session.query(UserCirclets).filter_by(circlet_id=circlet_id, user_id = user_id).one()



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///circlet'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
