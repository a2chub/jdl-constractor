"""
チーム管理APIルーター

このモジュールは以下の機能を提供します：
- チームの作成
- チーム情報の取得
- チーム情報の更新
- チームリストの取得
"""

from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore
from typing import List

from ..core.firebase import get_firestore
from ..models.team import TeamCreate, TeamUpdate, TeamResponse
from ..core.auth import get_current_user

router = APIRouter(
    prefix="/teams",
    tags=["teams"]
)

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team: TeamCreate,
    db: firestore.Client = Depends(get_firestore),
    current_user: dict = Depends(get_current_user)
):
    """
    新しいチームを作成します。

    Args:
        team (TeamCreate): 作成するチームの情報
        db (firestore.Client): Firestoreクライアント
        current_user (dict): 現在のユーザー情報

    Returns:
        TeamResponse: 作成されたチームの情報

    Raises:
        HTTPException: チーム名が既に存在する場合や、権限がない場合
    """
    # チーム名の重複チェック
    teams_ref = db.collection('teams')
    existing_team = teams_ref.where('name', '==', team.name).get()
    if len(list(existing_team)) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team name already exists"
        )

    # チームデータの作成
    team_data = {
        "name": team.name,
        "description": team.description,
        "logo_url": team.logo_url,
        "manager_id": current_user["uid"],
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "status": "active"
    }

    # Firestoreにデータを保存
    team_ref = teams_ref.document()
    team_ref.set(team_data)

    # 保存したデータを取得
    created_team = team_ref.get()
    team_dict = created_team.to_dict()
    team_dict["id"] = created_team.id

    return TeamResponse(**team_dict)

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    db: firestore.Client = Depends(get_firestore),
    current_user: dict = Depends(get_current_user)
):
    """
    指定されたIDのチーム情報を取得します。

    Args:
        team_id (str): チームID
        db (firestore.Client): Firestoreクライアント
        current_user (dict): 現在のユーザー情報

    Returns:
        TeamResponse: チームの情報

    Raises:
        HTTPException: チームが存在しない場合や、権限がない場合
    """
    team_ref = db.collection('teams').document(team_id)
    team = team_ref.get()

    if not team.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    team_data = team.to_dict()
    team_data["id"] = team.id

    return TeamResponse(**team_data)

@router.get("/", response_model=List[TeamResponse])
async def list_teams(
    db: firestore.Client = Depends(get_firestore),
    current_user: dict = Depends(get_current_user)
):
    """
    全てのチームのリストを取得します。

    Args:
        db (firestore.Client): Firestoreクライアント
        current_user (dict): 現在のユーザー情報

    Returns:
        List[TeamResponse]: チームのリスト
    """
    teams_ref = db.collection('teams')
    teams = teams_ref.where('status', '==', 'active').get()

    team_list = []
    for team in teams:
        team_data = team.to_dict()
        team_data["id"] = team.id
        team_list.append(TeamResponse(**team_data))

    return team_list

@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_update: TeamUpdate,
    db: firestore.Client = Depends(get_firestore),
    current_user: dict = Depends(get_current_user)
):
    """
    指定されたIDのチーム情報を更新します。

    Args:
        team_id (str): チームID
        team_update (TeamUpdate): 更新するチームの情報
        db (firestore.Client): Firestoreクライアント
        current_user (dict): 現在のユーザー情報

    Returns:
        TeamResponse: 更新されたチームの情報

    Raises:
        HTTPException: チームが存在しない場合や、権限がない場合
    """
    team_ref = db.collection('teams').document(team_id)
    team = team_ref.get()

    if not team.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # 権限チェック
    team_data = team.to_dict()
    if team_data["manager_id"] != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this team"
        )

    # 更新データの準備
    update_data = team_update.dict(exclude_unset=True)
    update_data["updated_at"] = firestore.SERVER_TIMESTAMP

    # データの更新
    team_ref.update(update_data)

    # 更新後のデータを取得
    updated_team = team_ref.get()
    team_dict = updated_team.to_dict()
    team_dict["id"] = updated_team.id

    return TeamResponse(**team_dict) 