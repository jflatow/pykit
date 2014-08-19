import os
import struct

from . import path, util

MAGIC = 'logfile:'
OZERO = 42

def int_to_path(int, depth=2, base=36):
    num = util.number(int, base).rjust(2 * depth, '0')
    return os.path.join(*(x + y for x, y in zip(num[::2], num[1::2])))

def path_to_int(path, depth=2, base=36):
    unit = base * base
    p, i = pow(unit, depth - 1), 0
    for part in path.split('/'):
        i += int(part, base) * p
        p /= unit
    return i

def id_to_str(id, inf='.'):
    return '%s:%d' % (id[0].replace('/', '.'), id[1]) if id else inf

def str_to_id(s):
    if len(s) == 1:
        return None
    p, o = s.split(':')
    return p.replace('.', '/'), int(o)

def tag((a, b)):
    return '%s-%s' % (id_to_str(a), id_to_str(b, ':'))

def untag(tag):
    a, b = tag.split('-')
    return str_to_id(a), str_to_id(b)

def rel(root, path):
    return util.disfix(root, path).strip('/')

def last(root, depth):
    return path.last(root) or os.path.join(root, int_to_path(0, depth))

def uint32(bytes):
    value, = struct.unpack('>L', bytes)
    return value

def uint128(bytes):
    hi, lo = struct.unpack('>QQ', bytes)
    return (hi << 64) + lo

def pread(file, offs, size):
    offs = file.seek(offs)
    return file.read(size)

def header(file):
    head = pread(file, 0, OZERO)
    magic, rest = util.slit(head, len(MAGIC))
    assert magic == MAGIC, magic
    c0, rest = util.slit(rest, 16)
    sc, rest = util.slit(rest, 1)
    assert sc == ';', sc
    c1, rest = util.slit(rest, 16)
    nl, rest = util.slit(rest, 1)
    assert nl == '\n', nl
    assert rest == '', rest
    return uint128(c0), uint128(c1)

def entry(file, offs):
    size = uint32(file.read(4))
    data, nl = util.slit(file.read(size + 1), size)
    assert nl == '\n', nl
    return data, offs + size + 5

def entries(file, (rel, offs), lower=None, upper=None):
    while upper is None or (rel, offs) < upper:
        try:
            data, offs_ = entry(file, offs)
            if (rel, offs) >= lower:
                yield ((rel, offs), (rel, offs_)), data
            offs = offs_
        except:
            return

class Log(object): # NB: currently read-only
    def __init__(self, root, **opts):
        self.root = root
        self.opts = opts
        self.depth = opts.get('depth', 2)
        self.limit = opts.get('limit', 8 << 20)
        self.path = rel(root, last(root, self.depth))
        self.offs = 'eof'
        self.file = path.openr(self.abs(self.path))

    def __iter__(self):
        return self.range()

    def verify(self):
        c0, c1 = header(self.file)
        nl_eof = pread(self.file, max(c0, c1), 2)
        assert nl_eof == '\n', nl_eof
        self.offs = max(c0, c1)

    def abs(self, p):
        return os.path.join(self.root, p)

    def rel(self, p):
        return rel(self.root, p)

    def lower(self, id):
        return id or (self.rel(path.head(self.root)), OZERO)

    def upper(self, id):
        return id or (self.path, self.offs)

    def range(self, lo=None, hi=None, start=OZERO, **kwds):
        lower = plo, _ = self.lower(lo)
        upper = phi, _ = self.upper(hi)
        for p in path.walk(self.root, lower=self.abs(plo), upper=self.abs(phi + '~')):
            with path.openr(p) as f:
                f.seek(start)
                for e in entries(f, (self.rel(p), start), lower=lower, upper=upper):
                    yield e
