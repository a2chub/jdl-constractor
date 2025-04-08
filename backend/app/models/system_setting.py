# backend/app/models/system_setting.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional
from datetime import datetime

class SystemSettingBase(BaseModel):
    """システム設定の基本モデル"""
    # FirestoreではドキュメントIDをキーとして使うことが多いので、
    # モデル自体に key を含めるかは設計による。
    # ここでは value と description を持つモデルとする。
    # key はAPIパスやドキュメントIDで指定する想定。
    value: Any = Field(..., description="設定値 (型は任意)")
    description: Optional[str] = Field(None, description="設定の説明")

class SystemSettingCreate(SystemSettingBase):
    """
    システム設定作成用モデル。
    キーも指定して作成する場合に使用。
    """
    key: str = Field(..., description="設定キー (一意)", examples=["default_entry_fee", "admin_notification_email"])
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)


class SystemSettingUpdate(BaseModel):
    """システム設定更新用モデル"""
    # 更新時は value や description を部分的に指定可能にする
    value: Optional[Any] = Field(None, description="新しい設定値")
    description: Optional[str] = Field(None, description="設定の説明（更新する場合）")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

class SystemSettingResponse(SystemSettingBase):
    """システム設定レスポンス用モデル"""
    key: str = Field(..., description="設定キー") # レスポンスにはキーを含める
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Pydantic V2 compatibility
    model_config = ConfigDict(
        from_attributes=True, # orm_mode is deprecated
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

# 例: 設定キーのEnum (任意)
# from enum import Enum
# class SettingKeys(str, Enum):
#     DEFAULT_ENTRY_FEE = "default_entry_fee"
#     ADMIN_EMAIL = "admin_notification_email"
#     MAX_TEAM_MEMBERS = "max_team_members"
