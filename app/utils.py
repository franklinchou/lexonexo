from contextlib import contextmanager

from random import random
from time import sleep

#------------------------------------------------------------------------------
# For use w/`import_submodules()`
#------------------------------------------------------------------------------
import pkgutil
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# `import_submodules()`
#------------------------------------------------------------------------------
def import_submodules(context, root_module, path):
    for loader, name, _ in pkgutil.walk_packages(path, root_module + '.'):
        module = loader.find_module(name).load_module(name)
        pkg_names = getattr(module, '__all__', None)
        for k, v in vars(module).items():
            if not k.startswith('_') and (pkg_names is None or k in pkg_names):
                context[k] = v
        context[name] = module
#------------------------------------------------------------------------------

DEFAULT_LOCK_TIMEOUT = 5

class UnableToLockException(Exception):
    pass

@contextmanager
def lock(conn, lock_key, timeout = DEFAULT_LOCK_TIMEOUT, expire = None, nowait = False):
    if expire is None:
        expire = timeout

    delay = 0.01 + random() / 10
    attempt = 0

    max_attempts = timeout / delay

    got_lock = None

    while not got_lock and attempt < max_attempts:
        pipe = conn.pipeline()
        pipe.setnx(lock_key, '')
        pipe.expire(lock_key, expire)
        got_lock = pipe.execute()[0]

        if not got_lock:
            if nowait:
                break
            sleep(delay)
            attempt = attempt + 1

    print("Attempting to acquire lock on %s", lock_key)

    if not got_lock:
        raise UnableToLockException("Unable to acquire lock on %s", (lock_key,))

    try:
        yield
    finally:
        print("Releasing lock on %s", (lock_key,))

        try:
            conn.delete(lock_key)
        except:
            print("Unanticipated exception occured")


