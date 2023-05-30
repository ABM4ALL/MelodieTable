import json
from sqlalchemy import Integer
import sys
sys.path.append("../..")
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


class CacheTreeNode:
    def __init__(self, value: Union[int, str]) -> None:
        self.value = value
        self.nodes: List[CacheTreeNode] = []
        self.data = None

    def format(self):
        return {"value": self.value, "nodes": [n.format() for n in self.nodes], "data": str(self.data)}

def find_in_list(l: List[CacheTreeNode], item: Union[int, str]) -> Optional[CacheTreeNode]:
    for a in l:
        if a.value == item:
            return a
    return None


class TreeCachedDict:
    def __init__(self, table: Table) -> None:
        self.table: Table = table
        self.cache_tree = CacheTreeNode(-1)  # id, region, sector

    def search_cache_tree(self, id, region, sector):
        id_ = find_in_list(self.cache_tree.nodes, id)
        if id_ is None:
            return False
        region_ = find_in_list(id_.nodes, region)
        if region_ is None:
            return False
        sector_ = find_in_list(region_.nodes, sector)
        if sector_ is None:
            return False
        return sector_.data

    def update_cache_tree(self, id, region, sector, data):
        id_node = find_in_list(self.cache_tree.nodes, id)
        if id_node is None:
            id_node = CacheTreeNode(id)
            region_node = CacheTreeNode(region)
            sector_node = CacheTreeNode(sector)
            self.cache_tree.nodes.append(id_node)
            id_node.nodes.append(region_node)
            region_node.nodes.append(sector_node)
            sector_node.data = data
            return
        region_node = find_in_list(id_node.nodes, region)
        if region_node is None:
            region_node = CacheTreeNode(region)
            sector_node = CacheTreeNode(sector)
            id_node.nodes.append(region_node)
            region_node.nodes.append(sector_node)
            sector_node.data = data
            return
        sector_node = find_in_list(region_node.nodes, sector)
        if sector_node is None:
            sector_node = CacheTreeNode(sector)
            region_node.nodes.append(sector_node)
            sector_node.data = data
            return

    def get_items(self, id:int, region:int, sector:int):
        v = self.search_cache_tree(id, region, sector)
        if v:
            return v
        else:
            data = self.table.find_all(lambda obj: obj.id == id and obj.region == region and obj.sector == sector)
            self.update_cache_tree(id, region, sector, data)
            return self.search_cache_tree(id, region, sector)            

    def format_cache(self, ):
        return self.cache_tree.format()["nodes"]

table = Table.from_dicts("", {"id": Integer(), "region": Integer(), "sector": Integer()},
                         [{"id": i%50, "region": i%20, "sector": i%10}
                             for i in range(100)]
                         )

hd = HashCachedDict(table)
td = TreeCachedDict(table)

ret = td.get_items(30, 10, 1)
# print(ret,"\n", json.dumps(td.format_cache(), indent=2))
def test_hash_cached():
    t0 = time.time()
    for j in range(100000):
        for i in range(100):
            hd.get_items((i%50, i%20, i%10))
    t1 = time.time()
    return t1-t0

def test_tree_cached():
    t0 = time.time()
    for j in range(100000):
        for i in range(100):
            td.get_items(i%50, i%20, i%10)
    t1 = time.time()
    return t1-t0

# print(test_hash_cached())
print("hash_cached", test_hash_cached(), "tree_cached", test_tree_cached())

with open("out.json", "w") as f:
    json.dump(td.format_cache(), f, indent=4)