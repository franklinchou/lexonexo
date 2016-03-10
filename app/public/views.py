from flask import render_template,\
    redirect

from . import public

from ..models import User

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
