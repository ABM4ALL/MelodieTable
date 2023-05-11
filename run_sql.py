from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

# 设置数据库连接信息
config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'melodie'
}

# 创建数据库引擎
engine_str = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
engine = create_engine(engine_str)

# 创建 MetaData 对象
metadata = MetaData()

# 定义表结构
class_table = Table('temp_mysql_table', metadata,
                    Column('a', Integer),
                    Column('index', Integer),
                    )

# 创建表
# class_table.create(bind=engine)

# 从表 temp_mysql_table 中获取全部数据
result = class_table.select()
print(result)

ret = engine.execute(result)
print(ret)
for row in ret:
    print(row)
