"""
トーナメント管理に関するルーターを定義するモジュール

このモジュールでは、トーナメントの作成、更新、取得、一覧表示、
エントリー管理などのエンドポイントを定義します。各エンドポイントは
認証が必要で、適切な権限を持つユーザーのみがアクセスできます。
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import firestore
from datetime import datetime

from ..models.tournament import (
    TournamentCreate,
    TournamentUpdate,
    TournamentResponse,
    TournamentList,
    Entry,
    TournamentStatus
)
from ..dependencies import get_current_user, get_db, get_admin_user
from ..utils.logger import get_logger

router = APIRouter(
    prefix="/tournaments",
    tags=["tournaments"],
    responses={404: {"description": "トーナメントが見つかりません"}},
)

logger = get_logger(__name__)

@router.post(
    "",
    response_model=TournamentResponse,
    status_code=201,
    summary="トーナメントを作成する",
    description="新しいトーナメントを作成します。管理者のみが実行できます。"
)
async def create_tournament(
    tournament: TournamentCreate,
    current_user: Annotated[dict, Depends(get_admin_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> TournamentResponse:
    """トーナメントを作成する

    Args:
        tournament (TournamentCreate): 作成するトーナメントの情報
        current_user (dict): 現在のユーザー情報（管理者のみ）
        db (firestore.Client): Firestoreクライアント

    Returns:
        TournamentResponse: 作成されたトーナメントの情報

    Raises:
        HTTPException: トーナメントの作成に失敗した場合
    """
    try:
        now = datetime.utcnow()
        tournament_dict = tournament.dict()
        tournament_dict.update({
            'created_at': now,
            'updated_at': now,
            'current_entries': 0,
            'entries': []
        })

        # トーナメントの作成
        doc_ref = db.collection('tournaments').document()
        doc_ref.set(tournament_dict)

        # レスポンスの作成
        response_dict = tournament_dict.copy()
        response_dict['id'] = doc_ref.id
        
        return TournamentResponse(**response_dict)

    except Exception as e:
        logger.error(f"トーナメントの作成に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="トーナメントの作成に失敗しました")

@router.get(
    "/{tournament_id}",
    response_model=TournamentResponse,
    summary="トーナメント情報を取得する",
    description="指定されたIDのトーナメント情報を取得します。"
)
async def get_tournament(
    tournament_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> TournamentResponse:
    """トーナメント情報を取得する

    Args:
        tournament_id (str): トーナメントID
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        TournamentResponse: トーナメント情報

    Raises:
        HTTPException: トーナメントが見つからない場合
    """
    try:
        doc_ref = db.collection('tournaments').document(tournament_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="トーナメントが見つかりません")

        tournament_dict = doc.to_dict()
        tournament_dict['id'] = doc.id

        return TournamentResponse(**tournament_dict)

    except Exception as e:
        logger.error(f"トーナメント情報の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="トーナメント情報の取得に失敗しました")

@router.put(
    "/{tournament_id}",
    response_model=TournamentResponse,
    summary="トーナメント情報を更新する",
    description="指定されたIDのトーナメント情報を更新します。管理者のみが実行できます。"
)
async def update_tournament(
    tournament_id: str,
    tournament: TournamentUpdate,
    current_user: Annotated[dict, Depends(get_admin_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> TournamentResponse:
    """トーナメント情報を更新する

    Args:
        tournament_id (str): トーナメントID
        tournament (TournamentUpdate): 更新するトーナメントの情報
        current_user (dict): 現在のユーザー情報（管理者のみ）
        db (firestore.Client): Firestoreクライアント

    Returns:
        TournamentResponse: 更新されたトーナメントの情報

    Raises:
        HTTPException: トーナメントの更新に失敗した場合
    """
    try:
        doc_ref = db.collection('tournaments').document(tournament_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="トーナメントが見つかりません")

        # 更新データの準備
        update_data = tournament.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()

        # トーナメント情報の更新
        doc_ref.update(update_data)

        # 更新後のデータを取得
        updated_doc = doc_ref.get()
        updated_dict = updated_doc.to_dict()
        updated_dict['id'] = doc.id

        return TournamentResponse(**updated_dict)

    except Exception as e:
        logger.error(f"トーナメント情報の更新に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="トーナメント情報の更新に失敗しました")

@router.get(
    "",
    response_model=TournamentList,
    summary="トーナメント一覧を取得する",
    description="トーナメントの一覧を取得します。ステータスによるフィルタリングが可能です。"
)
async def list_tournaments(
    status: Annotated[TournamentStatus | None, Query(description="ステータスでフィルタリング")] = None,
    limit: Annotated[int, Query(gt=0, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> TournamentList:
    """トーナメント一覧を取得する

    Args:
        status (TournamentStatus | None): フィルタリングするステータス
        limit (int): 取得件数 (1-100)
        offset (int): オフセット (0以上)
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        TournamentList: トーナメント一覧

    Raises:
        HTTPException: トーナメント一覧の取得に失敗した場合
    """
    try:
        query = db.collection('tournaments')
        if status:
            query = query.where('status', '==', status)

        # 総件数の取得
        total_query = query.count()
        total = total_query.get()[0][0]

        # データの取得
        docs = query.offset(offset).limit(limit).stream()
        
        items = []
        for doc in docs:
            tournament_dict = doc.to_dict()
            tournament_dict['id'] = doc.id
            items.append(TournamentResponse(**tournament_dict))

        return TournamentList(items=items, total=total)

    except Exception as e:
        logger.error(f"トーナメント一覧の取得に失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="トーナメント一覧の取得に失敗しました")

@router.post(
    "/{tournament_id}/entries",
    response_model=TournamentResponse,
    summary="トーナメントにエントリーする",
    description="指定されたトーナメントにプレイヤーをエントリーします。チーム管理者のみが実行できます。"
)
async def create_entry(
    tournament_id: str,
    entry: Entry,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> TournamentResponse:
    """トーナメントにエントリーする

    Args:
        tournament_id (str): トーナメントID
        entry (Entry): エントリー情報
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        TournamentResponse: 更新されたトーナメントの情報

    Raises:
        HTTPException: エントリーに失敗した場合
    """
    try:
        # トーナメントの取得
        tournament_ref = db.collection('tournaments').document(tournament_id)
        tournament = tournament_ref.get()
        if not tournament.exists:
            raise HTTPException(status_code=404, detail="トーナメントが見つかりません")

        tournament_dict = tournament.to_dict()

        # エントリー期間のチェック
        now = datetime.utcnow()
        if now < tournament_dict['entry_start_date']:
            raise HTTPException(status_code=400, detail="エントリー開始前です")
        if now > tournament_dict['entry_end_date']:
            raise HTTPException(status_code=400, detail="エントリー期間が終了しています")

        # エントリー制限のチェック
        if tournament_dict['current_entries'] >= tournament_dict['entry_restriction']['max_players']:
            raise HTTPException(status_code=400, detail="エントリー上限に達しています")

        # チーム管理者権限の確認
        team_ref = db.collection('teams').document(entry.team_id)
        team = team_ref.get()
        if not team.exists:
            raise HTTPException(status_code=404, detail="指定されたチームが見つかりません")
        if team.to_dict()['manager_id'] != current_user['uid']:
            raise HTTPException(status_code=403, detail="チーム管理者のみがエントリーできます")

        # プレイヤーの存在確認とクラス制限のチェック
        player_ref = db.collection('players').document(entry.player_id)
        player = player_ref.get()
        if not player.exists:
            raise HTTPException(status_code=404, detail="指定されたプレイヤーが見つかりません")
        
        player_dict = player.to_dict()
        if player_dict['team_id'] != entry.team_id:
            raise HTTPException(status_code=400, detail="指定されたプレイヤーは所属チームのメンバーではありません")

        # エントリーの追加
        entry_dict = entry.dict()
        entry_dict['entry_date'] = now
        
        if 'entries' not in tournament_dict:
            tournament_dict['entries'] = []
        tournament_dict['entries'].append(entry_dict)
        tournament_dict['current_entries'] += 1
        tournament_dict['updated_at'] = now

        # トーナメント情報の更新
        tournament_ref.update(tournament_dict)

        # レスポンスの作成
        tournament_dict['id'] = tournament_id
        return TournamentResponse(**tournament_dict)

    except Exception as e:
        logger.error(f"トーナメントエントリーに失敗しました: {str(e)}")
        raise HTTPException(status_code=500, detail="トーナメントエントリーに失敗しました") 