
import time
import base
from MelodieTable.table_objects import Table, TableRow


class TableRowCls4WriteTable(TableRow):
    a: int
    b: int
    c: int
    d: int

l = [('a', int), ('b', float), ('c', str), ('d', bool)]
def test_write_table():
    
    table = Table.from_dicts(TableRowCls4WriteTable, [
        {k[0]: k[1](0) for k in l} for i in range(2000000)])
    t0 = time.time()
    table.to_file_with_codegen("out.csv")
    t1 = time.time()
    print('write_table_time', t1-t0)


def test_write_cpython():
    import pandas as pd
    table = pd.DataFrame([
        {k[0]: k[1](0) for k in l} for i in range(2000000)])

    t0 = time.time()
    table.to_csv("out.csv", )
    t1 = time.time()
    print('write_table_time', t1-t0)


if base.is_pypy():
    test_write_table()
else:
    test_write_cpython()
