import bcrypt

from model import User


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




if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    sample_user()
