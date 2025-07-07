# Azure OpenAI設定手順

## 1. Azure OpenAI リソースの作成

### Azure ポータルでの手順：

1. **Azure ポータルにログイン**
   - https://portal.azure.com にアクセス

2. **Azure OpenAI リソースの作成**
   ```
   「リソースの作成」→「AI + Machine Learning」→「Azure OpenAI」
   ```

3. **基本設定**
   - サブスクリプション: お使いのサブスクリプション
   - リソースグループ: 新規作成または既存を選択
   - リージョン: East US または West Europe（推奨）
   - 名前: webapp-openai-resource（任意）
   - 価格レベル: Standard S0

4. **ネットワーク設定**
   - 「すべてのネットワーク」を選択（開発環境の場合）

5. **確認と作成**
   - 設定を確認して「作成」をクリック

## 2. モデルのデプロイ

### Azure OpenAI Studio での手順：

1. **Azure OpenAI Studio にアクセス**
   - 作成したリソースから「Azure OpenAI Studio に移動」

2. **モデルのデプロイ**
   ```
   「デプロイメント」→「新しいデプロイメント」
   ```

3. **モデル選択**
   - モデル: gpt-35-turbo または gpt-4
   - バージョン: 最新版
   - デプロイメント名: webapp-chat-model（任意）

4. **デプロイメント設定**
   - トークン/分制限: 10K（開発環境）
   - コンテンツフィルター: 既定値

## 3. 認証情報の取得

### 必要な情報：

1. **API キー**
   - リソース → 「キーとエンドポイント」
   - KEY 1 をコピー

2. **エンドポイント**
   - 同じページの「エンドポイント」をコピー
   - 形式: `https://your-resource-name.openai.azure.com/`

3. **デプロイメント名**
   - Azure OpenAI Studio → 「デプロイメント」
   - 作成したモデルのデプロイメント名をコピー

## 4. 環境変数の設定

### .env ファイルの作成：

```bash
# .env.template をコピーして .env ファイルを作成
cp .env.template .env
```

### .env ファイルの編集：

```bash
# Azure OpenAI設定を実際の値に置き換え
AZURE_OPENAI_API_KEY=your-actual-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=webapp-chat-model
```

## 5. テスト用クイックスタートスクリプト

### 接続テスト：

```python
# test_azure_connection.py
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

try:
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": "Hello, Azure OpenAI!"}],
        max_tokens=50
    )
    print("✅ Azure OpenAI接続成功:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ Azure OpenAI接続エラー: {e}")
```

## 6. 料金と制限

### 開発環境での推奨設定：

- **トークン制限**: 10,000 トークン/分
- **モデル**: gpt-35-turbo（コスト効率が良い）
- **リージョン**: East US（レイテンシー重視）

### 料金の目安：

- gpt-35-turbo: $0.0015/1K input tokens, $0.002/1K output tokens
- gpt-4: $0.03/1K input tokens, $0.06/1K output tokens

## 7. セキュリティ対策

### 本番環境での注意点：

1. **キーの管理**
   - .env ファイルを .gitignore に追加
   - Azure Key Vault の使用を検討

2. **ネットワーク制限**
   - 本番環境では IP アドレス制限を設定

3. **アクセス制御**
   - Azure RBAC でアクセス権限を管理

4. **監査**
   - Azure Monitor でアクセスログを監視