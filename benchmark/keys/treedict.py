import time
from typing import Callable, Dict, List, Optional, Tuple, Union
from MelodieTable import Table, TableRow
import random


class HashIndicedDict:
    def __init__(self) -> None:
        self.cache = {}

    def store(self, k, v):
        self.cache[k] = v

    @staticmethod
    def from_table(table: Table, index_columns: List[str], row_value_getter: Callable):
        new_dict = HashIndicedDict()

        def f(row: TableRow):
            vals = tuple((getattr(row, index_colname)
                         for index_colname in index_columns))
            new_dict.cache[vals] = row_value_getter(row)

        table.apply(f)
        return new_dict

    def get_items(self, indicer: Tuple[int, int, int]):
        if indicer in self.cache:
            return self.cache[indicer]
        else:
            raise ValueError(f"Element not found for {indicer}")


SEARCHER_FUNC_BASE = """
def searcher(self, tup):
    {tuple_unpack_vars} = tup

    {body}
    
    return {retval}
"""
DICT_ITEM_PATTERN = """
    {ret} = {container}.get({val})
    if {ret} is None:
        return None
"""


def gen_searcher(indicer_len: int):
    body = ""
    for i in range(indicer_len):
        body += DICT_ITEM_PATTERN.format(
            ret=f"tmp_{i}", container=f"tmp_{i-1}" if i >= 1 else "self.cache_tree", val=f"val_{i}")
    code = SEARCHER_FUNC_BASE.format(
        tuple_unpack_vars=", ".join([f"val_{i}" for i in range(indicer_len)]),
        body=body,
        retval=f"tmp_{indicer_len-1}"
    )
    print(code)
    locals_ = {}
    exec(code, None, locals_)
    return locals_['searcher']


CacheTreeType = Dict[int, Union["CacheTreeType", List]]


class TreeIndicedDict:
    def __init__(self) -> None:
        self.cache_tree: CacheTreeType = {}  # id, region, sector
        _search_cache_tree = gen_searcher(3)
        self.search_cache_tree = lambda tup: _search_cache_tree(self, tup)

    def store(self, tup: Tuple[int, int, int], data):
        node = self.cache_tree
        parent_node: Optional[CacheTreeType] = None
        item: int = -1
        for item in tup:
            parent_node = node
            node: Optional[CacheTreeType] = node.get(item)
            if node is None:
                node = {}
                parent_node[item] = node
        if parent_node is not None:
            parent_node[item] = data
        else:
            raise ValueError("Cache tree is empty.")

    @staticmethod
    def from_table(table: Table, index_columns: List[str], row_value_getter: Callable):
        new_dict = TreeIndicedDict()

        def f(row: TableRow):
            vals = tuple((getattr(row, index_colname)
                         for index_colname in index_columns))
            new_dict.store(vals, row_value_getter(row))

        table.apply(f)
        return new_dict

    def get_items(self, tup):
        v = self.search_cache_tree(tup)
        if v is not None:
            return v
        else:
            raise ValueError(f"No value for {tup}")


class MyTableRow(TableRow):
    id: int
    region: int
    sector: int
    value: float


table = Table.from_dicts(MyTableRow,
                         [{"id": i % 50, "region": i % 20, "sector": i % 10, "value": random.random()}
                          for i in range(100)]
                         )

hd = HashIndicedDict.from_table(
    table, ['id', 'region', 'sector'], lambda obj: obj.value)
td = TreeIndicedDict.from_table(
    table, ['id', 'region', 'sector'], lambda obj: obj.value)


def test_cached(d):
    t0 = time.time()
    for j in range(100000):
        for i in range(100):
            d.get_items((i % 50, i % 20, i % 10))
    t1 = time.time()
    return t1-t0


print("hash_cached", test_cached(hd), "tree_cached", test_cached(td))

with open("out.json", "w") as f:
    f.write(str(td.cache_tree))
