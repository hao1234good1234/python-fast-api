## ✅ 第三步：创建数据库连接（`database/connection.py`）

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from settings import settings

load_dotenv() # 读取 .env 文件
# 1. 配置数据库 URL（开发用 SQLite，生产可换 PostgreSQL/MySQL）
# 数据库文件路径
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/library.db") # 从环境变量中获取数据库 URL
DATABASE_URL = settings.DATABASE_URL # 从 settings.py 中获取

# 2. 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },  # 🔒 `check_same_thread=False` 是 SQLite 在 Web 环境下的常见设置（允许跨线程使用）
)
# 3. 创建会话工厂（SessionLocal 是一个“类”，不是实例！）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
