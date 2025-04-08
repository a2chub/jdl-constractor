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

# 必要な環境変数のチェック
check_environment() {
    print_info "環境変数のチェック中..."
    
    if [ -z "$PROJECT_ID" ]; then
        print_error "PROJECT_ID環境変数が設定されていません"
        exit 1
    fi
    
    if [ -z "$REGION" ]; then
        print_error "REGION環境変数が設定されていません"
        exit 1
    fi
}

# Dockerイメージのビルドとプッシュ
build_and_push() {
    local service=$1
    local image_name="gcr.io/$PROJECT_ID/$service"
    
    print_info "$serviceのDockerイメージをビルド中..."
    docker build -t $image_name ./$service
    
    print_info "イメージをContainer Registryにプッシュ中..."
    docker push $image_name
    
    echo $image_name
}

# Cloud Runへのデプロイ
deploy_to_cloud_run() {
    local service=$1
    local image_name=$2
    
    print_info "$serviceをCloud Runにデプロイ中..."
    
    gcloud run deploy $service \
        --image $image_name \
        --platform managed \
        --region $REGION \
        --project $PROJECT_ID \
        --allow-unauthenticated
}

# テストの実行
run_tests() {
    print_info "テストを実行中..."
    
    print_info "バックエンドのテストを実行..."
    docker-compose run --rm backend-test
    
    print_info "フロントエンドのテストを実行..."
    docker-compose run --rm frontend-test
}

# メイン処理
main() {
    print_info "デプロイを開始します..."
    
    # 環境変数のチェック
    check_environment
    
    # テストの実行
    run_tests
    
    # バックエンドのデプロイ
    local backend_image=$(build_and_push "backend")
    deploy_to_cloud_run "backend" $backend_image
    
    # フロントエンドのデプロイ
    local frontend_image=$(build_and_push "frontend")
    deploy_to_cloud_run "frontend" $frontend_image
    
    print_success "デプロイが完了しました"
    print_info "以下のURLでアプリケーションにアクセスできます："
    gcloud run services describe frontend --format='value(status.url)' --project $PROJECT_ID --region $REGION
}

# コマンドライン引数の処理
case "$1" in
    "backend")
        check_environment
        backend_image=$(build_and_push "backend")
        deploy_to_cloud_run "backend" $backend_image
        ;;
    "frontend")
        check_environment
        frontend_image=$(build_and_push "frontend")
        deploy_to_cloud_run "frontend" $frontend_image
        ;;
    "test")
        run_tests
        ;;
    *)
        main
        ;;
esac 