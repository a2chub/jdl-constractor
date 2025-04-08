# Firebase設定仕様書

## 1. Firestore データモデル

### 1.1 コレクション構造
```typescript
// teams collection
interface Team {
  id: string;              // チームID
  name: string;            // チーム名
  description: string;     // 説明
  logoUrl: string;        // ロゴURL
  managerIds: string[];   // 監督のUID配列
  status: 'active' | 'archived';
  memberCount: number;    // メンバー数
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

// players collection
interface Player {
  id: string;             // JDL ID
  name: string;           // 選手名
  teamId: string;         // 所属チームID
  currentClass: string;   // 現在のクラス
  participationCount: number;
  status: 'active' | 'inactive';
  joinedAt: Timestamp;
}

// tournaments collection
interface Tournament {
  id: string;
  name: string;
  startDate: Timestamp;
  endDate: Timestamp;
  status: 'upcoming' | 'active' | 'completed';
}
```

### 1.2 インデックス設定
```javascript
{
  "indexes": [
    {
      "collectionGroup": "players",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "teamId", "order": "ASCENDING" },
        { "fieldPath": "status", "order": "ASCENDING" }
      ]
    },
    {
      "collectionGroup": "tournaments",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "status", "order": "ASCENDING" },
        { "fieldPath": "startDate", "order": "DESCENDING" }
      ]
    }
  ]
}
```

## 2. セキュリティルール

### 2.1 基本ルール
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 認証チェック
    function isAuthenticated() {
      return request.auth != null;
    }
    
    // 管理者チェック
    function isAdmin() {
      return isAuthenticated() && 
        request.auth.token.role == 'admin';
    }
    
    // チーム監督チェック
    function isTeamManager(teamId) {
      return isAuthenticated() && 
        request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.managerIds;
    }

    // チームドキュメント
    match /teams/{teamId} {
      allow read: if isAuthenticated();
      allow create: if isAdmin();
      allow update: if isAdmin() || isTeamManager(teamId);
      allow delete: if isAdmin();
    }

    // プレイヤードキュメント
    match /players/{playerId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin() || 
        isTeamManager(resource.data.teamId);
    }
  }
}
```

## 3. Firebase Admin SDK設定

### 3.1 初期化
```python
# backend/app/core/firebase.py
import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('path/to/serviceAccount.json')
firebase_admin.initialize_app(cred)

def verify_id_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
```

### 3.2 カスタムクレーム
```python
def set_user_role(uid: str, role: str):
    auth.set_custom_user_claims(uid, {'role': role})
```

## 4. エラー処理

### 4.1 Firestore エラー
```typescript
try {
  await db.runTransaction(async (transaction) => {
    // トランザクション処理
  });
} catch (error) {
  if (error.code === 'failed-precondition') {
    // トランザクション前提条件エラー
  } else if (error.code === 'aborted') {
    // トランザクション競合
  }
  throw error;
}
```

### 4.2 認証エラー
```typescript
try {
  await auth().verifyIdToken(token);
} catch (error) {
  if (error.code === 'auth/id-token-expired') {
    // トークン期限切れ
  } else if (error.code === 'auth/id-token-revoked') {
    // トークン無効化
  }
  throw error;
}
``` 