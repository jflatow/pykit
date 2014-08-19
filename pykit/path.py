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

def peek(iter):
    try:
        return next(iter)
    except StopIteration:
        return None

def head(path):
    return peek(walk(path))

def last(path):
    return peek(walk(path, order=lambda p: sorted(p, reverse=True)))

def openr(path, mode='rb'):
    try:
        return open(path, mode)
    except IOError as e:
        if e.errno == errno.ENOENT:
            return io.BytesIO()
        raise

def openw(path, mode='w+b', dirs=True):
    try:
        return open(path, mode)
    except IOError as e:
        if e.errno == errno.ENOENT and dirs:
            os.makedirs(os.path.dirname(path))
            return open(path, mode)
        raise

def write(path, data, **opts):
    temp = opts.get('temp', path + '.p')
    dirs = opts.get('dirs', True)
    with openw(temp, dirs=dirs) as f:
        f.write(data)
    os.rename(temp, path)
