# -------------------------------------------------
# ・ファイル名：test_chat_api.py
# ・ファイル内容：チャットAPI直接テスト
# ・作成日時：2025/07/07 Claude Code
# -------------------------------------------------

import requests
import json

def test_login_and_chat():
    """ログインしてチャットAPIをテスト"""
    base_url = "http://localhost:8000"
    
    print("🔐 ログインテスト...")
    
    # ログインリクエスト
    login_data = {
        "username": "testAI",
        "password": "testAI00!"
    }
    
    try:
        response = requests.post(f"{base_url}/login", json=login_data)
        print(f"ログイン応答ステータス: {response.status_code}")
        print(f"ログイン応答内容: {response.text}")
        
        if response.status_code != 200:
            print("❌ ログインに失敗しました")
            return
        
        token_data = response.json()
        access_token = token_data["access_token"]
        print("✅ ログイン成功")
        
        # チャットリクエスト
        print("\n💬 チャットAPIテスト...")
        
        chat_data = {
            "messages": [
                {"role": "user", "content": "こんにちは！テストメッセージです。"}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{base_url}/chat", json=chat_data, headers=headers)
        print(f"チャット応答ステータス: {response.status_code}")
        print(f"チャット応答内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ チャットAPI成功")
            chat_response = response.json()
            print(f"AI応答: {chat_response.get('message', 'なし')}")
        else:
            print("❌ チャットAPIに失敗しました")
            
    except Exception as e:
        print(f"❌ テスト中にエラーが発生: {e}")

if __name__ == "__main__":
    test_login_and_chat()