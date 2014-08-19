import io
import os
import errno

def ls(path):
    try:
        return os.listdir(path)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return []
        raise

def walk(path, lower=None, upper=None, order=sorted):
    for name in order(ls(path)):
        opath = os.path.join(path, name)
        if (lower is None or opath >= lower) and (upper is None or opath < upper):
            if os.path.isdir(opath):
                for p in walk(opath, lower, upper, order):
                    yield p
            else:
                yield opath
        elif lower and lower.startswith(opath):
            if os.path.isdir(opath):
                for p in walk(opath, lower, upper, order):
                    yield p

def head(path):
    return next(walk(path))

def last(path):
    return next(walk(path, order=lambda p: sorted(p, reverse=True)))

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
