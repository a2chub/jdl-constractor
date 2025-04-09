"""
クラス変更に関するルーターを定義するモジュール

このモジュールでは、クラス変更リクエスト、承認、履歴の取得などの
エンドポイントを定義します。
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import firestore
from datetime import datetime

from ..models.class_change import (
    ClassChangeRequest,
    ClassChangeApproval,
    ClassChangeHistory
)
from ..dependencies import get_current_user, get_db
from ..utils.logger import get_logger
from ..utils.notifications import send_notification

router = APIRouter(
    prefix="/class-changes",
    tags=["class-changes"],
    responses={404: {"description": "クラス変更履歴が見つかりません"}},
)

logger = get_logger(__name__)

@router.post(
    "/request",
    response_model=ClassChangeHistory,
    status_code=201,
    summary="クラス変更をリクエストする",
    description="新しいクラス変更をリクエストします。チーム管理者のみが実行できます。"
)
async def request_class_change(
    request: ClassChangeRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> ClassChangeHistory:
    """クラス変更をリクエストする

    Args:
        request (ClassChangeRequest): クラス変更リクエスト情報
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        ClassChangeHistory: 作成されたクラス変更履歴

    Raises:
        HTTPException: クラス変更リクエストに失敗した場合
    """
    try:
        # プレイヤーの存在確認と現在のクラス取得
        player_ref = db.collection('players').document(request.player_id)
        player = player_ref.get()
        if not player.exists:
            raise HTTPException(status_code=404, detail="プレイヤーが見つかりません")
        
        player_data = player.to_dict()
        
        # チーム管理者権限の確認
        if player_data.get('team_id'):
            team_ref = db.collection('teams').document(player_data['team_id'])
            team = team_ref.get()
            if not team.exists or team.to_dict()['manager_id'] != current_user['uid']:
                raise HTTPException(status_code=403, detail="チーム管理者のみがクラス変更をリクエストできます")

        now = datetime.utcnow()
        history_ref = db.collection('class_change_history').document()
        history_data = {
            'id': history_ref.id,
            'player_id': request.player_id,
            'old_class': player_data['current_class'],
            'new_class': request.new_class,
            'reason': request.reason,
            'requested_by': current_user['uid'],
            'requested_at': now,
            'status': 'pending',
            'approved_by': None,
            'approved_at': None,
            'comment': None
        }

        history_ref.set(history_data)
        
        # 管理者に通知を送信
        await send_notification(
            'admin',
            'クラス変更リクエストが提出されました',
            f'プレイヤー {player_data["name"]} のクラス変更リクエストが提出されました'
        )

        return ClassChangeHistory(**history_data)

    except Exception as e:
        logger.error(f"クラス変更リクエストに失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="クラス変更リクエストに失敗しました")

@router.post(
    "/{history_id}/approve",
    response_model=ClassChangeHistory,
    summary="クラス変更を承認/却下する",
    description="クラス変更リクエストを承認または却下します。管理者のみが実行できます。"
)
async def approve_class_change(
    history_id: str,
    approval: ClassChangeApproval,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> ClassChangeHistory:
    """クラス変更を承認/却下する

    Args:
        history_id (str): クラス変更履歴ID
        approval (ClassChangeApproval): 承認情報
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        ClassChangeHistory: 更新されたクラス変更履歴

    Raises:
        HTTPException: 承認/却下に失敗した場合
    """
    try:
        # 管理者権限の確認
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="管理者のみがクラス変更を承認できます")

        # クラス変更履歴の取得
        history_ref = db.collection('class_change_history').document(history_id)
        history = history_ref.get()
        if not history.exists:
            raise HTTPException(status_code=404, detail="クラス変更履歴が見つかりません")

        history_data = history.to_dict()
        if history_data['status'] != 'pending':
            raise HTTPException(status_code=400, detail="このリクエストは既に処理済みです")

        now = datetime.utcnow()
        update_data = {
            'status': 'approved' if approval.approved else 'rejected',
            'approved_by': current_user['uid'],
            'approved_at': now,
            'comment': approval.comment
        }

        # トランザクションで更新
        transaction = db.transaction()
        @firestore.transactional
        def update_in_transaction(transaction, history_ref, player_ref):
            if approval.approved:
                # プレイヤーのクラスを更新
                player = player_ref.get(transaction=transaction)
                if not player.exists:
                    raise HTTPException(status_code=404, detail="プレイヤーが見つかりません")
                
                transaction.update(player_ref, {
                    'current_class': history_data['new_class'],
                    'updated_at': now
                })
            
            # 履歴を更新
            transaction.update(history_ref, update_data)

        # プレイヤーの参照を取得
        player_ref = db.collection('players').document(history_data['player_id'])
        update_in_transaction(transaction, history_ref, player_ref)

        # 申請者に通知を送信
        status_text = "承認" if approval.approved else "却下"
        await send_notification(
            history_data['requested_by'],
            f'クラス変更リクエストが{status_text}されました',
            f'プレイヤーID {history_data["player_id"]} のクラス変更リクエストが{status_text}されました'
        )

        history_data.update(update_data)
        return ClassChangeHistory(**history_data)

    except Exception as e:
        logger.error(f"クラス変更の承認/却下に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="クラス変更の承認/却下に失敗しました")

@router.get(
    "/history/{player_id}",
    response_model=List[ClassChangeHistory],
    summary="プレイヤーのクラス変更履歴を取得する",
    description="指定されたプレイヤーのクラス変更履歴を取得します。"
)
async def get_class_change_history(
    player_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)],
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
) -> List[ClassChangeHistory]:
    """プレイヤーのクラス変更履歴を取得する

    Args:
        player_id (str): プレイヤーID
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント
        limit (int): 取得する履歴の最大数
        offset (int): スキップする履歴の数

    Returns:
        List[ClassChangeHistory]: クラス変更履歴のリスト

    Raises:
        HTTPException: 履歴の取得に失敗した場合
    """
    try:
        history_ref = (
            db.collection('class_change_history')
            .where('player_id', '==', player_id)
            .order_by('requested_at', direction=firestore.Query.DESCENDING)
            .offset(offset)
            .limit(limit)
        )

        history_docs = history_ref.stream()
        return [ClassChangeHistory(**doc.to_dict()) for doc in history_docs]

    except Exception as e:
        logger.error(f"クラス変更履歴の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="クラス変更履歴の取得に失敗しました")

@router.get("/")
async def get_class_changes():
    return {"message": "Class change router is working"} 