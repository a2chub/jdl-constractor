# JDL IDマスター連携仕様書

## 1. 概要

### 1.1 目的
- JDL IDマスターデータとの連携による選手情報の検証
- 出場歴情報の確認
- クラス情報の同期

### 1.2 連携方式
- CSVファイルによる一括更新
- 1日1回の手動更新
- エラー時は管理者に通知

## 2. データ連携仕様

### 2.1 データ形式
1. CSVファイル形式
   - 文字コード：UTF-8
   - 改行コード：LF
   - 区切り文字：カンマ(,)

2. ファイル構成
   ```csv
   # players.csv
   jdl_id,player_name,participation_count,current_class,last_updated
   ```

### 2.2 更新プロセス
1. 管理者がCSVファイルをアップロード
2. システムがデータを検証
3. 問題なければ一括更新実行
4. 更新結果を管理者に通知

## 3. エラー処理

### 3.1 データ検証
- JDL ID形式チェック
- 必須項目の存在確認
- データ型チェック

### 3.2 エラー通知
- エラー内容をログに記録
- 管理者にメール通知
- エラーデータの一覧表示

## 4. リカバリ処理

### 4.1 手動リカバリ
- 前回の更新データを保持
- 管理者による更新の取り消し
- 手動での再実行

## 5. セキュリティ

### 5.1 アクセス制御
- 管理者のみがアップロード可能
- 更新履歴の記録
- 操作ログの保管（7日間） 