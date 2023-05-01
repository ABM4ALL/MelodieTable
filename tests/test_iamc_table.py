import time
from base import is_pypy
from MelodieTable import PyAMTable
from sqlalchemy import Integer
import os
# if not is_pypy():
#     import pyam
PATH = os.path.join(os.path.dirname(
    __file__), "data", "pyam_tutorial_data.csv")


def test_filter():

    table = PyAMTable.from_file(PATH, {})
    # if not is_pypy():
    #     pyam_table = pyam.IamDataFrame(data=PATH)
    #     t1 = time.time()
    #     for i in range(100):
    #         pyam_table.filter(model="MESSAGE*")
    #     t2 = time.time()
    #     pyam_time = t2 - t1
    t0 = time.time()
    for i in range(100):
        new_table = table.filter(lambda row: row.Model.startswith("MESSAGE"))
    t1 = time.time()
    print(new_table, t1 - t0)
    print(new_table.find_one_with_index(lambda obj: True))


def test_create_table():
    table = PyAMTable.from_file(os.path.join(os.path.dirname(
        __file__), "data", "pyam_tutorial_data.csv"), {})
    assert len(table) == 1026
