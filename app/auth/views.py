#------------------------------------------------------------------------------
# Franklin Chou
#------------------------------------------------------------------------------

from flask import render_template,\
    redirect,\
    request,\
    url_for,\
    flash

from flask_login import login_user,\
    logout_user,\
    login_required

from .forms import LoginForm,\
    RegistrationForm

from sqlalchemy.sql.expression import exists

from app import db
from app.jobs.tasks import get_points
from app.jobs.automation_exception import InvalidLogin
from app.jobs.automation_exception import InvalidLanding

from . import auth
from ..models import User
from datetime import datetime

@auth.route('/regd')
def register_success():
    return render_template(
        'auth/register_success.html'
    )

@auth.route('/fail')
def register_failure():
    return render_template(
        'auth/register_failure.html'
    )


#------------------------------------------------------------------------------
# `last_run` insertion point
#------------------------------------------------------------------------------

@auth.route('/register', methods = ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email = form.email.data,
            # password = form.password.data,
            la_username = form.lexis_username.data,
            la_password = form.lexis_password.data
        )

        try:
            get_points(form.lexis_username.data, form.lexis_password.data)
        except InvalidLogin as e:
            return redirect(url_for('auth.register_failure'))
        except InvalidLanding as e:
            # @TODO: Build page for general error
            pass
        else:
            user.last_run = datetime.now()
            db.session.add(user)
            db.session.flush()
            __verify_record__(user.id)

        return redirect(url_for('auth.register_success'))

    return render_template(
        'auth/register.html',
        form = form
    )

'''
    Will verify that the record exists (by the auto generated unique id)
    _AND_ attempts to determine that the `last_run` field has been appropriately set

    Query as to whether this sort of verfication is necessary in production models.
    Balance the cost of a database query versus the benefit of sanity checking an individualized record.
'''
def __verify_record__(user_id):
    try:
        (user_record, ), = db.session.query(
                exists().where(User.id==user_id).where(User.last_run.isnot(None))
        )
        if user_record == False:
            # @TODO: Build page for general error & log custom exception
            raise Exception
        # Persists change to database
        db.session.commit()
    except Exception as e:
        raise
