from flask import render_template,\
    redirect

from . import public

from ..models import User

from app import db

@public.route('/')
def index():
    return render_template(
        'index.html'
    )

@public.route('/about')
def about():
    return render_template(
        'about.html'
    )

@public.route('/metrics')
def metrics():

    from app import db
    from sqlalchemy import func

    n = db.session.query(func.count(User.id)).scalar()
    print(n)

    return render_template(
        'metrics.html',
        n = n
    )

@public.route('/privacy')
def privacy():
    return render_template(
       'privacy.html'
    )

@public.route('/source')
def source():
    return redirect(
        'https://github.com/franklinchou/lexonexo'
    )

#------------------------------------------------------------------------------
# Exposure for automated task queue testing
#------------------------------------------------------------------------------
@public.route('/test')
def test_queue():
    from datetime import datetime
    from app.jobs.lnq import Lnq

    test_id = 21
    u = User.query.filter_by(id=test_id).first()

    lnq = Lnq()

    try:
        lnq.delay(u.la_username, u.la_password)
    except Exception:
        raise Exception()
    else:
        # print(datetime.utcnow())
        u.last_run = datetime.utcnow()

    return 'attempting date/time update'
