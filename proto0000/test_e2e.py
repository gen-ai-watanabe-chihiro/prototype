# -------------------------------------------------
# ・ファイル名：test_e2e.py
# ・ファイル内容：エンドツーエンド（運用）テスト
# ・作成日時：2025/07/06 17:56:00  Claude Code
# -------------------------------------------------

import requests
import time
import json

class EndToEndTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_credentials = {"username": "testAI", "password": "testAI00!"}
        self.access_token = None
        
    def simulate_user_login(self):
        """ユーザーログインのシミュレーション"""
        print("👤 ユーザーログインをシミュレーション中...")
        try:
            response = requests.post(f"{self.backend_url}/login", json=self.test_credentials)
            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                print("✅ ログイン成功: トークンを取得しました")
                return True
            else:
                print(f"❌ ログイン失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ ログインエラー: {e}")
            return False
    
    def simulate_dashboard_access(self):
        """ダッシュボードアクセスのシミュレーション"""
        print("📊 ダッシュボードアクセスをシミュレーション中...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.backend_url}/dashboard", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ ダッシュボードアクセス成功: {data['message']}")
                return True
            else:
                print(f"❌ ダッシュボードアクセス失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ ダッシュボードアクセスエラー: {e}")
            return False
    
    def simulate_profile_access(self):
        """プロフィールアクセスのシミュレーション"""
        print("👨‍💼 プロフィールアクセスをシミュレーション中...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.backend_url}/profile", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ プロフィールアクセス成功: ユーザー {data['username']}")
                return True
            else:
                print(f"❌ プロフィールアクセス失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ プロフィールアクセスエラー: {e}")
            return False
    
    def simulate_unauthorized_access(self):
        """認証なしアクセスのシミュレーション"""
        print("🚫 認証なしアクセスをシミュレーション中...")
        try:
            response = requests.get(f"{self.backend_url}/dashboard")
            if response.status_code == 403:
                print("✅ 認証なしアクセス: 正しく拒否されました")
                return True
            else:
                print(f"❌ 認証なしアクセス: 予期しない応答 {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 認証なしアクセステストエラー: {e}")
            return False
    
    def test_invalid_credentials(self):
        """無効な認証情報でのテスト"""
        print("🔐 無効な認証情報でのテスト中...")
        try:
            invalid_credentials = {"username": "testAI", "password": "wrongpassword"}
            response = requests.post(f"{self.backend_url}/login", json=invalid_credentials)
            if response.status_code == 401:
                print("✅ 無効な認証情報: 正しく拒否されました")
                return True
            else:
                print(f"❌ 無効な認証情報: 予期しない応答 {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 無効な認証情報テストエラー: {e}")
            return False
    
    def test_frontend_availability(self):
        """フロントエンドの可用性テスト"""
        print("🌐 フロントエンドの可用性をテスト中...")
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200 and "WebApp" in response.text:
                print("✅ フロントエンド: 正常に応答しています")
                return True
            else:
                print(f"❌ フロントエンド: 応答に問題があります {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ フロントエンドテストエラー: {e}")
            return False
    
    def run_full_e2e_test(self):
        """完全なエンドツーエンドテストを実行"""
        print("🚀 エンドツーエンドテストを開始します...")
        print("=" * 50)
        
        test_scenarios = [
            ("フロントエンド可用性", self.test_frontend_availability),
            ("認証なしアクセステスト", self.simulate_unauthorized_access),
            ("無効な認証情報テスト", self.test_invalid_credentials),
            ("ユーザーログイン", self.simulate_user_login),
            ("ダッシュボードアクセス", self.simulate_dashboard_access),
            ("プロフィールアクセス", self.simulate_profile_access),
        ]
        
        passed = 0
        total = len(test_scenarios)
        
        for scenario_name, test_func in test_scenarios:
            print(f"\n🧪 テストシナリオ: {scenario_name}")
            if test_func():
                passed += 1
            else:
                print(f"⚠️ {scenario_name} が失敗しました")
            time.sleep(1)  # テスト間の間隔
        
        print("\n" + "=" * 50)
        print(f"📊 エンドツーエンドテスト結果: {passed}/{total} シナリオが成功")
        
        if passed == total:
            print("🎉 すべてのエンドツーエンドテストが成功しました！")
            print("✅ アプリケーションは本番環境での使用準備が整っています。")
            return True
        else:
            print("⚠️ いくつかのエンドツーエンドテストが失敗しました。")
            print("🔧 本番環境デプロイ前に修正が必要です。")
            return False

if __name__ == "__main__":
    test_runner = EndToEndTest()
    success = test_runner.run_full_e2e_test()
    exit(0 if success else 1)