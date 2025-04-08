# API仕様書

## 1. 概要

JDLコンストラクター管理システムのAPIは、RESTful原則に従い、JSON形式でデータを送受信します。

### 1.1 ベースURL
```
https://api.jdl-constructor.com/api/v1
```

### 1.2 認証
全てのAPIリクエストには、Firebase認証によって発行されたJWTトークンが必要です。

```http
Authorization: Bearer <firebase-jwt-token>
```

## 2. エンドポイント一覧

### 2.1 チーム管理 API

#### チーム作成
```http
POST /teams
```

**リクエスト**
```json
{
  "name": "チーム名",
  "description": "チーム説明",
  "manager_id": "監督のUID"
}
```

**レスポンス**
```json
{
  "id": "team-id",
  "name": "チーム名",
  "description": "チーム説明",
  "manager_id": "監督のUID",
  "created_at": "2024-03-20T12:00:00Z",
  "updated_at": "2024-03-20T12:00:00Z"
}
```

#### チーム一覧取得
```http
GET /teams
```

**レスポンス**
```json
{
  "teams": [
    {
      "id": "team-id",
      "name": "チーム名",
      "description": "チーム説明",
      "manager_id": "監督のUID",
      "created_at": "2024-03-20T12:00:00Z",
      "updated_at": "2024-03-20T12:00:00Z"
    }
  ]
}
```

### 2.2 選手管理 API

#### 選手登録
```http
POST /teams/{team_id}/players
```

**リクエスト**
```json
{
  "name": "選手名",
  "jdl_id": "JDL-ID",
  "class": "選手クラス"
}
```

**レスポンス**
```json
{
  "id": "player-id",
  "name": "選手名",
  "jdl_id": "JDL-ID",
  "class": "選手クラス",
  "team_id": "team-id",
  "joined_at": "2024-03-20T12:00:00Z"
}
```

#### チーム所属選手一覧
```http
GET /teams/{team_id}/players
```

**レスポンス**
```json
{
  "players": [
    {
      "id": "player-id",
      "name": "選手名",
      "jdl_id": "JDL-ID",
      "class": "選手クラス",
      "team_id": "team-id",
      "joined_at": "2024-03-20T12:00:00Z"
    }
  ]
}
```

### 2.3 大会管理 API

#### 大会作成
```http
POST /tournaments
```

**リクエスト**
```json
{
  "name": "大会名",
  "start_date": "2024-04-01T00:00:00Z",
  "end_date": "2024-04-02T00:00:00Z"
}
```

**レスポンス**
```json
{
  "id": "tournament-id",
  "name": "大会名",
  "start_date": "2024-04-01T00:00:00Z",
  "end_date": "2024-04-02T00:00:00Z",
  "created_at": "2024-03-20T12:00:00Z"
}
```

#### ラウンド登録
```http
POST /tournaments/{tournament_id}/rounds
```

**リクエスト**
```json
{
  "date": "2024-04-01T09:00:00Z",
  "entries": [
    {
      "player_id": "player-id",
      "team_id": "team-id",
      "class": "選手クラス"
    }
  ]
}
```

**レスポンス**
```json
{
  "id": "round-id",
  "tournament_id": "tournament-id",
  "date": "2024-04-01T09:00:00Z",
  "entries": [
    {
      "id": "entry-id",
      "player_id": "player-id",
      "team_id": "team-id",
      "class": "選手クラス",
      "points": 0
    }
  ]
}
```

### 2.4 ポイント管理 API

#### ポイント更新
```http
PUT /tournaments/{tournament_id}/rounds/{round_id}/entries/{entry_id}/points
```

**リクエスト**
```json
{
  "points": 100
}
```

**レスポンス**
```json
{
  "id": "entry-id",
  "player_id": "player-id",
  "team_id": "team-id",
  "class": "選手クラス",
  "points": 100,
  "updated_at": "2024-03-20T12:00:00Z"
}
```

#### チームポイント集計
```http
GET /tournaments/{tournament_id}/teams/{team_id}/points
```

**レスポンス**
```json
{
  "team_id": "team-id",
  "tournament_id": "tournament-id",
  "total_points": 500,
  "points_by_round": [
    {
      "round_id": "round-id",
      "points": 100,
      "date": "2024-04-01T09:00:00Z"
    }
  ]
}
```

## 3. エラーレスポンス

### 3.1 エラーフォーマット
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": {
      "field": "エラーの詳細情報"
    }
  }
}
```

### 3.2 エラーコード
| コード | 説明 |
|--------|------|
| 400 | リクエストが不正です |
| 401 | 認証が必要です |
| 403 | 権限がありません |
| 404 | リソースが見つかりません |
| 409 | リソースが競合しています |
| 500 | サーバーエラー |

## 4. レート制限

- リクエスト制限: 100回/分
- 制限超過時のレスポンス:
  ```http
  HTTP/1.1 429 Too Many Requests
  Retry-After: 60
  ```

## 5. データ型定義

### 5.1 共通フィールド
| フィールド | 型 | 説明 |
|------------|------|------|
| id | string | リソースの一意識別子 |
| created_at | string (ISO 8601) | 作成日時 |
| updated_at | string (ISO 8601) | 更新日時 |

### 5.2 チーム
| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| name | string | ○ | チーム名 |
| description | string | - | チーム説明 |
| manager_id | string | ○ | 監督のUID |

### 5.3 選手
| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| name | string | ○ | 選手名 |
| jdl_id | string | ○ | JDL ID |
| class | string | ○ | 選手クラス |
| team_id | string | ○ | 所属チームID |

### 5.4 大会
| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| name | string | ○ | 大会名 |
| start_date | string (ISO 8601) | ○ | 開始日時 |
| end_date | string (ISO 8601) | ○ | 終了日時 |

## 6. セキュリティ

### 6.1 認証
- Firebase認証を使用
- JWTトークンの有効期限: 1時間
- リフレッシュトークンの有効期限: 2週間

### 6.2 権限
| ロール | 権限 |
|--------|------|
| admin | 全ての操作が可能 |
| manager | 自チームの管理が可能 |
| player | 参照のみ可能 |

## 7. バージョニング

- URLにバージョンを含める: `/api/v1/`
- 後方互換性のない変更時にバージョンを更新
- 古いバージョンは6ヶ月間サポート 