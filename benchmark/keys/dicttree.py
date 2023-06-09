import sys
sys.path.append("../..")

from sqlalchemy import Integer
import json
from MelodieTable import Table, TableRow, column_meta
from typing import Dict, List, Optional, Tuple, Union
import time



class Key:
    def __init__(self, id_: int, region: int, sector: int) -> None:
        self.id = id_
        self.region = region
        self.sector = sector


class HashCachedDict:
    def __init__(self, table: Table) -> None:
        self.table: Table = table
        self.cache = {}

    def get_items(self, indicer: Tuple[int, int, int]):
        if indicer in self.cache:
            return self.cache[indicer]
        else:
            items = self.table.find_all(
                lambda obj: obj.id == indicer[0] and obj.region == indicer[1] and obj.region == indicer[2])
            self.cache[indicer] = items
            return items


INTNAN = -2**62  # 4.61*10^18, standing for not-a-number value of integer.


SEARCHER_FUNC_BASE = """
def searcher(self, tup):
    {tuple_unpack_vars} = tup

    {body}
    
    return {retval}
"""
DICT_ITEM_PATTERN = """
    {ret} = {container}.get({val} if {val} is not None else INTNAN)
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


class TreeCachedDict:
    def __init__(self, table: Table) -> None:
        self.table: Table = table
        self.cache_tree: CacheTreeType = {}  # id, region, sector
        _search_cache_tree = gen_searcher(3)
        self.search_cache_tree = lambda tup: _search_cache_tree(self, tup)

    def update_cache_tree_2(self, tup: Tuple[int, int, int], data):
        node = self.cache_tree
        parent_node: Optional[CacheTreeType] = None
        item: int = INTNAN
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

    
    def get_items(self, tup):
        def process_tuple(t):
            q1, q2, q3 = t
            v1 = INTNAN if q1 is None else q1
            v2 = INTNAN if q2 is None else q2
            v3 = INTNAN if q3 is None else q3
            assert isinstance(v1, int)
            assert isinstance(v2, int)
            assert isinstance(v3, int)
            return (v1, v2, v3)
        # def condition()
        v1, v2, v3 = process_tuple(tup)
        new_tup = (v1, v2, v3)
        v = self.search_cache_tree(new_tup)
        if v is not None:
            return v
        else:
            data = self.table.find_all(
                lambda obj: (v1 == INTNAN or obj.id == v1) and (v2 == INTNAN or obj.region == v2) and (v3 == INTNAN or obj.sector == v3))
            self.update_cache_tree_2(new_tup, data)
            return data


class MyTableRow(TableRow):
    id: int
    region: int
    sector: int


table = Table.from_dicts(MyTableRow,
                         [{"id": i % 50, "region": i % 20, "sector": i % 10}
                          for i in range(100)]
                         )

hd = HashCachedDict(table)
td = TreeCachedDict(table)

def test_cached(d):
    t0 = time.time()
    for j in range(100000):
        for i in range(100):
            d.get_items((i % 50, i % 20, i % 10))
        for i in range(100):
            d.get_items((i % 50, None, i % 10))
        for i in range(100):
            d.get_items((i % 50, None, i*5))
    t1 = time.time()
    return t1-t0


print("hash_cached", test_cached(hd), "tree_cached", test_cached(td))

with open("out.json", "w") as f:
    f.write(str(td.cache_tree))
