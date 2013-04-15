import os

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
                yield from files(opath, lower, upper, order)
            else:
                yield opath

def open_a(path):
    try:
        return open(path, 'a+')
    except IOError as e:
        if e.errno == errno.ENOENT:
            os.makedirs(os.path.dirname(path))
            return open(path, 'a+')
        raise

def open_r(path):
    try:
        return open(path, 'r')
    except IOError as e:
        if e.errno == errno.ENOENT:
            return io.BytesIO()
        raise
