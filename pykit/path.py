import os
import errno

def ls(path):
    try:
        return os.listdir(path)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return []
        raise

def files(path, lower=None, upper=None, order=sorted):
    for name in order(ls(path)):
        opath = os.path.join(path, name)
        if (lower is None or opath >= lower) and (upper is None or opath < upper):
            if os.path.isdir(opath):
                for file in files(opath, lower, upper, order):
                    yield file
            else:
                yield opath

def openr(path, mode='rb'):
    try:
        return open(path, mode)
    except IOError as e:
        if e.errno == errno.ENOENT:
            return io.BytesIO()
        raise

def openw(path, mode='w+b'):
    try:
        return open(path, mode)
    except IOError as e:
        if e.errno == errno.ENOENT:
            os.makedirs(os.path.dirname(path))
            return open(path, mode)
        raise
