# プロジェクト構造

## 1. ディレクトリ構成

```
jdl-constractor/
├── frontend/                # Next.jsアプリケーション
│   ├── src/
│   │   ├── app/           # ページコンポーネント
│   │   │   ├── (auth)/    # 認証関連ページ
│   │   │   ├── teams/     # チーム管理ページ
│   │   │   ├── players/   # 選手管理ページ
│   │   │   └── admin/     # 管理者ページ
│   │   ├── components/    # UIコンポーネント
│   │   │   ├── common/    # 共通コンポーネント
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   └── Input.tsx
│   │   │   └── features/  # 機能別コンポーネント
│   │   ├── styles/       # スタイル定義
│   │   │   ├── globals.css  # グローバルスタイル
│   │   │   └── themes/    # テーマ設定
│   │   └── lib/          # ユーティリティ
│   │       ├── firebase/  # Firebase設定
│   │       ├── api/       # APIクライアント
│   │       └── hooks/     # カスタムフック
│   ├── public/            # 静的ファイル
│   ├── tailwind.config.js # Tailwind CSS設定
│   ├── postcss.config.js  # PostCSS設定
│   └── tests/            # フロントエンドテスト
│
├── backend/                # FastAPIアプリケーション
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/       # APIエンドポイント
│   │   │       ├── teams.py
│   │   │       ├── players.py
│   │   │       └── tournaments.py
│   │   ├── core/         # コア機能
│   │   │   ├── auth.py   # Firebase認証
│   │   │   ├── config.py # 設定
│   │   │   └── logging.py # ロギング設定
│   │   ├── models/       # Pydanticモデル
│   │   │   ├── team.py
│   │   │   ├── player.py
│   │   │   └── tournament.py
│   │   ├── services/     # ビジネスロジック
│   │   │   ├── team_service.py
│   │   │   ├── player_service.py
│   │   │   └── tournament_service.py
│   │   └── utils/        # ユーティリティ
│   ├── tests/            # バックエンドテスト
│   │   ├── api/
│   │   ├── services/
│   │   └── conftest.py
│   └── main.py           # アプリケーションエントリーポイント
│
├── terraform/             # インフラ定義
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── modules/
│
└── docs/                 # ドキュメント
    ├── architecture/     # アーキテクチャ設計
    ├── api/             # API仕様
    └── requirements/    # 要件定義
```

## 2. コンポーネント詳細

### 2.1 フロントエンド (Next.js + Tailwind CSS)

#### スタイリング構造
```typescript
// src/components/common/Button.tsx
const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md' 
}: ButtonProps) => {
  const baseStyles = "rounded-md font-medium transition-colors duration-200";
  const variants = {
    primary: "bg-primary-600 hover:bg-primary-700 text-white",
    secondary: "bg-gray-200 hover:bg-gray-300 text-gray-800",
    outline: "border-2 border-primary-600 text-primary-600 hover:bg-primary-50"
  };
  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg"
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${sizes[size]}`}
    >
      {children}
    </button>
  );
};

// src/components/features/team/TeamCard.tsx
const TeamCard = ({ team }: TeamCardProps) => {
  return (
    <div className="
      bg-white 
      dark:bg-gray-800 
      rounded-lg 
      shadow-md 
      p-6 
      hover:shadow-lg 
      transition-shadow
      duration-300
    ">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
        {team.name}
      </h3>
      <p className="text-gray-600 dark:text-gray-300">
        {team.description}
      </p>
    </div>
  );
};
```

#### グローバルスタイル
```css
/* src/styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .input-primary {
    @apply w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent;
  }
  
  .card-container {
    @apply bg-white dark:bg-gray-800 rounded-lg shadow-md p-6;
  }
}
```

#### コンポーネント構造
- **ページコンポーネント**: アプリケーションのルーティングとページレイアウト
- **機能コンポーネント**: 特定の機能に関連するUI要素
- **共通コンポーネント**: 再利用可能なUI要素

#### 主要ファイル
```typescript
// src/lib/api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 5000,
});

// src/components/features/team/TeamList.tsx
import { useQuery } from 'react-query';
import { Team } from '@/types';

export const TeamList = () => {
  const { data: teams } = useQuery<Team[]>('teams', 
    () => apiClient.get('/teams').then(res => res.data)
  );
  
  return (
    // コンポーネントの実装
  );
};
```

### 2.2 バックエンド (FastAPI)

#### APIエンドポイント構造
- **v1**: 現在のAPIバージョン
- **モジュール別エンドポイント**: 機能ごとに分割されたルーター

#### 主要ファイル
```python
# app/api/v1/teams.py
from fastapi import APIRouter, Depends
from app.models.team import TeamCreate, TeamResponse
from app.services.team_service import TeamService

router = APIRouter()

@router.post("/teams/", response_model=TeamResponse)
async def create_team(
    team: TeamCreate,
    team_service: TeamService = Depends()
):
    return await team_service.create_team(team)

# app/models/team.py
from pydantic import BaseModel
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    description: str | None = None

class TeamCreate(TeamBase):
    manager_id: str

class TeamResponse(TeamBase):
    id: str
    created_at: datetime
    updated_at: datetime
```

### 2.3 テスト構造

#### フロントエンドテスト
```typescript
// tests/components/TeamList.test.tsx
import { render, screen } from '@testing-library/react';
import { TeamList } from '@/components/features/team/TeamList';

describe('TeamList', () => {
  it('チーム一覧を表示できること', async () => {
    render(<TeamList />);
    expect(await screen.findByText('チーム一覧')).toBeInTheDocument();
  });
});
```

#### バックエンドテスト
```python
# tests/api/test_teams.py
import pytest
from httpx import AsyncClient

async def test_create_team(client: AsyncClient):
    response = await client.post(
        "/api/v1/teams/",
        json={"name": "テストチーム", "manager_id": "test123"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "テストチーム"
```

## 3. 設定ファイル

### 3.1 フロントエンド設定
```json
// frontend/.env.example
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-auth-domain
```

### 3.2 バックエンド設定
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JDL Constructor Management API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    FIREBASE_CREDENTIALS: str

    class Config:
        env_file = ".env"

settings = Settings()
```

## 4. デプロイメント設定

### 4.1 Dockerファイル
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 4.2 Cloud Build設定
```yaml
# cloudbuild.yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/fastapi-backend', './backend']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/fastapi-backend']
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
  - 'run'
  - 'deploy'
  - 'fastapi-backend'
  - '--image'
  - 'gcr.io/$PROJECT_ID/fastapi-backend'
  - '--region'
  - 'asia-northeast1'
  - '--platform'
  - 'managed'
```

## 5. 開発環境セットアップ

### 5.1 必要条件
- Python 3.11以上
- Node.js 18以上
- Docker
- Firebase CLI
- Google Cloud SDK

### 5.2 環境構築手順
```bash
# バックエンド
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# フロントエンド
cd frontend
npm install

# 環境変数設定
cp .env.example .env
# .envファイルを編集

# 開発サーバー起動
# バックエンド
uvicorn main:app --reload

# フロントエンド
npm run dev
``` 