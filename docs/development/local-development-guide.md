# ローカル開発環境セットアップガイド

## 1. 前提条件

### 1.1 必要なソフトウェア
- Python 3.11以上
- Node.js 18以上
- Git
- Docker (オプション)
- VSCode (推奨エディタ)

### 1.2 必要なアカウントと認証情報
- GitHub アカウント
- Firebase プロジェクトのアクセス権限
- GCP プロジェクトのアクセス権限

## 2. 初期セットアップ

### 2.1 リポジトリのクローン
```bash
git clone https://github.com/a2chub/jdl-constractor.git
cd jdl-constractor
```

### 2.2 環境変数の設定
1. 開発用の環境変数ファイルを作成
```bash
# フロントエンド
cp frontend/.env.example frontend/.env.local

# バックエンド
cp backend/.env.example backend/.env
```

2. 環境変数の設定
```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-auth-domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id

# backend/.env
FIREBASE_CREDENTIALS=path/to/your/firebase-credentials.json
CORS_ORIGINS=http://localhost:3000
```

### 2.3 Firebase認証情報の設定
1. Firebase Console から サービスアカウントキーをダウンロード
   - Firebase Console → プロジェクト設定 → サービスアカウント
   - 「新しい秘密鍵の生成」をクリック
   - ダウンロードしたJSONファイルを `backend/firebase-credentials.json` として保存

2. Firebaseプロジェクト設定の取得
   - Firebase Console → プロジェクト設定 → 全般
   - ウェブアプリの設定値を `frontend/.env.local` に設定

## 3. バックエンド開発環境のセットアップ

### 3.1 Python仮想環境の作成
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

### 3.2 依存パッケージのインストール
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開発用パッケージ
```

### 3.3 バックエンドの起動
```bash
uvicorn app.main:app --reload --port 8000
```

## 4. フロントエンド開発環境のセットアップ

### 4.1 依存パッケージのインストール
```bash
cd frontend
npm install
```

### 4.2 フロントエンドの起動
```bash
npm run dev
```

## 5. 開発用スクリプト

### 5.1 開発環境の一括起動
```bash
# scripts/dev.sh
#!/bin/bash
tmux new-session -d -s dev
tmux split-window -h

# バックエンド起動
tmux send-keys -t 0 'cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000' C-m

# フロントエンド起動
tmux send-keys -t 1 'cd frontend && npm run dev' C-m

tmux attach-session -t dev
```

### 5.2 テストの実行
```bash
# バックエンドテスト
cd backend
pytest

# フロントエンドテスト
cd frontend
npm test
```

## 6. 開発フロー

### 6.1 ブランチ戦略
- `main`: 本番環境用ブランチ
- `develop`: 開発用ブランチ
- 機能開発: `feature/機能名`
- バグ修正: `fix/バグ内容`
- リリース: `release/バージョン番号`

### 6.2 コミットメッセージ規約
```
feat: 新機能
fix: バグ修正
docs: ドキュメントのみの変更
style: コードスタイルの変更
refactor: リファクタリング
test: テストコードの追加・修正
chore: ビルドプロセスやツールの変更
```

## 7. デバッグ方法

### 7.1 バックエンドデバッグ
1. VSCodeでのデバッグ設定
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

2. ログの確認
```python
# app/core/logging.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 7.2 フロントエンドデバッグ
1. Chromeデベロッパーツール
   - React Developer Tools
   - Redux DevTools (状態管理用)

2. デバッグログの設定
```typescript
// frontend/src/lib/logger.ts
const logger = {
  debug: (message: string, ...args: any[]) => {
    if (process.env.NODE_ENV === 'development') {
      console.debug(message, ...args);
    }
  },
  // ... other log levels
};
```

## 8. トラブルシューティング

### 8.1 よくある問題と解決方法
1. CORS エラー
   - バックエンドの CORS_ORIGINS 設定を確認
   - フロントエンドの API_URL 設定を確認

2. Firebase認証エラー
   - 認証情報の設定を確認
   - Firebaseプロジェクトの設定を確認

3. 環境変数の問題
   - .env ファイルの存在確認
   - 環境変数の値が正しく設定されているか確認

### 8.2 ログの確認方法
1. バックエンドログ
   - コンソール出力の確認
   - logging モジュールの出力確認

2. フロントエンドログ
   - ブラウザのコンソール確認
   - React Developer Tools の確認

## 9. 開発環境のメンテナンス

### 9.1 定期的な更新
```bash
# 依存パッケージの更新
# バックエンド
pip list --outdated
pip install -U パッケージ名

# フロントエンド
npm outdated
npm update
```

### 9.2 キャッシュのクリア
```bash
# バックエンド
find . -type d -name "__pycache__" -exec rm -r {} +

# フロントエンド
npm clean-install
``` 