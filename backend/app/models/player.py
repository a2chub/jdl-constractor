"""
プレイヤー関連のデータモデルを定義するモジュール

このモジュールでは、プレイヤーの作成、更新、レスポンスに関するPydanticモデルを定義します。
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class PlayerBase(BaseModel):
    """
    プレイヤーの基本情報を定義するベースモデル
    """
    name: str = Field(..., min_length=1, max_length=50, description="プレイヤー名")
    jdl_id: str = Field(..., description="JDL ID")
    team_id: Optional[str] = Field(None, description="所属チームID")

class PlayerCreate(PlayerBase):
    """
    プレイヤー作成時のリクエストモデル
    """
    user_id: str = Field(..., description="ユーザーID")

    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        """プレイヤー名に特殊文字が含まれていないことを確認"""
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_一-龠ぁ-んァ-ン]+$', v):
            raise ValueError('プレイヤー名に使用できない文字が含まれています')
        return v

    @validator('jdl_id')
    def validate_jdl_id_format(cls, v):
        """JDL IDのフォーマットを検証"""
        import re
        if not re.match(r'^JDL\d{6}$', v):
            raise ValueError('JDL IDの形式が正しくありません（例: JDL123456）')
        return v

class PlayerUpdate(BaseModel):
    """
    プレイヤー更新時のリクエストモデル
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    team_id: Optional[str] = Field(None)

class PlayerResponse(PlayerBase):
    """
    プレイヤー情報のレスポンスモデル
    """
    id: str = Field(..., description="プレイヤーID")
    user_id: str = Field(..., description="ユーザーID")
    participation_count: int = Field(..., ge=0, description="JDL参加回数")
    current_class: str = Field(..., description="現在のクラス")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    status: str = Field(..., description="プレイヤーのステータス")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PlayerTransfer(BaseModel):
    """
    プレイヤーの移籍情報モデル
    """
    player_id: str = Field(..., description="プレイヤーID")
    from_team_id: Optional[str] = Field(None, description="移籍元チームID")
    to_team_id: Optional[str] = Field(None, description="移籍先チームID")
    transfer_date: datetime = Field(..., description="移籍日時")
    reason: Optional[str] = Field(None, max_length=200, description="移籍理由")
