from typing import IO
import os

try:
    import fcntl

    _lock_file_path = '/var/lock/outdoor_leds.lockf'

    def _lock_file(f: IO):
        if f.writable():
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock_file(f: IO):
        if f.writable():
            fcntl.lockf(f, fcntl.LOCK_UN)

except ModuleNotFoundError:
    raise

class AppMutex:
    def __init__(self, path =_lock_file_path):
        self.file = open(path, mode='w')
        _lock_file(self.file)

    def __enter__(self):
        self.file.write(str(os.getpid()))
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        _unlock_file(self.file)
        self.file.close()
        return (exc_type is None)