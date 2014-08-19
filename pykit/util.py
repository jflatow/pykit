
def disfix(prefix, string):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string

def number(n, b=10, A='0123456789abcdefghijklmnopqrstuvwxyz'):
    if n == 0 or b < 2:
        return A[0]
    return number(n // b, b, A).lstrip(A[0]) + A[n % b]

def slit(string, i=0):
    return string[:i], string[i:]
