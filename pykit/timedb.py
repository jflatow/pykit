import datetime
import itertools
import os

import pykit.path

fpath = {'second': '%Y/%m/%d/%H/%M/%S',
         'minute': '%Y/%m/%d/%H/%M',
         'hour':   '%Y/%m/%d/%H',
         'day':    '%Y/%m/%d',
         'month':  '%Y/%m',
         'year':   '%Y'}

ftime = {'second': '%Y/%m/%d %H:%M:%S',
         'minute': '%Y/%m/%d %H:%M',
         'hour':   '%Y/%m/%d %H',
         'day':    '%Y/%m/%d',
         'month':  '%Y/%m',
         'year':   '%Y'}


def read_until(file, byte, buf=''):
    while True:
        b = file.read(1)
        if b == byte or not b:
            return buf
        buf += b

class TimeDB(object):
    def __init__(self, root, **opts):
        self.root = root
        self.opts = opts

    def __iter__(self):
        return self.between()

    def path(self, time):
        return os.path.join(self.root, time.strftime(fpath[self.opts.get('by', 'day')]))

    def format(self, time, data):
        return '%s %d ' % (time.strftime(ftime['second']), len(data)) + data + '\n'

    def lower(self, time):
        return self.path(time) if time else None

    def upper(self, time):
        return self.path(time) + '~' if time else None

    def log(self, data, time=None):
        time = time or datetime.datetime.now()
        file = pykit.path.openw(self.path(time), 'a+')
        file.write(self.format(time, data))

    def items(self, file):
        for n in itertools.count():
            timestamp = file.read(19)
            if file.read(1) != ' ':
                return
            uniq = '%s-%d' % (timestamp, n)
            size = int(read_until(file, ' '))
            data = file.read(size)
            if file.read(1) != '\n':
                return
            yield uniq, datetime.datetime.strptime(timestamp, ftime['second']), data

    def paths(self, t1=None, t2=None, reverse=False):
        def order(paths):
            return [p for p in sorted(paths, reverse=reverse) if p.isdigit()]
        return pykit.path.walk(self.root, lower=self.lower(t1), upper=self.upper(t2), order=order)

    def between(self, t1=None, t2=None, **kwds):
        for path in self.paths(t1=t1, t2=t2, **kwds):
            for uniq, time, data in self.items(pykit.path.openr(path, 'r')):
                if (t1 is None or time >= t1) and (t2 is None or time <= t2):
                    yield uniq, time, data
