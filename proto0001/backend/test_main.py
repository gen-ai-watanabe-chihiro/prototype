# -------------------------------------------------
# ・ファイル名：test_main.py
# ・ファイル内容：バックエンドAPIの単体テスト
# ・作成日時：2025/07/06 17:56:00  Claude Code
# -------------------------------------------------
# -------------------------------------------------
# ・更新日時：2025/07/07 12:00:00  更新者：Claude Code
# ・更新内容：Azure OpenAI チャット機能のテストを追加
# -------------------------------------------------

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from main import app
import jwt
from datetime import datetime, timedelta
import json

client = TestClient(app)

class TestAPI:
    def test_root_endpoint(self):
        """ルートエンドポイントのテスト"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "WebApp API is running"}

    @patch('main.get_db_connection')
    @patch('main.hash_password')
    def test_login_success(self, mock_hash, mock_db):
        """ログイン成功のテスト"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # 実際のパスワードハッシュを生成
        actual_hash = '$2b$12$EhKjNQoGFjKmZgGZgJqwxuJyWQVBQWCgJ9oL7.HJYZKlJFDpqFJgK'
        import bcrypt
        actual_hash = bcrypt.hashpw('testAI00!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # テストユーザーのデータをモック
        mock_cursor.fetchone.return_value = {
            'username': 'testAI',
            'password_hash': actual_hash
        }
        
        response = client.post("/login", json={
            "username": "testAI",
            "password": "testAI00!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @patch('main.get_db_connection')
    def test_login_failure(self, mock_db):
        """ログイン失敗のテスト"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # 存在しないユーザー
        mock_cursor.fetchone.return_value = None
        
        response = client.post("/login", json={
            "username": "wronguser",
            "password": "wrongpass"
        })
        
        assert response.status_code == 401
        assert "ユーザー名またはパスワードが間違っています" in response.json()["detail"]

    @patch('main.get_db_connection')
    def test_dashboard_with_valid_token(self, mock_db):
        """有効なトークンでダッシュボードアクセスのテスト"""
        token = jwt.encode(
            {"sub": "testAI", "exp": datetime.utcnow() + timedelta(minutes=30)},
            "your-secret-key-here",
            algorithm="HS256"
        )
        
        response = client.get("/dashboard", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "こんにちは、testAIさん！" in data["message"]
        assert "dashboard_data" in data

    def test_dashboard_without_token(self):
        """トークンなしでダッシュボードアクセスのテスト"""
        response = client.get("/dashboard")
        assert response.status_code == 403

    def test_dashboard_with_invalid_token(self):
        """無効なトークンでダッシュボードアクセスのテスト"""
        response = client.get("/dashboard", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401

    @patch('main.get_db_connection')
    def test_profile_endpoint(self, mock_db):
        """プロフィールエンドポイントのテスト"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # ユーザーデータをモック
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'username': 'testAI',
            'created_at': datetime.now()
        }
        
        token = jwt.encode(
            {"sub": "testAI", "exp": datetime.utcnow() + timedelta(minutes=30)},
            "your-secret-key-here",
            algorithm="HS256"
        )
        
        response = client.get("/profile", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testAI"
        assert data["id"] == 1

    @patch('main.get_azure_openai_client')
    @patch('main.save_chat_history')
    def test_chat_endpoint(self, mock_save_history, mock_get_client):
        """チャットエンドポイントのテスト"""
        # Azure OpenAI クライアントのモック
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # チャット応答のモック
        from azure_openai_client import ChatResponse
        mock_response = ChatResponse(
            message="テスト応答です",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            timestamp=datetime.now().isoformat()
        )
        mock_client.chat_completion = AsyncMock(return_value=mock_response)
        mock_save_history.return_value = None
        
        # JWTトークンの生成
        token = jwt.encode(
            {"sub": "testAI", "exp": datetime.utcnow() + timedelta(minutes=30)},
            "your-secret-key-here",
            algorithm="HS256"
        )
        
        # チャットリクエスト
        chat_data = {
            "messages": [
                {"role": "user", "content": "こんにちは"}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = client.post("/chat", 
            json=chat_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "テスト応答です"
        assert "usage" in data
        assert "timestamp" in data

    @patch('main.get_db_connection')
    def test_chat_history_endpoint(self, mock_db):
        """チャット履歴取得エンドポイントのテスト"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # 履歴データのモック
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'user_message': 'こんにちは',
                'assistant_message': 'こんにちは！',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        token = jwt.encode(
            {"sub": "testAI", "exp": datetime.utcnow() + timedelta(minutes=30)},
            "your-secret-key-here",
            algorithm="HS256"
        )
        
        response = client.get("/chat/history", 
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert len(data["history"]) == 1

    @patch('main.get_db_connection')
    def test_clear_chat_history_endpoint(self, mock_db):
        """チャット履歴削除エンドポイントのテスト"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        token = jwt.encode(
            {"sub": "testAI", "exp": datetime.utcnow() + timedelta(minutes=30)},
            "your-secret-key-here",
            algorithm="HS256"
        )
        
        response = client.delete("/chat/history", 
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "チャット履歴が削除されました"

    def test_chat_without_token(self):
        """トークンなしでチャットアクセスのテスト"""
        chat_data = {
            "messages": [{"role": "user", "content": "テスト"}]
        }
        response = client.post("/chat", json=chat_data)
        assert response.status_code == 403

    @patch('main.get_azure_openai_client')
    def test_chat_with_azure_error(self, mock_get_client):
        """Azure OpenAI エラー時のテスト"""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat_completion = AsyncMock(side_effect=Exception("Azure OpenAI Error"))
        
        token = jwt.encode(
            {"sub": "testAI", "exp": datetime.utcnow() + timedelta(minutes=30)},
            "your-secret-key-here",
            algorithm="HS256"
        )
        
        chat_data = {
            "messages": [{"role": "user", "content": "テスト"}]
        }
        
        response = client.post("/chat", 
            json=chat_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 500
        assert "チャット処理中にエラーが発生しました" in response.json()["detail"]