# バックエンド実装仕様書

## 1. FastAPI実装

### 1.1 アプリケーション構造
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(title=settings.PROJECT_NAME)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
```

### 1.2 認証ミドルウェア
```python
# backend/app/api/deps.py
from fastapi import Depends, HTTPException, status
from firebase_admin import auth
from app.core.firebase import verify_id_token

async def get_current_user(
    authorization: str = Header(None)
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報が不足しています",
        )
    
    token = authorization.split(" ")[1]
    try:
        return verify_id_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効な認証トークンです",
        )

async def get_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not current_user.get("role") == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です",
        )
    return current_user
```

## 2. エンドポイント実装

### 2.1 チーム管理API
```python
# backend/app/api/v1/teams.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.services.team_service import TeamService
from app.api.deps import get_current_user, get_admin_user

router = APIRouter()

@router.post("/teams/", response_model=TeamResponse)
async def create_team(
    team: TeamCreate,
    current_user: dict = Depends(get_admin_user),
    team_service: TeamService = Depends(),
):
    return await team_service.create_team(team, current_user["uid"])

@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(),
):
    team = await team_service.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="チームが見つかりません")
    return team
```

### 2.2 CSVアップロード処理
```python
# backend/app/api/v1/master_data.py
from fastapi import APIRouter, UploadFile, File, Depends
from app.services.csv_service import CSVService
from app.api.deps import get_admin_user

router = APIRouter()

@router.post("/master-data/upload")
async def upload_master_data(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_admin_user),
    csv_service: CSVService = Depends(),
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="CSVファイルのみアップロード可能です",
        )
    
    try:
        result = await csv_service.process_master_data(file)
        return {"message": "アップロード成功", "details": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 3. サービス層実装

### 3.1 チームサービス
```python
# backend/app/services/team_service.py
from firebase_admin import firestore
from app.schemas.team import TeamCreate, TeamUpdate

class TeamService:
    def __init__(self):
        self.db = firestore.client()
        self.teams_ref = self.db.collection('teams')

    async def create_team(self, team: TeamCreate, manager_id: str):
        team_data = team.dict()
        team_data["managerIds"] = [manager_id]
        team_data["status"] = "active"
        team_data["memberCount"] = 0
        team_data["createdAt"] = firestore.SERVER_TIMESTAMP
        team_data["updatedAt"] = firestore.SERVER_TIMESTAMP

        doc_ref = self.teams_ref.document()
        await doc_ref.set(team_data)
        
        return {**team_data, "id": doc_ref.id}

    async def get_team(self, team_id: str):
        doc = await self.teams_ref.document(team_id).get()
        if not doc.exists:
            return None
        return {**doc.to_dict(), "id": doc.id}
```

### 3.2 CSVサービス
```python
# backend/app/services/csv_service.py
import csv
import io
from firebase_admin import firestore
from app.schemas.player import PlayerUpdate

class CSVService:
    def __init__(self):
        self.db = firestore.client()
        self.players_ref = self.db.collection('players')

    async def process_master_data(self, file: UploadFile):
        content = await file.read()
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))

        batch = self.db.batch()
        updated_count = 0
        errors = []

        for row in csv_reader:
            try:
                player_ref = self.players_ref.document(row['jdl_id'])
                batch.set(player_ref, {
                    'name': row['player_name'],
                    'participationCount': int(row['participation_count']),
                    'currentClass': row['current_class'],
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }, merge=True)
                updated_count += 1
            except Exception as e:
                errors.append({
                    'row': row,
                    'error': str(e)
                })

            if updated_count % 500 == 0:  # バッチサイズの制限
                await batch.commit()
                batch = self.db.batch()

        if updated_count % 500 != 0:
            await batch.commit()

        return {
            'updated_count': updated_count,
            'errors': errors
        }
```

## 4. エラーハンドリング

### 4.1 例外ハンドラー
```python
# backend/app/core/errors.py
from fastapi import Request
from fastapi.responses import JSONResponse
from firebase_admin.exceptions import FirebaseError

async def firebase_error_handler(
    request: Request,
    exc: FirebaseError
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "message": "データベースエラーが発生しました",
            "detail": str(exc)
        }
    )

# エラーハンドラーの登録
app.add_exception_handler(FirebaseError, firebase_error_handler)
```

### 4.2 カスタム例外
```python
# backend/app/core/exceptions.py
class TeamError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# 使用例
if team.member_count >= 8:
    raise TeamError("チームメンバーが上限に達しています", 400)
``` 