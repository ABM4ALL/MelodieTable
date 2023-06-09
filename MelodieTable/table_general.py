from typing import Callable, List, Optional, Tuple, Type, Union, Dict
from sqlalchemy import Column
from sqlalchemy.types import TypeEngine
from sqlalchemy.orm import declarative_base
from .reader_writer import TableReader, TableWriter, DatabaseConnector
from .table_base import TableBase, RowBase

Base = declarative_base()

VEC_TEMPLATE = """
def vectorize_template(obj):
    return [{exprs}]
"""


RowType = Dict[str, TypeEngine]


class GeneralTable(TableBase):
    data: List[dict]

    def __init__(self, row_type: RowType) -> None:
        super().__init__()
        self._db_model_cls: Type = None
        self.row_types: Dict[str, Column] = {}

        for prop_name, prop_value in row_type.items():
            self.row_types[prop_name] = Column(prop_value)

    def clear(self):
        self.data.clear()

    def new_row(self):
        return {}

    @staticmethod
    def parse_header(header_colnames_list: List[str]):
        """
        Parse the header row.
        """
        return header_colnames_list

    @staticmethod
    def from_file(file_name: str, row_types: RowType, encoding='utf-8'):
        table = GeneralTable(row_type=row_types)
        reader = TableReader(file_name,
                             text_encoding=encoding)
        header, rows_iter = reader.read()
        columns = GeneralTable.parse_header(header)

        for row_data in rows_iter:
            table_row_obj = {col: row_data[i] for i, col in enumerate(columns)}
            table.data.append(table_row_obj)
        return table

    def to_file(self, file_name: str, encoding="utf-8"):
        writer = TableWriter(file_name,
                             text_encoding=encoding).write()
        headers = [col_name for col_name in self.row_types.keys()]
        writer.send(headers)
        for row_data in self.data:
            writer.send([row_data[k] for k in headers])
        writer.close()

    def to_database(self, engine, table_name: str):
        conn = DatabaseConnector(engine)
        conn.write_table(table_name, self.row_types, self.data)

    # def from_pandas(self, df: "pd.DataFrame"):
    #     """
    #     Create a general table from pandas dataframe.
    #     """
    #     pass

    @staticmethod
    def from_dicts(row_type: RowType, dicts: List[dict], copy=True):
        table = GeneralTable(row_type)
        if not copy:
            for dic in dicts:
                table.data.append(dic)
        else:
            for dic in dicts:
                table.data.append({k: v for k, v in dic.items()})
        return table

    def find_one(self, query: Callable[[dict], bool]) -> Optional[dict]:
        _, obj = self.find_one_with_index(query)
        return obj

    def find_one_with_index(self, query: Callable[[dict], bool]) -> Tuple[int, Optional[dict]]:
        for i, obj in enumerate(self.data):
            if query(obj):
                return i, obj
        return -1, None

    @property
    def iat(self):
        return TableBase.IatDictsIndicer(self.data)
