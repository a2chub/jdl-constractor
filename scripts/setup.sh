#!/bin/bash

# エラーが発生した場合にスクリプトを終了
set -e

# 色付きの出力用の関数
print_info() {
    echo -e "\033[0;34m[INFO] $1\033[0m"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS] $1\033[0m"
}

print_error() {
    echo -e "\033[0;31m[ERROR] $1\033[0m"
}

# 必要なソフトウェアの確認
check_requirements() {
    print_info "必要なソフトウェアの確認中..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3がインストールされていません"
        exit 1
    fi
    
    # Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.jsがインストールされていません"
        exit 1
    fi
    
    # npm
    if ! command -v npm &> /dev/null; then
        print_error "npmがインストールされていません"
        exit 1
    fi
}

# バックエンド環境のセットアップ
setup_backend() {
    print_info "バックエンド環境のセットアップを開始..."
    
    cd backend
    
    # Python仮想環境の作成
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # 仮想環境のアクティベート
    source venv/bin/activate
    
    # 依存パッケージのインストール
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    
    # .env ファイルの作成
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_info ".envファイルを作成しました。必要な環境変数を設定してください。"
    fi
    
    cd ..
    print_success "バックエンド環境のセットアップが完了しました"
}

# フロントエンド環境のセットアップ
setup_frontend() {
    print_info "フロントエンド環境のセットアップを開始..."
    
    cd frontend
    
    # 依存パッケージのインストール
    npm install
    
    # .env.local ファイルの作成
    if [ ! -f ".env.local" ]; then
        cp .env.example .env.local
        print_info ".env.localファイルを作成しました。必要な環境変数を設定してください。"
    fi
    
    cd ..
    print_success "フロントエンド環境のセットアップが完了しました"
}

# VSCode設定の作成
setup_vscode() {
    print_info "VSCode設定の作成を開始..."
    
    mkdir -p .vscode
    
    # launch.json の作成
    cat > .vscode/launch.json << EOL
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
EOL
    
    # settings.json の作成
    cat > .vscode/settings.json << EOL
{
    "python.defaultInterpreterPath": "./backend/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
EOL
    
    print_success "VSCode設定の作成が完了しました"
}

# メイン処理
main() {
    print_info "開発環境のセットアップを開始します..."
    
    # 必要なソフトウェアの確認
    check_requirements
    
    # バックエンド環境のセットアップ
    setup_backend
    
    # フロントエンド環境のセットアップ
    setup_frontend
    
    # VSCode設定の作成
    setup_vscode
    
    print_success "開発環境のセットアップが完了しました"
    print_info "以下の手順を実行してください："
    echo "1. backend/.env ファイルに必要な環境変数を設定"
    echo "2. frontend/.env.local ファイルに必要な環境変数を設定"
    echo "3. Firebase認証情報を backend/firebase-credentials.json として保存"
}

# スクリプトの実行
main 