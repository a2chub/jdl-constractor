"""
チーム関連のデータモデルを定義するモジュール

このモジュールでは、チームの作成、更新、レスポンスに関するPydanticモデルを定義します。
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class TeamBase(BaseModel):
    """
    チームの基本情報を定義するベースモデル
    """
    name: str = Field(..., min_length=1, max_length=50, description="チーム名")
    description: Optional[str] = Field(None, max_length=200, description="チーム説明")
    logo_url: Optional[str] = Field(None, description="チームロゴのURL")

class TeamCreate(TeamBase):
    """
    チーム作成時のリクエストモデル
    """
    manager_id: str = Field(..., description="チーム代表のユーザーID")

    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        """チーム名に特殊文字が含まれていないことを確認"""
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_一-龠ぁ-んァ-ン]+$', v):
            raise ValueError('チーム名に使用できない文字が含まれています')
        return v

class TeamUpdate(TeamBase):
    """
    チーム更新時のリクエストモデル
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    manager_id: Optional[str] = Field(None, description="チーム代表のユーザーID")

class TeamMember(BaseModel):
    """
    チームメンバー情報のモデル
    """
    user_id: str = Field(..., description="メンバーのユーザーID")
    name: str = Field(..., description="メンバー名")
    jdl_id: str = Field(..., description="JDL ID")
    joined_at: datetime = Field(..., description="加入日時")
    participation_count: int = Field(..., ge=0, description="JDL参加回数")

class TeamResponse(TeamBase):
    """
    チーム情報のレスポンスモデル
    """
    id: str = Field(..., description="チームID")
    manager_id: str = Field(..., description="チーム代表のユーザーID")
    members: List[TeamMember] = Field(default_factory=list, description="チームメンバー一覧")
    member_count: int = Field(..., ge=0, le=8, description="メンバー数")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    status: str = Field(..., description="チームのステータス")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
