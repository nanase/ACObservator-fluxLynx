from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# データベースURL (SQLite)
DATABASE_URL = "sqlite:///app/db/database.db"

# エンジンの作成
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLiteの場合に必要

# セッションファクトリの作成
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine  # 自動コミットを無効化  # 自動フラッシュを無効化
)

# モデル用のBase
Base = declarative_base()


# データベース接続を取得するユーティリティ関数
def get_db() -> Generator[Session]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
