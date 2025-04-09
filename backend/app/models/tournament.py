"""
トーナメント管理に関するPydanticモデルを定義するモジュール

このモジュールでは、トーナメントの作成、更新、レスポンスに関する
データモデルを定義します。各モデルはFirestoreとの連携を考慮して
設計されています。
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class TournamentStatus(str, Enum):
    """トーナメントの状態を表す列挙型"""
    DRAFT = "draft"  # 下書き
    ENTRY_OPEN = "entry_open"  # エントリー受付中
    ENTRY_CLOSED = "entry_closed"  # エントリー締切
    IN_PROGRESS = "in_progress"  # 開催中
    COMPLETED = "completed"  # 終了
    CANCELLED = "cancelled"  # キャンセル

class ClassRestriction(BaseModel):
    """クラス制限を表すモデル"""
    class_name: str = Field(..., description="クラス名")
    min_participation: int = Field(0, description="最小参加回数", ge=0)
    max_participation: Optional[int] = Field(None, description="最大参加回数", ge=0)

    @validator('class_name')
    def validate_class_name(cls, v):
        """クラス名の検証"""
        valid_classes = ['A', 'B', 'C', 'D', 'E']
        if v not in valid_classes:
            raise ValueError('クラスはA, B, C, D, Eのいずれかである必要があります')
        return v

class EntryRestriction(BaseModel):
    """エントリー制限を表すモデル"""
    max_players: int = Field(..., description="最大参加人数", gt=0)
    min_players_per_team: int = Field(1, description="チームあたりの最小参加人数", ge=1)
    max_players_per_team: int = Field(..., description="チームあたりの最大参加人数", gt=0)
    class_restrictions: List[ClassRestriction] = Field(
        default_factory=list,
        description="クラスごとの制限"
    )

    @validator('max_players_per_team')
    def validate_max_players_per_team(cls, v, values):
        """チームあたりの最大参加人数の検証"""
        if 'min_players_per_team' in values and v < values['min_players_per_team']:
            raise ValueError('最大参加人数は最小参加人数以上である必要があります')
        return v

class TournamentBase(BaseModel):
    """トーナメントの基本情報を定義するベースモデル"""
    name: str = Field(..., description="トーナメント名")
    description: str = Field(..., description="トーナメントの説明")
    start_date: datetime = Field(..., description="開始日時")
    end_date: datetime = Field(..., description="終了日時")
    entry_start_date: datetime = Field(..., description="エントリー開始日時")
    entry_end_date: datetime = Field(..., description="エントリー終了日時")
    venue: str = Field(..., description="開催場所")
    entry_fee: int = Field(0, description="参加費", ge=0)
    status: TournamentStatus = Field(TournamentStatus.DRAFT, description="トーナメントの状態")
    entry_restriction: EntryRestriction = Field(..., description="エントリー制限")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """終了日時の検証"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('終了日時は開始日時より後である必要があります')
        return v

    @validator('entry_end_date')
    def validate_entry_end_date(cls, v, values):
        """エントリー終了日時の検証"""
        if 'entry_start_date' in values and v <= values['entry_start_date']:
            raise ValueError('エントリー終了日時はエントリー開始日時より後である必要があります')
        if 'start_date' in values and v >= values['start_date']:
            raise ValueError('エントリー終了日時は開始日時より前である必要があります')
        return v

class TournamentCreate(TournamentBase):
    """トーナメント作成リクエスト用のモデル"""
    pass

class TournamentUpdate(BaseModel):
    """トーナメント更新リクエスト用のモデル"""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    entry_start_date: Optional[datetime] = None
    entry_end_date: Optional[datetime] = None
    venue: Optional[str] = None
    entry_fee: Optional[int] = Field(None, ge=0)
    status: Optional[TournamentStatus] = None
    entry_restriction: Optional[EntryRestriction] = None

class Entry(BaseModel):
    """トーナメントエントリーを表すモデル"""
    player_id: str = Field(..., description="プレイヤーID")
    team_id: str = Field(..., description="チームID")
    entry_date: datetime = Field(..., description="エントリー日時")
    status: str = Field("pending", description="エントリーの状態")

class TournamentResponse(TournamentBase):
    """トーナメント情報レスポンス用のモデル"""
    id: str = Field(..., description="トーナメントID")
    entries: List[Entry] = Field(default_factory=list, description="エントリー一覧")
    current_entries: int = Field(0, description="現在のエントリー数")
    created_at: datetime
    updated_at: datetime

    class Config:
        """モデルの設定"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TournamentList(BaseModel):
    """トーナメント一覧レスポンス用のモデル"""
    items: List[TournamentResponse]
    total: int
