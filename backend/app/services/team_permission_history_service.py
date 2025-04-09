"""
チーム権限の変更履歴を管理するサービス

このモジュールでは、チーム権限の変更履歴を記録・取得するための
サービス機能を提供します。
"""

from datetime import datetime
from typing import Optional
from google.cloud import firestore
from ..models.team_permission_history import (
    TeamPermissionHistoryCreate,
    TeamPermissionHistoryResponse,
    TeamPermissionHistoryList
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TeamPermissionHistoryService:
    """チーム権限の変更履歴を管理するサービスクラス"""

    def __init__(self, db: firestore.Client):
        """
        初期化

        Args:
            db (firestore.Client): Firestoreクライアント
        """
        self.db = db
        self.collection = db.collection('team_permission_histories')

    async def create_history(
        self,
        history: TeamPermissionHistoryCreate,
    ) -> TeamPermissionHistoryResponse:
        """
        権限変更履歴を作成する

        Args:
            history (TeamPermissionHistoryCreate): 作成する履歴情報

        Returns:
            TeamPermissionHistoryResponse: 作成された履歴情報

        Raises:
            Exception: 履歴の作成に失敗した場合
        """
        try:
            history_dict = history.dict()
            doc_ref = self.collection.document()
            doc_ref.set(history_dict)

            response_dict = history_dict.copy()
            response_dict['id'] = doc_ref.id

            return TeamPermissionHistoryResponse(**response_dict)

        except Exception as e:
            logger.error(f"権限変更履歴の作成に失敗しました: {str(e)}")
            raise

    async def get_histories(
        self,
        team_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> TeamPermissionHistoryList:
        """
        権限変更履歴を取得する

        Args:
            team_id (Optional[str]): チームIDでフィルタリング
            user_id (Optional[str]): ユーザーIDでフィルタリング
            limit (int): 取得件数
            offset (int): オフセット

        Returns:
            TeamPermissionHistoryList: 履歴一覧

        Raises:
            Exception: 履歴の取得に失敗した場合
        """
        try:
            query = self.collection.order_by('changed_at', direction=firestore.Query.DESCENDING)

            if team_id:
                query = query.where('team_id', '==', team_id)
            if user_id:
                query = query.where('user_id', '==', user_id)

            # 総件数の取得
            total_query = query.count()
            total = total_query.get()[0][0]

            # データの取得
            docs = query.offset(offset).limit(limit).stream()

            items = []
            for doc in docs:
                history_dict = doc.to_dict()
                history_dict['id'] = doc.id
                items.append(TeamPermissionHistoryResponse(**history_dict))

            return TeamPermissionHistoryList(items=items, total=total)

        except Exception as e:
            logger.error(f"権限変更履歴の取得に失敗しました: {str(e)}")
            raise

    async def get_history(self, history_id: str) -> TeamPermissionHistoryResponse:
        """
        指定されたIDの権限変更履歴を取得する

        Args:
            history_id (str): 履歴ID

        Returns:
            TeamPermissionHistoryResponse: 履歴情報

        Raises:
            Exception: 履歴の取得に失敗した場合
        """
        try:
            doc = self.collection.document(history_id).get()
            if not doc.exists:
                raise ValueError("指定された履歴が見つかりません")

            history_dict = doc.to_dict()
            history_dict['id'] = doc.id

            return TeamPermissionHistoryResponse(**history_dict)

        except Exception as e:
            logger.error(f"権限変更履歴の取得に失敗しました: {str(e)}")
            raise 