#!/bin/bash

# カラー出力の設定
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 開発モードの確認（デフォルトはDocker無し）
USE_DOCKER=false
while getopts "d" opt; do
  case $opt in
    d) USE_DOCKER=true ;;
    \?) echo "Usage: $0 [-d] (use -d for Docker mode)" >&2; exit 1 ;;
  esac
done

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")/.." || exit 1

# Firebase設定の確認
if [ ! -f ".firebaserc" ]; then
    echo -e "${BLUE}Initializing Firebase project...${NC}"
    echo '{
        "projects": {
            "default": "jdl-constructor-local"
        }
    }' > .firebaserc
fi

# 実行中のプロセスをクリーンアップ
echo -e "${BLUE}Cleaning up existing processes...${NC}"
cleanup_ports() {
    local ports=(4001 8081 9099 3000 8000)
    for port in "${ports[@]}"; do
        pid=$(lsof -t -i:"$port" 2>/dev/null)
        if [ ! -z "$pid" ]; then
            echo -e "${BLUE}Killing process on port $port (PID: $pid)${NC}"
            kill "$pid" 2>/dev/null || true
        fi
    done
}

cleanup_docker() {
    echo -e "${BLUE}Stopping Docker containers...${NC}"
    docker-compose down 2>/dev/null || true
}

cleanup_ports

# Docker環境のクリーンアップ（必要な場合）
if [ "$USE_DOCKER" = true ]; then
    cleanup_docker
fi

# 全てのプロセスを終了するための関数
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    if [ "$USE_DOCKER" = true ]; then
        cleanup_docker
    else
        kill $EMULATOR_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        kill $BACKEND_PID 2>/dev/null || true
    fi
    cleanup_ports
    echo -e "${GREEN}All services have been stopped.${NC}"
    exit 0
}

# Ctrl+Cのハンドリング
trap cleanup SIGINT SIGTERM

# エミュレーターの起動確認を行う関数
check_emulator() {
    local max_attempts=30
    local attempt=1
    local wait_time=2

    echo -e "${BLUE}Waiting for Firebase Emulators to start...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        # Auth Emulatorの確認
        if curl -s http://localhost:9099 > /dev/null; then
            # Firestore Emulatorの確認
            if curl -s http://localhost:8081 > /dev/null; then
                echo -e "${GREEN}Firebase Emulators are ready!${NC}"
                return 0
            fi
        fi
        
        echo -e "${BLUE}Attempt $attempt/$max_attempts: Emulators not ready yet, waiting...${NC}"
        sleep $wait_time
        attempt=$((attempt + 1))
    done

    echo -e "${RED}Failed to connect to Firebase Emulators after $max_attempts attempts.${NC}"
    return 1
}

if [ "$USE_DOCKER" = true ]; then
    # Docker環境での起動
    echo -e "${BLUE}Starting services using Docker...${NC}"
    
    # Dockerイメージのビルドと起動
    docker-compose up --build -d

    # エミュレーターの起動
    echo -e "${BLUE}Starting Firebase Emulators...${NC}"
    firebase emulators:start --import=./dev-data --export-on-exit=./dev-data &
    EMULATOR_PID=$!

    # エミュレーターの起動確認
    if ! check_emulator; then
        echo -e "${RED}Failed to start Firebase Emulators. Cleaning up...${NC}"
        cleanup
        exit 1
    fi

    # 初期データの投入
    echo -e "${BLUE}Loading seed data...${NC}"
    node scripts/seed-emulator.js

else
    # 通常環境での起動
    # エミュレーターの起動
    echo -e "${BLUE}Starting Firebase Emulators...${NC}"
    firebase emulators:start --import=./dev-data --export-on-exit=./dev-data &
    EMULATOR_PID=$!

    # エミュレーターの起動確認
    if ! check_emulator; then
        echo -e "${RED}Failed to start Firebase Emulators. Cleaning up...${NC}"
        cleanup
        exit 1
    fi

    # 初期データの投入
    echo -e "${BLUE}Loading seed data...${NC}"
    node scripts/seed-emulator.js

    # フロントエンドの起動（開発モード）
    echo -e "${BLUE}Starting Frontend (Development Mode)...${NC}"
    cd frontend && npm install && npm run dev &
    FRONTEND_PID=$!

    # バックエンドの起動
    echo -e "${BLUE}Starting Backend...${NC}"
    cd ../backend && python3 -m pip install -r requirements.txt > /dev/null 2>&1
    python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
fi

echo -e "${GREEN}Development environment is ready!${NC}"
echo -e "${GREEN}Access the following URLs:${NC}"
echo -e "${BLUE}- Frontend: ${NC}http://localhost:3000"
echo -e "${BLUE}- Backend: ${NC}http://localhost:8000"
echo -e "${BLUE}- Emulator UI: ${NC}http://localhost:4001"
echo -e "${BLUE}- Firestore Emulator: ${NC}http://localhost:8081"
echo -e "${BLUE}- Auth Emulator: ${NC}http://localhost:9099"

if [ "$USE_DOCKER" = true ]; then
    echo -e "\n${BLUE}Docker containers are running in the background.${NC}"
    echo -e "${BLUE}Use Ctrl+C to stop all services.${NC}"
fi

# プロセスの待機
wait 