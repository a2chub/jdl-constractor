# JDL Constructor Management System

JDLコンストラクター管理システムは、ドローンレース大会におけるチーム、選手、監督の管理を効率化するためのWebアプリケーションです。

## 主な機能

### 1. チーム・選手管理
- チーム情報の登録・編集
- 選手の登録・移籍管理
- JDL IDマスターとの連携による選手情報の検証
- クラス別選手管理

### 2. 監督管理
- チーム監督の登録・変更
- 監督権限の委譲・継承
- 複数監督の権限管理

### 3. 大会管理
- ラウンドごとの選手エントリー
- クラス別ポイント管理
- 大会結果の記録・集計

### 4. アクセス管理
- Gmailアカウントによる認証
- ロールベースのアクセス制御
- 監督・管理者権限の管理

## プロジェクト構成

```
jdl-constructor/
├── frontend/          # フロントエンドアプリケーション (React/TypeScript)
├── backend/           # バックエンドアプリケーション (Firebase Functions)
├── docs/             # プロジェクトドキュメント
│   ├── requirements/ # 要件定義ドキュメント
│   ├── diagrams/    # システム設計図
│   ├── api/         # API仕様書
│   └── database/    # データベース設計書
├── scripts/          # 開発・デプロイメントスクリプト
└── docker-compose.yml # 開発環境設定
```

## 技術仕様

### システム要件
- Webアプリケーション（フロントエンド）
- データ保持期間：1年間
- 日本語・英語対応（予定）

### セキュリティ
- OAuth2.0による認証
- データ暗号化
- アクセスログの記録

### 外部連携
- JDL IDマスターデータ連携
- 大会結果CSVインポート

## ドキュメント
詳細な仕様については、以下のドキュメントを参照してください：

### 主要ドキュメント（推奨読書順）

1. システム概要と要件
   - [システム仕様書](docs/requirements/constructor-management-system.md)
   - [コンストラクタールールブック2025](docs/requirements/constructor-rulebook-2025.md)

2. 技術仕様と設計
   - [アーキテクチャ設計書](docs/architecture/README.md)
   - [データベース設計書](docs/database/README.md)
   - [API仕様書](docs/api/README.md)

3. セキュリティと運用
   - [セキュリティ要件](docs/requirements/security-requirements.md)
   - [マスターデータ連携仕様](docs/requirements/master-data-integration.md)

4. 開発ガイド
   - [開発環境セットアップ](docs/development/setup.md)
   - [コーディング規約](docs/development/coding-guidelines.md)
   - [テスト方針](docs/development/testing-guidelines.md)

5. 実装計画と進捗
   - [実装計画書](docs/implementation-plan.md)
   - [プロジェクト履歴](docs/project-history.md)

## ライセンス
Copyright (c) 2024 JDL. All rights reserved.