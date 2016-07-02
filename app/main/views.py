from . import main

from app.jobs import lnq

from ..models import User

from flask import render_template,\
    current_app

from flask_login import login_required,\
    current_user

@main.route('/ran')
@login_required
def ran():

    last_run = current_user.last_run

    return render_template(
        'ran.html',
        last_run = last_run
    )
