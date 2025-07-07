# -------------------------------------------------
# ・ファイル名：main.py
# ・ファイル内容：FastAPI バックエンドのメインファイル
# ・作成日時：2025/07/06 17:56:00  Claude Code
# -------------------------------------------------
# -------------------------------------------------
# ・更新日時：2025/07/07 11:57:00  更新者：Claude Code
# ・更新内容：Azure OpenAI チャット機能の追加
# -------------------------------------------------

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import jwt
import bcrypt
from datetime import datetime, timedelta
import os
from database import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor
from azure_openai_client import get_azure_openai_client, ChatRequest, ChatMessage, ChatResponse
import json

app = FastAPI(title="WebApp API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# セキュリティ設定
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# データモデル
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

# パスワードハッシュ化
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# JWT生成
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# JWT検証
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なトークンです",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )

# データベース初期化
def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ユーザーテーブル作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # チャット履歴テーブル作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            user_message TEXT NOT NULL,
            assistant_message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)
    
    # テストユーザー作成
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'testAI'")
    if cursor.fetchone()[0] == 0:
        hashed_password = hash_password("testAI00!")
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            ("testAI", hashed_password)
        )
    
    conn.commit()
    cursor.close()
    conn.close()

# API エンドポイント
@app.get("/")
async def root():
    return {"message": "WebApp API is running"}

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
    db_user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not db_user or not verify_password(user.password, db_user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが間違っています",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user['username']}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/dashboard")
async def dashboard(current_user: str = Depends(verify_token)):
    return {
        "message": f"こんにちは、{current_user}さん！",
        "dashboard_data": {
            "total_users": 1,
            "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

@app.get("/profile")
async def profile(current_user: str = Depends(verify_token)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT id, username, created_at FROM users WHERE username = %s", (current_user,))
    user_data = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )
    
    return user_data

# チャット関連のAPIエンドポイント
@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, current_user: str = Depends(verify_token)):
    """Azure OpenAI を使用したチャット機能"""
    try:
        # Azure OpenAI クライアントの取得
        client = get_azure_openai_client()
        
        # システムプロンプトの設定
        system_prompt = """あなたは親切で知識豊富なAIアシスタントです。
ユーザーの質問に対して、正確で有用な回答を提供してください。
回答は日本語で行ってください。"""
        
        # チャットリクエストにシステムプロンプトを設定
        if not chat_request.system_prompt:
            chat_request.system_prompt = system_prompt
        
        # Azure OpenAI APIの呼び出し
        response = await client.chat_completion(chat_request)
        
        # チャット履歴をデータベースに保存
        await save_chat_history(current_user, chat_request.messages, response.message)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"チャット処理中にエラーが発生しました: {str(e)}"
        )

@app.post("/chat/stream")
async def chat_stream(chat_request: ChatRequest, current_user: str = Depends(verify_token)):
    """ストリーミングチャット機能"""
    try:
        # Azure OpenAI クライアントの取得
        client = get_azure_openai_client()
        
        # システムプロンプトの設定
        system_prompt = """あなたは親切で知識豊富なAIアシスタントです。
ユーザーの質問に対して、正確で有用な回答を提供してください。
回答は日本語で行ってください。"""
        
        # チャットリクエストにシステムプロンプトを設定
        if not chat_request.system_prompt:
            chat_request.system_prompt = system_prompt
        
        # ストリーミングレスポンスの生成
        async def stream_generator():
            full_response = ""
            async for chunk in client.chat_completion_stream(chat_request):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # 完了通知
            yield f"data: {json.dumps({'done': True})}\n\n"
            
            # チャット履歴をデータベースに保存
            await save_chat_history(current_user, chat_request.messages, full_response)
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ストリーミングチャット処理中にエラーが発生しました: {str(e)}"
        )

@app.get("/chat/history")
async def get_chat_history(current_user: str = Depends(verify_token)):
    """チャット履歴の取得"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, user_message, assistant_message, created_at
            FROM chat_history
            WHERE username = %s
            ORDER BY created_at DESC
            LIMIT 50
        """, (current_user,))
        
        history = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"チャット履歴の取得中にエラーが発生しました: {str(e)}"
        )

@app.delete("/chat/history")
async def clear_chat_history(current_user: str = Depends(verify_token)):
    """チャット履歴の削除"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE username = %s", (current_user,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"message": "チャット履歴が削除されました"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"チャット履歴の削除中にエラーが発生しました: {str(e)}"
        )

# チャット履歴保存用の関数
async def save_chat_history(username: str, messages: List[ChatMessage], assistant_response: str):
    """チャット履歴をデータベースに保存"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 最後のユーザーメッセージを取得
        user_message = ""
        for msg in reversed(messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        cursor.execute("""
            INSERT INTO chat_history (username, user_message, assistant_message, created_at)
            VALUES (%s, %s, %s, %s)
        """, (username, user_message, assistant_response, datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"チャット履歴の保存エラー: {str(e)}")

# アプリケーション起動時にデータベースを初期化
@app.on_event("startup")
async def startup_event():
    init_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)