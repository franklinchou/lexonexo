from contextlib import contextmanager

from random import random
from time import sleep

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
