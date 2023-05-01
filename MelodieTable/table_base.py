from typing import Callable, List, Tuple


class RowBase:
    def payload_to_str(self):
        return f"{self.__dict__}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.payload_to_str()}>"


class TableBase:
    def __init__(self) -> None:
        self.data: List[object] = []

    def __len__(self):
        return len(self.data)

    def create_empty(self):
        raise NotImplementedError("Abstract method")

    def create_same_schemed_empty(self):
        new_table: TableBase = self.create_empty()
        for k, v in new_table.__dict__.items():
            if k != "data":
                setattr(new_table, k,  v)
        new_table.data = []
        return new_table

    def find_one_with_index(self, query: Callable[[object], bool]) -> Tuple[int, object]:
        for i, obj in enumerate(self.data):
            if query(obj):
                return i, obj
        return -1, None

    def find_all_with_index(self, query: Callable[[object], bool]) -> List[Tuple[int, object]]:
        result = []
        for i, obj in enumerate(self.data):
            if query(obj):
                result.append((i, obj))
        return result

    def find_all(self, query: Callable[[object], bool]) -> List[object]:
        result = []
        for obj in self.data:
            if query(obj):
                result.append(obj)
        return result

    def filter(self, query: Callable[[object], bool]):
        new_data = self.find_all(query)
        new_table = self.create_same_schemed_empty()
        new_table.data = new_data
        return new_table
