from typing import Callable, List, Tuple, Type, Union, Dict
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


class TableRow(RowBase):
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def vectorizer(attrs: List[str]) -> Callable[[List[str]], str]:
        exprs = ",".join(['obj.'+attr for attr in attrs])
        code = VEC_TEMPLATE.format(exprs=exprs)
        vars = {}
        exec(code, None, vars)
        return vars["vectorize_template"]


RowType = Union[Type, Dict[str, TypeEngine]]


class Table(TableBase):
    def __init__(self, name: str, row_type: RowType) -> None:
        super().__init__()
        self.name = name
        self.row_cls: Type = None
        self._db_model_cls: Type = None
        self.row_types: Dict[str, Column] = {}

        if callable(row_type):
            self.row_cls = row_type
        elif isinstance(row_type, dict):
            self.row_cls = TableRow
            for prop_name, prop_value in row_type.items():
                self.row_types[prop_name] = Column(prop_value)
        else:
            raise NotImplementedError(
                f"Cannot recognize table row type {type(row_type)}")

    def clear(self):
        self.data = []

    def new_row(self):
        # if len(self._deleted_rows_cache) == 0:
        return self.row_cls()
        # else:
        #     return self._deleted_rows_cache.pop()

    @staticmethod
    def parse_header(header_colnames_list: List[str]):
        """
        Parse the header row.
        """
        cols: List[str] = []
        for col_index, col_name in enumerate(header_colnames_list):
            cols.append(col_name)
            assert col_name.isidentifier, f"Column name '{col_name}' should be an identifier!"
        return cols

    @staticmethod
    def from_file(file_name: str, row_types: RowType, encoding='utf-8'):
        table = Table('', row_type=row_types)
        reader = TableReader(file_name,
                             text_encoding=encoding)
        header, rows_iter = reader.read()
        columns = Table.parse_header(header)

        for row_data in rows_iter:
            table_row_obj = table.row_cls(
                **{col: row_data[i] for i, col in enumerate(columns)})
            table.data.append(table_row_obj)
        return table

    def to_file(self, file_name: str, encoding="utf-8"):
        writer = TableWriter(file_name,
                             text_encoding=encoding).write()
        headers = [row for row in self.row_types.keys()]
        writer.send(headers)
        for row_data in self.data:
            writer.send([row_data.__dict__[k] for k in headers])
        writer.close()

    def to_database(self, engine, table_name: str):
        conn = DatabaseConnector(engine)
        conn.write_table(table_name, self.row_types, [
                         d.__dict__ for d in self.data])

    def to_file_with_codegen(self, file_name: str, encoding="utf-8"):
        writer = TableWriter(file_name,
                             text_encoding=encoding).write()
        headers = [row for row in self.row_types.keys()]
        writer.send(headers)
        vectorizer = TableRow.vectorizer(headers)
        for row_data in self.data:
            writer.send(vectorizer(row_data))
        writer.close()

    @staticmethod
    def from_dicts(name: str, row_type: RowType, dicts: List[dict]):
        table = Table(name, row_type)
        for dic in dicts:
            table.data.append(table.row_cls(**dic))
        return table

    def find_one(self, query: Callable[[object], bool]) -> object:
        _, obj = self.find_one_with_index(query)
        return obj

    def find_one_with_index(self, query: Callable[[object], bool]) -> Tuple[int, object]:
        for i, obj in enumerate(self.data):
            if query(obj):
                return i, obj
        return -1, None
    # def get_db_class(self):
    #     if self._db_model_cls is not None:
    #         self._db_model_cls = type("TableModel_"+self.name, (Base,), {
    #             '__tablename__': "{}".format(self.name),
    #             "id": Column(Integer, primary_key=True, autoincrement=True),
    #             "a": Column(Integer),
    #             "b": Column(Integer)
    #         })
    #     return self._db_model_cls
