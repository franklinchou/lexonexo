from task import get_points

from automation_exception import InvalidLanding

from datetime import datetime


if __name__ == "__main__":

    MODE = 2

    if MODE == 0:
        try:
            get_points('franklin.chou', '4107htkdh3xG')
            get_points('franklinchou', 'Fillmore234!!')
        except InvalidLanding as e:
            raise
    elif MODE == 1:

        # Work around for minimal testing reproduction purposes, 25 OCT 2016
        # Import all modules in the app/ directory



        # from models import User

        time_threshold = datetime.now() - timedelta(hours=2)
        try:
            u = User.query.filter_by(last_run=time_threshold)
            for record in u:
                print(record)
        except:
            raise
