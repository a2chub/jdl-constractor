"""
チーム権限管理のサービスを定義するモジュール

このモジュールでは、チームの権限管理に関連するビジネスロジックを実装します。
権限の作成、更新、取得、削除などの操作を提供します。
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models.team_permission import (
    TeamPermissionCreate,
    TeamPermissionUpdate,
    TeamPermissionResponse,
    TeamPermissionList,
    TeamRole
)
from app.core.errors import NotFoundException, ValidationError

class TeamPermissionService:
    """チーム権限管理サービス"""

    def __init__(self, db: firestore.Client):
        """
        初期化

        Args:
            db (firestore.Client): Firestoreクライアント
        """
        self.db = db
        self.collection = db.collection('team_permissions')

    async def create_permission(self, permission: TeamPermissionCreate) -> TeamPermissionResponse:
        """
        チーム権限を作成する

        Args:
            permission (TeamPermissionCreate): 作成する権限情報

        Returns:
            TeamPermissionResponse: 作成された権限情報

        Raises:
            ValidationError: 既に同じユーザーが同じチームの権限を持っている場合
        """
        # 既存の権限をチェック
        existing = self.collection.where(
            filter=FieldFilter("user_id", "==", permission.user_id)
        ).where(
            filter=FieldFilter("team_id", "==", permission.team_id)
        ).get()

        if len(existing) > 0:
            raise ValidationError("指定されたユーザーは既にこのチームの権限を持っています")

        now = datetime.utcnow()
        permission_id = str(uuid4())
        permission_dict = {
            "id": permission_id,
            "user_id": permission.user_id,
            "team_id": permission.team_id,
            "role": permission.role,
            "created_at": now,
            "updated_at": now
        }

        # 権限を作成
        self.collection.document(permission_id).set(permission_dict)

        return TeamPermissionResponse(**permission_dict)

    async def update_permission(
        self,
        permission_id: str,
        update_data: TeamPermissionUpdate
    ) -> TeamPermissionResponse:
        """
        チーム権限を更新する

        Args:
            permission_id (str): 更新する権限のID
            update_data (TeamPermissionUpdate): 更新データ

        Returns:
            TeamPermissionResponse: 更新された権限情報

        Raises:
            NotFoundException: 指定された権限が存在しない場合
        """
        doc_ref = self.collection.document(permission_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise NotFoundException(f"権限が見つかりません: {permission_id}")

        # 権限を更新
        update_dict = {
            "role": update_data.role,
            "updated_at": datetime.utcnow()
        }
        doc_ref.update(update_dict)

        # 更新後のデータを取得
        updated_doc = doc_ref.get()
        return TeamPermissionResponse(**updated_doc.to_dict())

    async def get_permission(self, permission_id: str) -> TeamPermissionResponse:
        """
        チーム権限を取得する

        Args:
            permission_id (str): 取得する権限のID

        Returns:
            TeamPermissionResponse: 取得された権限情報

        Raises:
            NotFoundException: 指定された権限が存在しない場合
        """
        doc = self.collection.document(permission_id).get()

        if not doc.exists:
            raise NotFoundException(f"権限が見つかりません: {permission_id}")

        return TeamPermissionResponse(**doc.to_dict())

    async def list_team_permissions(
        self,
        team_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> TeamPermissionList:
        """
        チームの権限一覧を取得する

        Args:
            team_id (str): チームID
            limit (int, optional): 取得件数. デフォルトは10.
            offset (int, optional): オフセット. デフォルトは0.

        Returns:
            TeamPermissionList: 権限一覧
        """
        # 総件数を取得
        total_query = self.collection.where(
            filter=FieldFilter("team_id", "==", team_id)
        )
        total = len(total_query.get())

        # 権限一覧を取得
        permissions_query = (
            self.collection
            .where(filter=FieldFilter("team_id", "==", team_id))
            .order_by("created_at")
            .offset(offset)
            .limit(limit)
        )
        permissions = [
            TeamPermissionResponse(**doc.to_dict())
            for doc in permissions_query.get()
        ]

        return TeamPermissionList(permissions=permissions, total=total)

    async def delete_permission(self, permission_id: str) -> None:
        """
        チーム権限を削除する

        Args:
            permission_id (str): 削除する権限のID

        Raises:
            NotFoundException: 指定された権限が存在しない場合
        """
        doc_ref = self.collection.document(permission_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise NotFoundException(f"権限が見つかりません: {permission_id}")

        doc_ref.delete() 