from itertools import groupby

def disfix(prefix, string):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string

def number(n, base=10, A='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    if n == 0 or base < 2:
        return A[0]
    elif n < 0:
        return '-' + number(-n, base, A)
    return number(n // base, base, A).lstrip(A[0]) + A[n % base]

def pad(n, width=0, base=10):
    return number(n, base).zfill(width)

def slit(string, i=0):
    return string[:i], string[i:]

def key((k, v)):
    return k

def kvgroup(kviter, key=key):
    for k, kvs in groupby(kviter, key):
        yield k, (v for _k, v in kvs)
