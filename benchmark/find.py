import time
from base import is_pypy
from MelodieTable import Table


def df_getitem(df, b_value):
    val = df.loc[df["b"] == b_value, :]
    # print(val["b"][0])
    # assert val["b"] == M-1


def table_getitem(table: Table, b_value):
    val = table.find_one(lambda o: o.b == b_value)
    # assert val.b == M-1


def on_cpython():
    import pandas as pd
    df = pd.DataFrame(l1)
    t0 = time.time()
    for i in range(N):
        df_getitem(df, M-1)
    t1 = time.time()
    return t1-t0


def on_pypy():
    t0 = time.time()
    table = Table.from_dicts('a', {}, l1)
    for i in range(N):
        table_getitem(table, M-1)
    t1 = time.time()
    return t1-t0


# 当N较大M较小的时候，PyPy比Pandas快
# 当N较小M较大的时候，PyPy比Pandas慢
sizes = [100, 1000, 10000, 100000]
batch_nums = [100, 200, 500, 1000, 2000, 5000, 10000]
with open("out.csv", "a") as f:
    for N in batch_nums:
        for M in sizes:
            l1 = [
                {"a": i, "b": i} for i in range(M)
            ]
            if is_pypy():
                from pypyjit import releaseall
                from gc import collect
                releaseall()
                collect()
                elapsed = on_pypy()
            else:
                elapsed = on_cpython()
            typ = "pypy" if is_pypy() else "cpython"
            print(typ,
                "size", M, "batch_num", N, "time", elapsed)
            f.write(",".join([typ, str(M), str(N),str(elapsed)])+"\n")