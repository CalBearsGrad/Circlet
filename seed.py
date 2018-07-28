import bcrypt

from model import User, CreditCards, Circlets


from model import connect_to_db, db
from server import app

def sample_user():
    """ Add sample user to DB """

    print "Sample User"

    password = "123"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    alyssa = User(first_name="George", last_name="Smith", email="gerge@example.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=1)
    db.session.add(alyssa)
    db.session.commit()

def sample_cc():
    """ Add sample cc to DB """

    print "Sample CC"

    cc = CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123")
    db.session.add(cc)
    db.session.commit()


def sample_circlet():
    """ Add sample user to DB """

    print "Sample Circlet"

    circlet = Circlets(created_at='2018-07-29', activated_at='2018-07-29', description="Thing I want to buy", total_amount=100, amount_paid=0, payment_frequency=7, payment_per_interval=10)
    db.session.add(circlet)
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    sample_user()
    sample_cc()
    sample_circlet()

