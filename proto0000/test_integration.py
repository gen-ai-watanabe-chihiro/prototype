# -------------------------------------------------
# ・ファイル名：test_integration.py
# ・ファイル内容：総合テスト（システム統合テスト）
# ・作成日時：2025/07/06 17:56:00  Claude Code
# -------------------------------------------------

import requests
import time
import subprocess
import signal
import os
import psutil

class SystemTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_user = {"username": "testAI", "password": "testAI00!"}
        
    def test_backend_health(self):
        """バックエンドのヘルスチェック"""
        try:
            response = requests.get(f"{self.backend_url}/")
            assert response.status_code == 200
            assert response.json()["message"] == "WebApp API is running"
            print("✅ バックエンドのヘルスチェック: 成功")
            return True
        except Exception as e:
            print(f"❌ バックエンドのヘルスチェック: 失敗 - {e}")
            return False
    
    def test_frontend_health(self):
        """フロントエンドのヘルスチェック"""
        try:
            response = requests.get(self.frontend_url)
            assert response.status_code == 200
            assert "WebApp" in response.text
            print("✅ フロントエンドのヘルスチェック: 成功")
            return True
        except Exception as e:
            print(f"❌ フロントエンドのヘルスチェック: 失敗 - {e}")
            return False
    
    def test_user_authentication_flow(self):
        """ユーザー認証フローの統合テスト"""
        try:
            # ログインテスト
            response = requests.post(f"{self.backend_url}/login", json=self.test_user)
            assert response.status_code == 200
            token_data = response.json()
            assert "access_token" in token_data
            assert token_data["token_type"] == "bearer"
            
            # トークンを使用してダッシュボードにアクセス
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            response = requests.get(f"{self.backend_url}/dashboard", headers=headers)
            assert response.status_code == 200
            dashboard_data = response.json()
            assert "こんにちは、testAIさん！" in dashboard_data["message"]
            
            # プロフィール情報の取得
            response = requests.get(f"{self.backend_url}/profile", headers=headers)
            assert response.status_code == 200
            profile_data = response.json()
            assert profile_data["username"] == "testAI"
            
            print("✅ ユーザー認証フローの統合テスト: 成功")
            return True
        except Exception as e:
            print(f"❌ ユーザー認証フローの統合テスト: 失敗 - {e}")
            return False
    
    def test_invalid_authentication(self):
        """無効な認証のテスト"""
        try:
            # 間違ったパスワードでログイン試行
            invalid_user = {"username": "testAI", "password": "wrongpassword"}
            response = requests.post(f"{self.backend_url}/login", json=invalid_user)
            assert response.status_code == 401
            
            # 無効なトークンでダッシュボードにアクセス
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(f"{self.backend_url}/dashboard", headers=headers)
            assert response.status_code == 401
            
            print("✅ 無効な認証のテスト: 成功")
            return True
        except Exception as e:
            print(f"❌ 無効な認証のテスト: 失敗 - {e}")
            return False
    
    def run_all_tests(self):
        """全ての総合テストを実行"""
        print("🔍 総合テストを開始します...")
        tests = [
            self.test_backend_health,
            self.test_frontend_health,
            self.test_user_authentication_flow,
            self.test_invalid_authentication
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # テスト間の間隔
        
        print(f"\n📊 総合テスト結果: {passed}/{total} テストが成功")
        
        if passed == total:
            print("🎉 すべての総合テストが成功しました！")
            return True
        else:
            print("⚠️ いくつかの総合テストが失敗しました。")
            return False

if __name__ == "__main__":
    test_runner = SystemTest()
    success = test_runner.run_all_tests()
    exit(0 if success else 1)