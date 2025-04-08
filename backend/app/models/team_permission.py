"""
チーム権限管理のモデルを定義するモジュール

このモジュールでは、チームの権限管理に関連するPydanticモデルを定義します。
権限の作成、更新、レスポンスに使用されるモデルが含まれます。
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, validator

class TeamRole(str, Enum):
    """チームにおける役割を定義する列挙型"""
    OWNER = "owner"  # チームオーナー：全ての権限を持つ
    MANAGER = "manager"  # チーム管理者：メンバー管理、情報更新が可能
    MEMBER = "member"  # 一般メンバー：閲覧のみ可能

class TeamPermissionBase(BaseModel):
    """チーム権限の基本モデル"""
    user_id: str = Field(..., description="ユーザーID")
    team_id: str = Field(..., description="チームID")
    role: TeamRole = Field(..., description="チームでの役割")

    @validator("user_id")
    def validate_user_id(cls, v: str) -> str:
        """ユーザーIDのバリデーション"""
        if not v.strip():
            raise ValueError("ユーザーIDは必須です")
        return v

    @validator("team_id")
    def validate_team_id(cls, v: str) -> str:
        """チームIDのバリデーション"""
        if not v.strip():
            raise ValueError("チームIDは必須です")
        return v

class TeamPermissionCreate(TeamPermissionBase):
    """チーム権限作成リクエストモデル"""
    pass

class TeamPermissionUpdate(BaseModel):
    """チーム権限更新リクエストモデル"""
    role: TeamRole = Field(..., description="更新後の役割")

class TeamPermissionResponse(TeamPermissionBase):
    """チーム権限レスポンスモデル"""
    id: str = Field(..., description="権限ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    class Config:
        """モデルの設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TeamPermissionList(BaseModel):
    """チーム権限一覧レスポンスモデル"""
    permissions: List[TeamPermissionResponse] = Field(..., description="権限一覧")
    total: int = Field(..., description="総件数") 