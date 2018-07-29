import bcrypt

from model import User, CreditCards, Circlets, UserCirclets


from model import connect_to_db, db
from server import app

def sample_user():
    """ Add sample user to DB """
    password = "123"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users = [
        User(first_name="Madeline", last_name="Sanchez", email="madeline@example.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=1),
        User(first_name="Allison", last_name="Kim", email="a@example.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=2),
        User(first_name="Bo", last_name="B", email="b@example.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=3),
        User(first_name="Cy", last_name="C", email="c@example.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=4),
        User(first_name="De", last_name="D", email="d@example.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=5),
        User(first_name="Em", last_name="E", email="e@example.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=6),
        User(first_name="Fa", last_name="F", email="f@example.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=7),
        User(first_name="Gu", last_name="G", email="g@example.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=8),
        User(first_name="Dave", last_name="Galbraith", email="davidvgalbraith@gmail.com", password=hashed_pw, created_at='2018-07-28', reliability=10, ranking=10, credit_card_id=9),
        User(first_name="Marijane", last_name="Castillo", email="MarijaneCastillo@gmail.com", password=hashed_pw, created_at='2018-07-29', reliability=10, ranking=10, credit_card_id=10)

    ]

    for user in users:
        db.session.add(user)
    db.session.commit()

def sample_cc():
    """ Add sample cc to DB """

    print "Sample CC"

    cc = CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123")
    db.session.add(cc)
    cards = [
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123"),
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123"),
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123"),
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123"),
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123"),
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123"),
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123"),
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123"),
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123"),
        CreditCards(number="123456", exp_month= "01", exp_year="20", cvc="123")
    ]
    for cc in cards:
        db.session.add(cc)
    db.session.commit()


def sample_circlet():
    """ Add sample circlet to DB """

    print "Sample Circlet"

    circlet = Circlets(created_at='2018-07-29', due_date='2018-07-29', activated_at='2018-07-29', description="Thing I want to buy", total_amount=100, amount_paid=0, payment_per_interval=10)
    db.session.add(circlet)
    db.session.commit()

def sample_uc():
    """ Add sample user-circlet to DB """

    print "Sample UC"

    uc = UserCirclets(user_id=1, circlet_id=1)
    db.session.add(uc)
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    sample_cc()
    sample_user()
    sample_circlet()
    sample_uc()

