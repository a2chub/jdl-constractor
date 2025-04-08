"""
チーム権限管理のルーターを定義するモジュール

このモジュールでは、チームの権限管理に関連するエンドポイントを定義します。
権限の作成、更新、取得、削除などのエンドポイントを提供します。
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from firebase_admin import firestore

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.team_permission import (
    TeamPermissionCreate,
    TeamPermissionUpdate,
    TeamPermissionResponse,
    TeamPermissionList,
    TeamRole
)
from app.services.team_permission_service import TeamPermissionService

router = APIRouter(
    prefix="/team-permissions",
    tags=["team-permissions"]
)

@router.post(
    "",
    response_model=TeamPermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="チーム権限を作成する",
    description="新しいチーム権限を作成します。"
)
async def create_team_permission(
    permission: TeamPermissionCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> TeamPermissionResponse:
    """
    チーム権限を作成する

    Args:
        permission (TeamPermissionCreate): 作成する権限情報
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        TeamPermissionResponse: 作成された権限情報

    Raises:
        HTTPException: 権限がない場合やバリデーションエラーの場合
    """
    service = TeamPermissionService(db)

    try:
        return await service.create_permission(permission)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/{permission_id}",
    response_model=TeamPermissionResponse,
    summary="チーム権限を更新する",
    description="既存のチーム権限を更新します。"
)
async def update_team_permission(
    permission_id: str,
    update_data: TeamPermissionUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> TeamPermissionResponse:
    """
    チーム権限を更新する

    Args:
        permission_id (str): 更新する権限のID
        update_data (TeamPermissionUpdate): 更新データ
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        TeamPermissionResponse: 更新された権限情報

    Raises:
        HTTPException: 権限が見つからない場合や権限がない場合
    """
    service = TeamPermissionService(db)

    try:
        return await service.update_permission(permission_id, update_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "見つかりません" in str(e)
            else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{permission_id}",
    response_model=TeamPermissionResponse,
    summary="チーム権限を取得する",
    description="指定されたチーム権限の情報を取得します。"
)
async def get_team_permission(
    permission_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> TeamPermissionResponse:
    """
    チーム権限を取得する

    Args:
        permission_id (str): 取得する権限のID
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Returns:
        TeamPermissionResponse: 取得された権限情報

    Raises:
        HTTPException: 権限が見つからない場合や権限がない場合
    """
    service = TeamPermissionService(db)

    try:
        return await service.get_permission(permission_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "見つかりません" in str(e)
            else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "",
    response_model=TeamPermissionList,
    summary="チーム権限一覧を取得する",
    description="指定されたチームの権限一覧を取得します。"
)
async def list_team_permissions(
    team_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)],
    limit: Annotated[int, Query(gt=0, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0
) -> TeamPermissionList:
    """
    チーム権限一覧を取得する

    Args:
        team_id (str): チームID
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント
        limit (int): 取得件数 (1-100)
        offset (int): オフセット (0以上)

    Returns:
        TeamPermissionList: 権限一覧

    Raises:
        HTTPException: 権限がない場合
    """
    service = TeamPermissionService(db)

    try:
        return await service.list_team_permissions(team_id, limit, offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="チーム権限を削除する",
    description="指定されたチーム権限を削除します。"
)
async def delete_team_permission(
    permission_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[firestore.Client, Depends(get_db)]
) -> None:
    """
    チーム権限を削除する

    Args:
        permission_id (str): 削除する権限のID
        current_user (dict): 現在のユーザー情報
        db (firestore.Client): Firestoreクライアント

    Raises:
        HTTPException: 権限が見つからない場合や権限がない場合
    """
    service = TeamPermissionService(db)

    try:
        await service.delete_permission(permission_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "見つかりません" in str(e)
            else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 