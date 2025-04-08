"""
クラス変更に関するPydanticモデルを定義するモジュール

このモジュールでは、クラス変更リクエスト、承認、履歴に関する
データモデルを定義します。
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class ClassChangeRequest(BaseModel):
    """クラス変更リクエストモデル"""
    player_id: str = Field(..., description="プレイヤーID")
    new_class: str = Field(..., description="変更後のクラス")
    reason: str = Field(..., description="変更理由", max_length=200)

    @validator('new_class')
    def validate_class(cls, v):
        """クラスの値を検証"""
        valid_classes = ['A', 'B', 'C', 'D', 'E']
        if v not in valid_classes:
            raise ValueError('クラスはA, B, C, D, Eのいずれかである必要があります')
        return v

class ClassChangeApproval(BaseModel):
    """クラス変更承認モデル"""
    approved: bool = Field(..., description="承認状態")
    comment: Optional[str] = Field(None, description="承認/却下コメント", max_length=200)

class ClassChangeHistory(BaseModel):
    """クラス変更履歴モデル"""
    id: str = Field(..., description="変更履歴ID")
    player_id: str = Field(..., description="プレイヤーID")
    old_class: str = Field(..., description="変更前のクラス")
    new_class: str = Field(..., description="変更後のクラス")
    reason: str = Field(..., description="変更理由")
    requested_by: str = Field(..., description="申請者ID")
    requested_at: datetime = Field(..., description="申請日時")
    status: str = Field(..., description="ステータス")
    approved_by: Optional[str] = Field(None, description="承認者ID")
    approved_at: Optional[datetime] = Field(None, description="承認日時")
    comment: Optional[str] = Field(None, description="承認/却下コメント")

    class Config:
        """モデルの設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 