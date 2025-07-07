#!/bin/bash
# -------------------------------------------------
# ・ファイル名：setup_environment.sh
# ・ファイル内容：環境設定自動化スクリプト
# ・作成日時：2025/07/07 Claude Code
# -------------------------------------------------

echo "🚀 WebApp 環境設定を開始します..."

# 1. PostgreSQL設定確認
echo "📊 PostgreSQL設定を確認中..."
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQLがインストールされていません"
    echo "以下のコマンドでインストールしてください:"
    echo "sudo apt update && sudo apt install -y postgresql postgresql-contrib"
    exit 1
fi

# 2. PostgreSQLサービス状態確認
if ! systemctl is-active --quiet postgresql; then
    echo "⚠️ PostgreSQLサービスが停止しています"
    echo "以下のコマンドでサービスを開始してください:"
    echo "sudo systemctl start postgresql"
    echo "sudo systemctl enable postgresql"
fi

# 3. Python仮想環境の設定
echo "🐍 Python仮想環境を設定中..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 仮想環境を作成しました"
fi

source venv/bin/activate
pip install -r requirements.txt
echo "✅ 依存関係をインストールしました"

# 4. 環境変数ファイルの確認
echo "⚙️ 環境変数ファイルを確認中..."
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "⚠️ .env ファイルを作成しました"
    echo "📝 .env ファイルを編集してAzure OpenAI設定を追加してください"
    echo "   - AZURE_OPENAI_API_KEY"
    echo "   - AZURE_OPENAI_ENDPOINT"
    echo "   - AZURE_OPENAI_DEPLOYMENT_NAME"
else
    echo "✅ .env ファイルが存在します"
fi

# 5. データベース接続テスト
echo "🔗 データベース接続をテスト中..."
python3 -c "
import sys
sys.path.append('.')
from database import test_connection
if test_connection():
    print('✅ データベース接続成功')
else:
    print('❌ データベース接続失敗')
    print('PostgreSQLの設定を確認してください')
"

# 6. データベース初期化
echo "🗃️ データベースを初期化中..."
python3 init_db.py

# 7. Azure OpenAI接続テスト
echo "🤖 Azure OpenAI接続をテスト中..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('AZURE_OPENAI_API_KEY')
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

if not api_key or api_key == 'your-azure-openai-api-key-here':
    print('⚠️ Azure OpenAI API キーが設定されていません')
    print('📝 .env ファイルでAZURE_OPENAI_API_KEYを設定してください')
elif not endpoint or endpoint == 'https://your-resource-name.openai.azure.com/':
    print('⚠️ Azure OpenAI エンドポイントが設定されていません')
    print('📝 .env ファイルでAZURE_OPENAI_ENDPOINTを設定してください')
elif not deployment or deployment == 'your-deployment-name':
    print('⚠️ Azure OpenAI デプロイメント名が設定されていません')
    print('📝 .env ファイルでAZURE_OPENAI_DEPLOYMENT_NAMEを設定してください')
else:
    print('✅ Azure OpenAI設定が完了しています')
"

# 8. フロントエンド依存関係のインストール
echo "⚛️ フロントエンド依存関係をインストール中..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ フロントエンド依存関係をインストールしました"
else
    echo "✅ フロントエンド依存関係は既にインストールされています"
fi

cd ..

echo ""
echo "🎉 環境設定が完了しました！"
echo ""
echo "次のステップ:"
echo "1. 📝 backend/.env ファイルでAzure OpenAI設定を完了してください"
echo "2. 🚀 アプリケーションを起動してください:"
echo "   - バックエンド: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   - フロントエンド: cd frontend && npm start"
echo "3. 🧪 テストを実行してください:"
echo "   - 単体テスト: python test_unit.py"
echo "   - 結合テスト: python test_integration.py"
echo "   - 運用テスト: python test_e2e.py"
echo ""