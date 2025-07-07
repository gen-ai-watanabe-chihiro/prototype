# -------------------------------------------------
# ・ファイル名：azure_openai_client.py
# ・ファイル内容：Azure OpenAI APIクライアント
# ・作成日時：2025/07/07 11:57:00  Claude Code
# -------------------------------------------------

import os
import asyncio
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from pydantic import BaseModel
import json
from datetime import datetime

# 環境変数から設定を読み込み
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
AZURE_OPENAI_MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-35-turbo")

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    usage: Optional[Dict[str, Any]] = None
    timestamp: str

class AzureOpenAIClient:
    def __init__(self):
        """Azure OpenAI クライアントの初期化"""
        if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
            raise ValueError("Azure OpenAI の設定が不完全です。環境変数を確認してください。")
        
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION
        )
        self.model_name = AZURE_OPENAI_MODEL_NAME

    async def chat_completion(self, chat_request: ChatRequest) -> ChatResponse:
        """チャット完了APIの実行"""
        try:
            # システムプロンプトの設定
            messages = []
            if chat_request.system_prompt:
                messages.append({"role": "system", "content": chat_request.system_prompt})
            
            # ユーザーメッセージの追加
            for msg in chat_request.messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Azure OpenAI APIの呼び出し
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=chat_request.max_tokens,
                temperature=chat_request.temperature,
                stream=False
            )

            # レスポンスの処理
            assistant_message = response.choices[0].message.content
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else None

            return ChatResponse(
                message=assistant_message,
                usage=usage_info,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            raise Exception(f"Azure OpenAI APIの呼び出しでエラーが発生しました: {str(e)}")

    async def chat_completion_stream(self, chat_request: ChatRequest):
        """ストリーミングチャット完了APIの実行"""
        try:
            # システムプロンプトの設定
            messages = []
            if chat_request.system_prompt:
                messages.append({"role": "system", "content": chat_request.system_prompt})
            
            # ユーザーメッセージの追加
            for msg in chat_request.messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Azure OpenAI APIのストリーミング呼び出し
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=chat_request.max_tokens,
                temperature=chat_request.temperature,
                stream=True
            )

            # ストリーミングレスポンスの処理
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"Azure OpenAI APIのストリーミング呼び出しでエラーが発生しました: {str(e)}")

    def validate_connection(self) -> bool:
        """接続の検証"""
        try:
            # 簡単なテストメッセージを送信
            test_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return test_response.choices[0].message.content is not None
        except Exception as e:
            print(f"Azure OpenAI接続検証エラー: {str(e)}")
            return False

# グローバルインスタンス
azure_openai_client = None

def get_azure_openai_client() -> AzureOpenAIClient:
    """Azure OpenAI クライアントのシングルトンインスタンスを取得"""
    global azure_openai_client
    if azure_openai_client is None:
        azure_openai_client = AzureOpenAIClient()
    return azure_openai_client