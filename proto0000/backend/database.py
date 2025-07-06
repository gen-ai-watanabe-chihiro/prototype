# -------------------------------------------------
# ・ファイル名：database.py
# ・ファイル内容：PostgreSQL データベース接続設定
# ・作成日時：2025/07/06 17:56:00  Claude Code
# -------------------------------------------------

import psycopg2
import os
from typing import Optional

# データベース接続設定
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "webapp_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "port": os.getenv("DB_PORT", "5432"),
}

def get_db_connection():
    """PostgreSQL データベースへの接続を取得"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"データベース接続エラー: {e}")
        raise

def test_connection() -> bool:
    """データベース接続をテスト"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"データベース接続テストエラー: {e}")
        return False