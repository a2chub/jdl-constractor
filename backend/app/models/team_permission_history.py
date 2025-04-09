"""
チーム権限の変更履歴を管理するモデル

このモジュールでは、チーム権限の変更履歴を記録・管理するための
データモデルを定義します。
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TeamPermissionHistory(BaseModel):
    """チーム権限の変更履歴を表すモデル"""
    team_id: str = Field(..., description="チームID")
    user_id: str = Field(..., description="ユーザーID")
    role: str = Field(..., description="権限（manager, member）")
    action: str = Field(..., description="変更内容（add, remove, update）")
    changed_by: str = Field(..., description="変更を行ったユーザーID")
    changed_at: datetime = Field(default_factory=datetime.utcnow, description="変更日時")
    reason: Optional[str] = Field(None, description="変更理由")

class TeamPermissionHistoryCreate(TeamPermissionHistory):
    """チーム権限変更履歴作成リクエスト用のモデル"""
    pass

class TeamPermissionHistoryResponse(TeamPermissionHistory):
    """チーム権限変更履歴レスポンス用のモデル"""
    id: str = Field(..., description="履歴ID")

    class Config:
        """モデルの設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TeamPermissionHistoryList(BaseModel):
    """チーム権限変更履歴一覧レスポンス用のモデル"""
    items: list[TeamPermissionHistoryResponse]
    total: int 