"""
プレイヤー管理に関するルーターを定義するモジュール

このモジュールでは、プレイヤーの作成、更新、取得、一覧表示などの
エンドポイントを定義します。各エンドポイントは認証が必要で、
適切な権限を持つユーザーのみがアクセスできます。
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import firestore
from datetime import datetime

from ..models.player import (
    PlayerCreate,
    PlayerUpdate,
    PlayerResponse,
    PlayerList,
    ClassHistory
)
from ..dependencies import get_current_user, get_db
from ..utils.logger import get_logger

router = APIRouter(
    prefix="/players",
    tags=["players"],
    responses={404: {"description": "プレイヤーが見つかりません"}},
)

logger = get_logger(__name__)

@router.post(
    "",
    response_model=PlayerResponse,
    status_code=201,
    summary="プレイヤーを作成する",
    description="新しいプレイヤーを作成します。チーム管理者のみが実行できます。"
)
async def create_player(
    player: PlayerCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> PlayerResponse:
    """プレイヤーを作成する

    Args:
        player (PlayerCreate): 作成するプレイヤーの情報
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        PlayerResponse: 作成されたプレイヤーの情報

    Raises:
        HTTPException: プレイヤーの作成に失敗した場合
    """
    try:
        # チーム管理者権限の確認
        if player.team_id:
            team_ref = db.collection('teams').document(player.team_id)
            team = team_ref.get()
            if not team.exists:
                raise HTTPException(status_code=404, detail="指定されたチームが見つかりません")
            if team.to_dict()['manager_id'] != current_user['uid']:
                raise HTTPException(status_code=403, detail="チーム管理者のみがプレイヤーを作成できます")

        # JDL IDの重複チェック
        players_ref = db.collection('players')
        existing_player = players_ref.where('jdl_id', '==', player.jdl_id).limit(1).get()
        if len(list(existing_player)) > 0:
            raise HTTPException(status_code=400, detail="指定されたJDL IDは既に使用されています")

        now = datetime.utcnow()
        player_dict = player.dict()
        player_dict.update({
            'created_at': now,
            'updated_at': now,
        })

        # プレイヤーの作成
        doc_ref = players_ref.document()
        doc_ref.set(player_dict)

        # レスポンスの作成
        response_dict = player_dict.copy()
        response_dict['id'] = doc_ref.id
        if player.team_id:
            response_dict['team_name'] = team.to_dict().get('name')
        
        return PlayerResponse(**response_dict)

    except Exception as e:
        logger.error(f"プレイヤーの作成に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="プレイヤーの作成に失敗しました")

@router.get(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="プレイヤー情報を取得する",
    description="指定されたIDのプレイヤー情報を取得します。"
)
async def get_player(
    player_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> PlayerResponse:
    """プレイヤー情報を取得する

    Args:
        player_id (str): プレイヤーID
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        PlayerResponse: プレイヤー情報

    Raises:
        HTTPException: プレイヤーが見つからない場合
    """
    try:
        doc_ref = db.collection('players').document(player_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="プレイヤーが見つかりません")

        player_dict = doc.to_dict()
        player_dict['id'] = doc.id

        # チーム名の取得
        if player_dict.get('team_id'):
            team_ref = db.collection('teams').document(player_dict['team_id'])
            team = team_ref.get()
            if team.exists:
                player_dict['team_name'] = team.to_dict().get('name')

        return PlayerResponse(**player_dict)

    except Exception as e:
        logger.error(f"プレイヤー情報の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="プレイヤー情報の取得に失敗しました")

@router.put(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="プレイヤー情報を更新する",
    description="指定されたIDのプレイヤー情報を更新します。チーム管理者のみが実行できます。"
)
async def update_player(
    player_id: str,
    player: PlayerUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> PlayerResponse:
    """プレイヤー情報を更新する

    Args:
        player_id (str): プレイヤーID
        player (PlayerUpdate): 更新するプレイヤーの情報
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        PlayerResponse: 更新されたプレイヤーの情報

    Raises:
        HTTPException: プレイヤーの更新に失敗した場合
    """
    try:
        doc_ref = db.collection('players').document(player_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="プレイヤーが見つかりません")

        current_data = doc.to_dict()

        # チーム管理者権限の確認
        if current_data.get('team_id'):
            team_ref = db.collection('teams').document(current_data['team_id'])
            team = team_ref.get()
            if team.exists and team.to_dict()['manager_id'] != current_user['uid']:
                raise HTTPException(status_code=403, detail="チーム管理者のみがプレイヤー情報を更新できます")

        # 更新データの準備
        update_data = player.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()

        # クラス変更の履歴を記録
        if 'current_class' in update_data and update_data['current_class'] != current_data['current_class']:
            class_history = ClassHistory(
                old_class=current_data['current_class'],
                new_class=update_data['current_class'],
                changed_at=update_data['updated_at'],
                reason="Manual update",
                approved_by=current_user['uid']
            )
            if 'class_history' not in current_data:
                current_data['class_history'] = []
            current_data['class_history'].append(class_history.dict())
            update_data['class_history'] = current_data['class_history']

        # プレイヤー情報の更新
        doc_ref.update(update_data)

        # 更新後のデータを取得
        updated_doc = doc_ref.get()
        updated_dict = updated_doc.to_dict()
        updated_dict['id'] = doc.id

        # チーム名の取得
        if updated_dict.get('team_id'):
            team_ref = db.collection('teams').document(updated_dict['team_id'])
            team = team_ref.get()
            if team.exists:
                updated_dict['team_name'] = team.to_dict().get('name')

        return PlayerResponse(**updated_dict)

    except Exception as e:
        logger.error(f"プレイヤー情報の更新に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="プレイヤー情報の更新に失敗しました")

@router.get(
    "",
    response_model=PlayerList,
    summary="プレイヤー一覧を取得する",
    description="プレイヤーの一覧を取得します。チームIDによるフィルタリングが可能です。"
)
async def list_players(
    team_id: Annotated[str | None, Query(description="チームIDでフィルタリング")] = None,
    limit: Annotated[int, Query(gt=0, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> PlayerList:
    """プレイヤー一覧を取得する

    Args:
        team_id (str | None): フィルタリングするチームID
        limit (int): 取得件数 (1-100)
        offset (int): オフセット (0以上)
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        PlayerList: プレイヤー一覧

    Raises:
        HTTPException: プレイヤー一覧の取得に失敗した場合
    """
    try:
        query = db.collection('players')
        if team_id:
            query = query.where('team_id', '==', team_id)

        # 総件数の取得
        total_query = query.count()
        total = total_query.get()[0][0]

        # データの取得
        docs = query.offset(offset).limit(limit).stream()
        
        items = []
        for doc in docs:
            player_dict = doc.to_dict()
            player_dict['id'] = doc.id

            # チーム名の取得
            if player_dict.get('team_id'):
                team_ref = db.collection('teams').document(player_dict['team_id'])
                team = team_ref.get()
                if team.exists:
                    player_dict['team_name'] = team.to_dict().get('name')

            items.append(PlayerResponse(**player_dict))

        return PlayerList(items=items, total=total)

    except Exception as e:
        logger.error(f"プレイヤー一覧の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="プレイヤー一覧の取得に失敗しました")

@router.get("/")
async def get_players():
    return {"message": "Player router is working"} 