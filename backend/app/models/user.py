# backend/app/models/user.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """ユーザーの基本情報"""
    email: EmailStr = Field(..., description="メールアドレス")
    name: Optional[str] = Field(None, max_length=50, description="ユーザー名")
    is_admin: bool = Field(False, description="管理者フラグ")
    is_locked: bool = Field(False, description="アカウントロック状態") # is_locked を追加

class UserCreate(UserBase):
    """ユーザー作成用 (通常はFirebase Auth側で作成される)"""
    # Firebase Auth UID を ID として使うことが多い
    id: Optional[str] = Field(None, description="Firebase Auth UID")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

class UserUpdate(BaseModel):
    """ユーザー情報更新用 (管理者による更新など)"""
    name: Optional[str] = Field(None, max_length=50)
    is_admin: Optional[bool] = None
    is_locked: Optional[bool] = None # is_locked を更新可能に
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

class UserResponse(UserBase):
    """ユーザー情報レスポンス用"""
    id: str = Field(..., description="ユーザーID (ドキュメントID)")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
