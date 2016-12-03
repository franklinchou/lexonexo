#------------------------------------------------------------------------------
# Franklin Chou
# 03 DEC 2016
# REVISION 3
#------------------------------------------------------------------------------

from . import main

# DEPRECATE
# from app.jobs import lnq

from ..models import User

from flask import render_template,\
    current_app

from flask_login import login_required,\
    current_user

