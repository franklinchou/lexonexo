
    import sys
    from glob import glob
    from os import listdir
    from os.path import dirname,\
            abspath,\
            isdir,\
            join

    parent_dir = dirname(abspath(__file__))

    project_dir = dirname(parent_dir)

    # Include models?
    sys.path.extend(glob(project_dir + "/*.py"))

    for i in listdir(project_dir):
        file_path = join(project_dir, i)
        if isdir(file_path):
            sys.path.extend(glob(file_path + "/*.py"))

    print(sys.path)

    from autolex.app.models import User
