# Helper script to create database from fresh install

# @TODO:
#   Integrate into manage.py script

from manage import app

from app import db

from flask import current_app

def mkdb(testing):

    total_query = 'SELECT COUNT(id) FROM users'

    # create application context
    with app.app_context():
        if (current_app == None):
            print("Unexpected failure to create application")
        assert(app.config['SQLALCHEMY_DATABASE_URI'] != None)
        db.create_all()
        before = db.engine.execute(total_query)
        assert(before == 0)

#------------------------------------------------------------------------------
        # Add dummy row
#------------------------------------------------------------------------------

        if (testing == True):
            db.engine.execute(
                'INSERT INTO users(email) VALUES(\'franklin.chou@student.shu.edu\')'
            )

            after = db.engine.execute(total_query)
            assert(after == 1)

        if (testing == False):
            db.session.commit()

if __name__ == '__main__':
    from sys import argv

    if (len(argv) == 0 and arv[0] == 'test'):
        mkdb(testing=True)
    else:
        mkdb(testing=False)
