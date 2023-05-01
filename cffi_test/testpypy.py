# from _pi.lib import test

import cffi as cf

ffi=cf.FFI()

lib=ffi.dlopen("test111.pyd")

ffi.cdef("""
            int test(int n);
""")

import time


def test2(n):
    s = 0
    for i in range(n):
        if i % 5 == 0 or i % 1145 == 0:
            s += 1
        else:
            s -= 1
    return s


lib.test(10000)
test2(10000)
t0 = time.time()
for i in range(10000):
    lib.test(50000)
t1 = time.time()
for i in range(10000):
    test2(50000)

t2 = time.time()
print(t1 - t0, t2-t1)
