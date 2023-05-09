import os
import time
from typing import List
from base import OUTPUT_DIR
from MelodieTable import Table
from sqlalchemy import Integer, create_engine

XLSFILE = os.path.join(os.path.dirname(
    __file__), "data", "params.xlsx")

XLSFILE_TO_WRITE = os.path.join(OUTPUT_DIR, "params.xlsx")
CSVFILE_TO_WRITE = os.path.join(OUTPUT_DIR, "params.csv")
SQLITE_FILE = os.path.join(OUTPUT_DIR, "out.sqlite")


def test_create_table():
    table = Table.from_dicts("mytable", {"a": Integer(), "b": Integer()}, [
        {"a": i, "b": i} for i in range(1000)])

    row = table.find_one(lambda obj: obj.a == 999)
    assert row.a == 999


def test_load_table():
    table = Table.from_file(XLSFILE, {})
    print(table.data[-1])


def test_write_table():
    from Melodie import run_profile
    l = ['a', 'b', 'c', 'd', '__e', 'f', 'g']
    table = Table.from_dicts("mytable", {k: Integer() for k in l}, [
        {k: i for k in l} for i in range(2000)])
    t0 = time.time()
    table.to_file_with_codegen(CSVFILE_TO_WRITE)

    t1 = time.time()
    print('write_table_time', t1-t0)


class Agent:
    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b


def collect(agents: List[Agent], props: List[str], table: Table):
    table.data = []
    for agent in agents:
        r = table.row_cls(**{prop_name: getattr(agent, prop_name)
                             for prop_name in props})
        table.data.append(r)


def collect2(agents: List[Agent], collector, table: Table):
    table.clear()
    for agent in agents:
        table.data.append(collector(agent, table))


collector_template = """
def collector3(a, table:Table):
    r = table.new_row()
{assignments}
    return r
"""


def create_collector(properties: List[str]):
    code = collector_template.format(assignments="\n".join(
        ["    "+f"r.{prop} = a.{prop}" for prop in properties]))
    local_vars = {}
    exec(code, None, local_vars)
    return local_vars['collector3']


def test_to_database():
    engine = create_engine("sqlite:///"+SQLITE_FILE)
    agents = [{"a": i, "b": i} for i in range(1000)]
    table = Table.from_dicts(
        'aaaaaa', {"a": Integer(), "b": Integer()}, agents)
    # table.from_dicts()

    table.to_database(engine, "aaaaaa")


def test_data_collect():
    agents = [Agent(i, i*2) for i in range(1000)]
    table = Table('aaaaaa', {"a": Integer(), "b": Integer()})
    # print(create_collector(["a", "b"]))

    def collector3(a, table: Table):
        r = table.new_row()
        r.a = a.a
        r.b = a.b
        return r
    N = 100
    t0 = time.time()
    for i in range(N):
        collect(agents, ['a', 'b'], table)
    t1 = time.time()
    table.row_cls
    for i in range(N):
        collect2(agents, lambda a, table: table.row_cls(a=a.a, b=a.b), table)
    t2 = time.time()
    for i in range(N):
        collect2(agents, collector3, table)
    t3 = time.time()
    collector_func = create_collector(['a', 'b'])
    for i in range(N):
        collect2(agents, collector_func, table)
    t4 = time.time()
    print(t1-t0, t2-t1, t3-t2, 'dynamically-created-collector', t4-t3)

def test_indicing():
    agents = [{"a": i, "b": i} for i in range(1000)]
    table = Table.from_dicts(
        'aaaaaa', {"a": Integer(), "b": Integer()}, agents)
    assert table.iat[50, 'a'] == 50