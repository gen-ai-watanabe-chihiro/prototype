# WebApp - ユーザー認証システム

## 📖 概要

このプロジェクトは、モダンなWebテクノロジーを使用して構築されたユーザー認証システムです。セキュアなログイン機能とダッシュボード画面を提供します。

## 🏗️ 技術スタック

- **バックエンド**: Python (FastAPI)
- **フロントエンド**: TypeScript + React
- **データベース**: PostgreSQL
- **コンテナ化**: Docker + Docker Compose
- **認証**: JWT (JSON Web Token)
- **実行環境**: Windows 11 WSL2 Ubuntu + Docker Engine
- **動作環境**: Windows 11 Google Chrome

## ✨ 機能

- **ユーザー認証**
  - セキュアなログイン/ログアウト機能
  - JWT認証による認可システム
  - パスワードハッシュ化による安全な認証情報保存

- **ダッシュボード**
  - 認証済みユーザー向けのメニュー画面
  - ユーザー情報の表示
  - システム情報の確認

## 🔧 セットアップ

### 前提条件

- Docker Engine
- Node.js (18.x以上)
- Python 3.11以上
- Git

### インストール

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd proto0000
```

2. **バックエンドの依存関係インストール**
```bash
cd backend
sudo apt install python3.12-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

3. **フロントエンドの依存関係インストール**
```bash
cd frontend
npm install
cd ..
```

4. **データベース起動**
```bash
docker compose up -d postgres
```

5. **バックエンド起動**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

6. **フロントエンド起動（新しいターミナル）**
```bash
cd frontend
npm start
```

7. **ログイン確認**
   - ブラウザで http://localhost:3000 にアクセス
   - 以下のテストユーザーでログインできることを確認:
     - **ユーザー名**: `testAI`
     - **パスワード**: `testAI00!`

## 🚀 起動方法

### 1. データベース起動
```bash
docker compose up -d postgres
```

### 2. バックエンド起動
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. フロントエンド起動
```bash
cd frontend
npm start
```
### フロントエンド起動時に「react-scripts: not found」が発生した場合
```bash
npm install react-scripts
```

### アクセス

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **API仕様書**: http://localhost:8000/docs

## 🛑 停止方法

### 1. アプリケーション停止
```bash
# 各ターミナルで実行
Ctrl + C  # フロントエンド停止
Ctrl + C  # バックエンド停止
```

### 2. データベース停止
```bash
# PostgreSQLコンテナのみ停止
docker compose stop postgres

# すべてのコンテナを停止
docker compose down

# コンテナとボリュームも削除（データも削除される）
docker compose down -v
```

### 3. 強制停止（必要時のみ）
```bash
# プロセス確認
lsof -i :3000  # フロントエンド
lsof -i :8000  # バックエンド
lsof -i :5432  # PostgreSQL

# 強制終了
sudo kill -9 $(lsof -t -i:3000)  # フロントエンド
sudo kill -9 $(lsof -t -i:8000)  # バックエンド
```

## 👤 テストユーザー

- **ユーザー名**: `testAI`
- **パスワード**: `testAI00!`

## 🧪 テスト

### 単体テスト実行
```bash
# バックエンドテスト
cd backend
source venv/bin/activate
python -m pytest test_main.py -v

# フロントエンドテスト
cd frontend
npm test -- --watchAll=false
```

### 統合テスト実行
```bash
# 総合テスト
source backend/venv/bin/activate
python test_integration.py

# 運用テスト（E2E）
python test_e2e.py
```

## 📁 プロジェクト構成

```
proto0000/
├── backend/                    # FastAPI バックエンド
│   ├── main.py                # メインアプリケーションファイル
│   ├── database.py            # データベース接続設定
│   ├── requirements.txt       # Python依存関係
│   ├── test_main.py          # 単体テスト
│   └── Dockerfile            # バックエンド用Dockerファイル
├── frontend/                   # React フロントエンド
│   ├── src/
│   │   ├── components/       # Reactコンポーネント
│   │   ├── contexts/         # Context API
│   │   └── App.tsx          # メインアプリケーション
│   ├── package.json         # Node.js依存関係
│   └── Dockerfile           # フロントエンド用Dockerファイル
├── docker-compose.yml         # Docker Compose設定
├── test_integration.py        # 総合テスト
├── test_e2e.py               # エンドツーエンドテスト
├── .env                      # 環境変数設定
└── README.md                 # このファイル
```

## 🔒 セキュリティ機能

- **JWT認証**: セキュアなトークンベース認証
- **パスワードハッシュ化**: bcryptによる安全なパスワード保存
- **CORS設定**: クロスオリジンリクエストの適切な制御
- **認可システム**: 保護されたエンドポイントへのアクセス制御

## 🐛 トラブルシューティング

### よくある問題

1. **ポートが既に使用されている**
```bash
# 使用中のプロセスを確認
lsof -i :3000
lsof -i :8000
lsof -i :5432

# プロセスを停止
sudo kill -9 <PID>
```

2. **データベース接続エラー**
```bash
# PostgreSQLコンテナの状態確認
docker ps
docker logs proto0000-postgres-1

# コンテナ再起動
docker compose down
docker compose up -d postgres
```

3. **Node.jsの依存関係エラー**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📝 API仕様

### 認証エンドポイント

- `POST /login` - ユーザーログイン
- `GET /dashboard` - ダッシュボード情報取得（要認証）
- `GET /profile` - ユーザープロフィール取得（要認証）

詳細なAPI仕様は http://localhost:8000/docs で確認できます。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

---

**作成者**: Claude Code  
**作成日**: 2025/07/06  
**最終更新**: 2025/07/06
