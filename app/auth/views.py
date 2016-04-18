from flask import render_template,\
    redirect,\
    request,\
    url_for,\
    flash

from flask.ext.login import login_user,\
    logout_user,\
    login_required

from app import queue_instance

from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(
                # request.args.get('next') or url_for('public.index')
                request.args.get('next') or url_for('main.ran')
            )
        # flash()
    return render_template(
        'auth/login.html',
        form = form
    )

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    # flash()
    return redirect(url_for('public.index'))

def confirm_lexis_login(la_username, la_password):
    from ..main.runner import VerifyRunner
    with VerifyRunner(la_username, la_password) as r:
        r.verify()

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

@auth.route('/register', methods = ['GET','POST'])
def register_and_enq():
    '''
        Register user and enqueue in task list
    '''
    registered = False
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email = form.email.data,
            password = form.password.data,
            la_username = form.lexis_username.data,
            la_password = form.lexis_password.data
        )

        try:
            confirm_lexis_login(
                form.lexis_username.data,
                form.lexis_password.data
            )
        except Exception:
            return redirect(url_for('auth.register_failure'))
        else:
            try:
                db.session.add(user)
                registered = True
            except:
                print("Error: unable to append user information to database.")

#------------------------------------------------------------------------------
    # Add to automation queue
#------------------------------------------------------------------------------
    if registered is True:
        pass
#------------------------------------------------------------------------------

        return redirect(url_for('auth.register_success'))

    return render_template(
        'auth/register.html',
        form = form
    )
