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

# バックエンドのテスト実行
run_backend_tests() {
    print_info "バックエンドのテストを開始..."
    
    cd backend
    source venv/bin/activate
    
    # 単体テストの実行
    print_info "単体テストを実行中..."
    python -m pytest tests/unit -v
    
    # 統合テストの実行
    print_info "統合テストを実行中..."
    python -m pytest tests/integration -v
    
    # カバレッジレポートの生成
    print_info "カバレッジレポートを生成中..."
    python -m pytest --cov=app tests/ --cov-report=html
    
    deactivate
    cd ..
    
    print_success "バックエンドのテストが完了しました"
}

# フロントエンドのテスト実行
run_frontend_tests() {
    print_info "フロントエンドのテストを開始..."
    
    cd frontend
    
    # 単体テストの実行
    print_info "単体テストを実行中..."
    npm run test
    
    # E2Eテストの実行
    print_info "E2Eテストを実行中..."
    npm run test:e2e
    
    cd ..
    
    print_success "フロントエンドのテストが完了しました"
}

# リンターの実行
run_linters() {
    print_info "リンターチェックを開始..."
    
    # バックエンドのリンター
    cd backend
    source venv/bin/activate
    print_info "バックエンドのリンターを実行中..."
    flake8 app tests
    black --check app tests
    isort --check-only app tests
    deactivate
    cd ..
    
    # フロントエンドのリンター
    cd frontend
    print_info "フロントエンドのリンターを実行中..."
    npm run lint
    cd ..
    
    print_success "リンターチェックが完了しました"
}

# 型チェックの実行
run_type_checks() {
    print_info "型チェックを開始..."
    
    # バックエンドの型チェック
    cd backend
    source venv/bin/activate
    print_info "バックエンドの型チェックを実行中..."
    mypy app tests
    deactivate
    cd ..
    
    # フロントエンドの型チェック
    cd frontend
    print_info "フロントエンドの型チェックを実行中..."
    npm run type-check
    cd ..
    
    print_success "型チェックが完了しました"
}

# メイン処理
main() {
    print_info "テストスイートを開始します..."
    
    # リンターの実行
    run_linters
    
    # 型チェックの実行
    run_type_checks
    
    # バックエンドのテスト実行
    run_backend_tests
    
    # フロントエンドのテスト実行
    run_frontend_tests
    
    print_success "全てのテストが完了しました"
}

# コマンドライン引数の処理
case "$1" in
    "backend")
        run_backend_tests
        ;;
    "frontend")
        run_frontend_tests
        ;;
    "lint")
        run_linters
        ;;
    "type")
        run_type_checks
        ;;
    *)
        main
        ;;
esac 