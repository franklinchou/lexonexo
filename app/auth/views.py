from flask import render_template,\
    redirect,\
    request,\
    url_for,\
    flash

from flask_login import login_user,\
    logout_user,\
    login_required

# from app import queue_instance

from app import db

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

def confirm_lexis_login(la_username, la_password):
    from ..jobs.lnq import VerifyRunner
    print ('here')
    with VerifyRunner(la_username, la_password) as r:
        r.verify()

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
        except Exception as e:
            print(e)
            return redirect(url_for('auth.register_failure'))
        else:
            db.session.add(user)
            registered = True

        return redirect(url_for('auth.register_success'))

    return render_template(
        'auth/register.html',
        form = form
    )
