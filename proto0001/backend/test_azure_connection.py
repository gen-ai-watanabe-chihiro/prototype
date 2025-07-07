# -------------------------------------------------
# ・ファイル名：test_azure_connection.py
# ・ファイル内容：Azure OpenAI接続テスト
# ・作成日時：2025/07/07 Claude Code
# -------------------------------------------------

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def test_azure_openai_connection():
    """Azure OpenAI接続テスト"""
    load_dotenv()
    
    # 環境変数の確認
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    print("🔍 Azure OpenAI設定を確認中...")
    print(f"エンドポイント: {endpoint}")
    print(f"APIバージョン: {api_version}")
    print(f"デプロイメント名: {deployment_name}")
    print(f"APIキー: {'設定済み' if api_key else '未設定'}")
    
    if not all([api_key, endpoint, api_version, deployment_name]):
        print("❌ 必要な環境変数が設定されていません")
        return False
    
    try:
        # Azure OpenAI クライアントの初期化
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        print("🤖 Azure OpenAI接続テスト中...")
        
        # テストリクエスト
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "あなたは親切なAIアシスタントです。"},
                {"role": "user", "content": "こんにちは！接続テストです。"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        print("✅ Azure OpenAI接続成功!")
        print(f"応答: {response.choices[0].message.content}")
        print(f"使用トークン: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI接続エラー: {e}")
        return False

def test_streaming_connection():
    """ストリーミング接続テスト"""
    load_dotenv()
    
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        print("🔄 ストリーミング接続テスト中...")
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "user", "content": "1から3まで数えてください。"}
            ],
            stream=True,
            max_tokens=50
        )
        
        print("📡 ストリーミング応答:")
        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="")
        
        print("\n✅ ストリーミング接続成功!")
        return True
        
    except Exception as e:
        print(f"❌ ストリーミング接続エラー: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Azure OpenAI接続テストを開始します...")
    print("=" * 50)
    
    # 基本接続テスト
    if test_azure_openai_connection():
        print("\n" + "=" * 50)
        # ストリーミング接続テスト
        test_streaming_connection()
    
    print("\n" + "=" * 50)
    print("🏁 テスト完了")