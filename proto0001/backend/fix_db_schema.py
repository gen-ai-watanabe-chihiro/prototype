# -------------------------------------------------
# ・ファイル名：fix_db_schema.py
# ・ファイル内容：データベーススキーマ修正スクリプト
# ・作成日時：2025/07/07 Claude Code
# -------------------------------------------------

import psycopg2
from database import DATABASE_CONFIG

def fix_chat_history_schema():
    """chat_historyテーブルにusernameカラムを追加"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        # usernameカラムが存在するかチェック
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chat_history' AND column_name = 'username'
        """)
        
        if not cursor.fetchone():
            print("📝 chat_historyテーブルにusernameカラムを追加中...")
            # usernameカラムを追加
            cursor.execute("""
                ALTER TABLE chat_history 
                ADD COLUMN username VARCHAR(50)
            """)
            
            # 既存のデータにusernameを設定（user_idから取得）
            cursor.execute("""
                UPDATE chat_history 
                SET username = users.username 
                FROM users 
                WHERE chat_history.user_id = users.id
            """)
            
            print("✅ usernameカラムを追加しました")
        else:
            print("✅ usernameカラムは既に存在します")
        
        # インデックスを追加してパフォーマンスを向上
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_history_username 
            ON chat_history(username)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_history_created_at 
            ON chat_history(created_at DESC)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ データベーススキーマの修正が完了しました")
        return True
        
    except Exception as e:
        print(f"❌ スキーマ修正エラー: {e}")
        return False

def reset_database():
    """データベースを完全にリセット"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        
        print("🗑️ 既存のテーブルを削除中...")
        cursor.execute("DROP TABLE IF EXISTS chat_history CASCADE")
        cursor.execute("DROP TABLE IF EXISTS users CASCADE")
        
        print("📊 テーブルを再作成中...")
        
        # usersテーブルの作成
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # chat_historyテーブルの作成（usernameカラム付き）
        cursor.execute("""
            CREATE TABLE chat_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                username VARCHAR(50) NOT NULL,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # インデックスの作成
        cursor.execute("""
            CREATE INDEX idx_chat_history_username ON chat_history(username)
        """)
        cursor.execute("""
            CREATE INDEX idx_chat_history_created_at ON chat_history(created_at DESC)
        """)
        
        # テストユーザーの作成
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("testAI00!")
        
        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
        """, ("testAI", hashed_password))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ データベースのリセットが完了しました")
        return True
        
    except Exception as e:
        print(f"❌ データベースリセットエラー: {e}")
        return False

if __name__ == "__main__":
    print("データベーススキーマの修正を開始します...")
    print("1. スキーマ修正（既存データ保持）")
    print("2. 完全リセット（データ削除）")
    
    choice = input("選択してください (1 or 2): ")
    
    if choice == "1":
        fix_chat_history_schema()
    elif choice == "2":
        reset_database()
    else:
        print("無効な選択です")