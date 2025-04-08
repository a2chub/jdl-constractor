"""
プレイヤー管理に関するPydanticモデルを定義するモジュール

このモジュールでは、プレイヤーの作成、更新、レスポンスに関する
データモデルを定義します。各モデルはFirestoreとの連携を考慮して
設計されています。
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import re

class PlayerBase(BaseModel):
    """プレイヤーの基本情報を定義するベースモデル"""
    name: str = Field(..., description="プレイヤー名")
    jdl_id: str = Field(..., description="JDL ID")
    team_id: Optional[str] = Field(None, description="所属チームID")
    participation_count: int = Field(0, description="大会参加回数", ge=0)
    current_class: str = Field(..., description="現在のクラス")

    @validator('jdl_id')
    def validate_jdl_id(cls, v):
        """JDL IDの形式を検証"""
        if not re.match(r'^JDL\d{6}$', v):
            raise ValueError('JDL IDは"JDL"で始まる6桁の数字である必要があります')
        return v

    @validator('current_class')
    def validate_class(cls, v):
        """クラスの値を検証"""
        valid_classes = ['A', 'B', 'C', 'D', 'E']
        if v not in valid_classes:
            raise ValueError('クラスはA, B, C, D, Eのいずれかである必要があります')
        return v

class PlayerCreate(PlayerBase):
    """プレイヤー作成リクエスト用のモデル"""
    pass

class PlayerUpdate(BaseModel):
    """プレイヤー更新リクエスト用のモデル"""
    name: Optional[str] = None
    team_id: Optional[str] = None
    participation_count: Optional[int] = Field(None, ge=0)
    current_class: Optional[str] = None

    @validator('current_class')
    def validate_class(cls, v):
        """クラスの値を検証"""
        if v is not None:
            valid_classes = ['A', 'B', 'C', 'D', 'E']
            if v not in valid_classes:
                raise ValueError('クラスはA, B, C, D, Eのいずれかである必要があります')
        return v

class ClassHistory(BaseModel):
    """クラス変更履歴を表すモデル"""
    old_class: str
    new_class: str
    changed_at: datetime
    reason: str
    approved_by: Optional[str] = None

class PlayerResponse(PlayerBase):
    """プレイヤー情報レスポンス用のモデル"""
    id: str = Field(..., description="プレイヤーID")
    team_name: Optional[str] = Field(None, description="所属チーム名")
    class_history: List[ClassHistory] = Field(default_factory=list, description="クラス変更履歴")
    created_at: datetime
    updated_at: datetime

    class Config:
        """モデルの設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PlayerList(BaseModel):
    """プレイヤー一覧レスポンス用のモデル"""
    items: List[PlayerResponse]
    total: int

class PlayerTransfer(BaseModel):
    """
    プレイヤーの移籍情報モデル
    """
    player_id: str = Field(..., description="プレイヤーID")
    from_team_id: Optional[str] = Field(None, description="移籍元チームID")
    to_team_id: Optional[str] = Field(None, description="移籍先チームID")
    transfer_date: datetime = Field(..., description="移籍日時")
    reason: Optional[str] = Field(None, max_length=200, description="移籍理由")
