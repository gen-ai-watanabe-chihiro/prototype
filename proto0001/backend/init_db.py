# -------------------------------------------------
# ・ファイル名：init_db.py
# ・ファイル内容：データベース初期化スクリプト
# ・作成日時：2025/07/07 Claude Code
# -------------------------------------------------

import psycopg2
import os
from database import DATABASE_CONFIG

def initialize_database():
    """データベースとテーブルの初期化"""
    try:
        # データベースに接続
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        # usersテーブルの作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # chat_historyテーブルの作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # テストユーザーの作成（パスワード: testAI00!）
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("testAI00!")
        
        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            ON CONFLICT (username) DO NOTHING
        """, ("testAI", hashed_password))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ データベースの初期化が完了しました")
        return True
        
    except Exception as e:
        print(f"❌ データベース初期化エラー: {e}")
        return False

if __name__ == "__main__":
    initialize_database()