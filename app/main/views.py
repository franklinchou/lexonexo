from . import main

from . runner import Runner

from ..models import User

from flask import render_template,\
    current_app

# @main.route('/myrunner')
def run():

    from datetime import datetime

    user = User.query.filter_by(email='franklin.chou@student.shu.edu').first()
    # user = User.query.filter_by(id=2).first()

    with Runner(user.la_username, user.la_password_encrypted) as r:
        r.login()
        r.query()
        if (r.passed == True):
            user.last_run = datetime.utcnow()

    return render_template(
        'runner.html'
    )
