# -------------------------------------------------
# ・ファイル名：debug_chat.py
# ・ファイル内容：チャット機能デバッグスクリプト
# ・作成日時：2025/07/07 Claude Code
# -------------------------------------------------

import asyncio
import traceback
from azure_openai_client import AzureOpenAIClient, ChatRequest, ChatMessage
from main import save_chat_history
import os
from dotenv import load_dotenv

async def debug_chat_flow():
    """チャット処理の各ステップをデバッグ"""
    load_dotenv()
    
    print("🔍 チャット機能デバッグを開始します...")
    
    # 1. 環境変数の確認
    print("\n1. 環境変数の確認:")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    print(f"   API Key: {'設定済み' if api_key else '未設定'}")
    print(f"   Endpoint: {endpoint}")
    print(f"   Deployment: {deployment}")
    
    # 2. Azure OpenAI クライアントの初期化
    print("\n2. Azure OpenAI クライアントの初期化:")
    try:
        client = AzureOpenAIClient()
        print("   ✅ クライアント初期化成功")
    except Exception as e:
        print(f"   ❌ クライアント初期化失敗: {e}")
        traceback.print_exc()
        return
    
    # 3. チャットリクエストの作成
    print("\n3. チャットリクエストの作成:")
    try:
        chat_request = ChatRequest(
            messages=[
                ChatMessage(role="user", content="こんにちは！テストです。")
            ],
            max_tokens=100,
            temperature=0.7
        )
        print("   ✅ チャットリクエスト作成成功")
    except Exception as e:
        print(f"   ❌ チャットリクエスト作成失敗: {e}")
        traceback.print_exc()
        return
    
    # 4. Azure OpenAI API呼び出し
    print("\n4. Azure OpenAI API呼び出し:")
    try:
        response = await client.chat_completion(chat_request)
        print("   ✅ API呼び出し成功")
        print(f"   応答: {response.message}")
        print(f"   トークン使用量: {response.usage}")
    except Exception as e:
        print(f"   ❌ API呼び出し失敗: {e}")
        traceback.print_exc()
        return
    
    # 5. チャット履歴保存
    print("\n5. チャット履歴保存:")
    try:
        await save_chat_history("testAI", chat_request.messages, response.message)
        print("   ✅ チャット履歴保存成功")
    except Exception as e:
        print(f"   ❌ チャット履歴保存失敗: {e}")
        traceback.print_exc()
        return
    
    print("\n🎉 すべてのステップが成功しました！")

async def test_actual_api_call():
    """実際のAPI呼び出しをテスト"""
    load_dotenv()
    
    print("🧪 実際のAPI呼び出しテストを開始...")
    
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        print("✅ Azure OpenAI クライアント作成成功")
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "あなたは親切なAIアシスタントです。"},
                {"role": "user", "content": "こんにちは！"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        print("✅ API呼び出し成功")
        print(f"応答: {response.choices[0].message.content}")
        print(f"使用トークン: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"❌ API呼び出しエラー: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("チャットデバッグスクリプト")
    print("=" * 50)
    
    # 実際のAPI呼び出しテスト
    asyncio.run(test_actual_api_call())
    
    print("\n" + "=" * 50)
    
    # 完全なチャットフローテスト
    asyncio.run(debug_chat_flow())