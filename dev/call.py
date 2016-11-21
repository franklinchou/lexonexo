from task import get_points

from automation_exception import InvalidLanding

if __name__ == "__main__":
    try:
        # get_points('franklin.chou', '4107htkdh3xG')
        get_points('franklinchou', 'Fillmore234!!')
    except InvalidLanding as e:
        raise
