import sys
sys.path.append("../..")

from sqlalchemy import Integer
import json
from MelodieTable import Table
from typing import List, Optional, Tuple, Union
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


class SmallIntegerMap:
    def __init__(self) -> None:
        self.data: List[Optional[CacheTreeNode]] = [
            None for i in range(0, 200)]
        self.offset = 0

    # def append(self, val: "CacheTreeNode"):
    #     self.__setitem__(val.value, val)

    def __setitem__(self, k,  item):
        pos = k+self.offset
        # if pos < 0:
        #     self.data = ([None]*(-pos)).extend(self.data)
        #     self.offset -= pos
        # elif pos >= len(self.data):
        #     self.data.extend([None]*(pos-len(self.data)))
        # else:
        self.data[pos] = item

    def __getitem__(self, k):
        return self.data[k+self.offset]

    def get(self, k):
        return self.data[k+self.offset]

class CacheTreeNode:
    def __init__(self, value: Union[int, str]) -> None:
        self.value = value
        self.nodes = {}
        self.data = None

    def format(self):
        if isinstance(self.nodes, dict):
            nodes = [{k: n} for k,n in self.nodes.items() ]
        else:
            nodes = [n.format() for n in self.nodes.data if n is not None]
        return {"value": self.value, "nodes": nodes, "data": str(self.data)}


def find_in_list(l: SmallIntegerMap, item: Union[int, str]) -> Optional[CacheTreeNode]:
    # for a in l:
    #     if a.value == item:
    #         return a
    # return None
    return l.get(item)


class TreeCachedDict:
    def __init__(self, table: Table) -> None:
        self.table: Table = table
        self.cache_tree = {} # id, region, sector

    def search_cache_tree(self, tup):
        """
        手动循环展开之后，发现速度更快。

        """
        id, region, sector= tup
        id_ = find_in_list(self.cache_tree, id)
        if id_ is None:
            return False
        region_ = find_in_list(id_, region)
        if region_ is None:
            return False
        sector_ = find_in_list(region_, sector)
        if sector_ is None:
            return False
        return sector_

    def search_cache_tree_(self, tup: Tuple[int, int, int]):
        node = self.cache_tree
        for item in tup:
            node = find_in_list(node, item)
            if node is None:
                return False
        return node

    def update_cache_tree_2(self, tup: Tuple[int, int, int], data):
        node = self.cache_tree
        for item in tup:
            parent_node = node
            node = find_in_list(node, item)
            if node is None:
                node = {}
                # parent_node.nodes.append(node)
                parent_node[item] = node
        # node.data = data
        parent_node[item]=  data

    def get_items(self, tup):
        v = self.search_cache_tree(tup)
        if v:
            return v
        else:
            data = self.table.find_all(
                lambda obj: obj.id == tup[0] and obj.region == tup[1] and obj.sector == tup[2])
            self.update_cache_tree_2(tup, data)
            return self.search_cache_tree(tup)

    # def format_cache(self):
    #     if node is None:
    #         node = self.cache_tree
    #     for k, v in node.items():
    #         pass


table = Table.from_dicts("", {"id": Integer(), "region": Integer(), "sector": Integer()},
                         [{"id": i % 50, "region": i % 20, "sector": i % 10}
                             for i in range(100)]
                         )

hd = HashCachedDict(table)
td = TreeCachedDict(table)

# ret = td.get_items(30, 10, 1)
# print(ret,"\n", json.dumps(td.format_cache(), indent=2))


def test_hash_cached():
    t0 = time.time()
    for j in range(100000):
        for i in range(100):
            hd.get_items((i % 50, i % 20, i % 10))
    t1 = time.time()
    return t1-t0


def test_tree_cached():
    t0 = time.time()
    for j in range(100000):
        for i in range(100):
            td.get_items((i % 50, i % 20, i % 10))
    t1 = time.time()
    return t1-t0


# print(test_hash_cached())
print("hash_cached", test_hash_cached(), "tree_cached", test_tree_cached())

with open("out.json", "w") as f:
    f.write(str(td.cache_tree))
