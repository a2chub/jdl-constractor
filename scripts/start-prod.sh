#!/bin/bash

# 本番環境用のDockerコンテナを起動
echo "Starting Production Services..."
docker-compose -f docker-compose.prod.yml up --build -d

# ログの表示
echo "Showing logs (Ctrl+C to exit)..."
docker-compose -f docker-compose.prod.yml logs -f 