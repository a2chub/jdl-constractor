"""
チーム管理APIのテスト

このモジュールでは以下のテストを実施します：
- チーム作成機能のテスト
- チーム情報取得機能のテスト
- チーム情報更新機能のテスト
- チームリスト取得機能のテスト
"""

import pytest
from fastapi import status
from firebase_admin import firestore
from unittest.mock import Mock, patch

from ..app.models.team import TeamCreate, TeamUpdate
from ..app.routers.team import router

@pytest.fixture
def mock_firestore():
    """Firestoreのモックを作成します。"""
    with patch('firebase_admin.firestore.Client') as mock:
        yield mock

@pytest.fixture
def mock_current_user():
    """現在のユーザー情報のモックを作成します。"""
    return {
        "uid": "test_user_id",
        "email": "test@example.com",
        "role": "admin"
    }

def test_create_team(mock_firestore, mock_current_user):
    """チーム作成機能のテスト"""
    # モックの設定
    mock_teams_ref = Mock()
    mock_firestore.collection.return_value = mock_teams_ref
    mock_teams_ref.where.return_value.get.return_value = []
    
    mock_doc_ref = Mock()
    mock_teams_ref.document.return_value = mock_doc_ref
    
    mock_doc = Mock()
    mock_doc.to_dict.return_value = {
        "name": "Test Team",
        "description": "Test Description",
        "logo_url": "http://example.com/logo.png",
        "manager_id": mock_current_user["uid"],
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "status": "active"
    }
    mock_doc.id = "test_team_id"
    mock_doc_ref.get.return_value = mock_doc

    # テストデータ
    team_data = {
        "name": "Test Team",
        "description": "Test Description",
        "logo_url": "http://example.com/logo.png"
    }

    # テストの実行
    response = router.post("/", json=team_data)

    # 結果の検証
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == team_data["name"]
    assert response.json()["description"] == team_data["description"]
    assert response.json()["logo_url"] == team_data["logo_url"]
    assert response.json()["manager_id"] == mock_current_user["uid"]

def test_get_team(mock_firestore, mock_current_user):
    """チーム情報取得機能のテスト"""
    # モックの設定
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "name": "Test Team",
        "description": "Test Description",
        "logo_url": "http://example.com/logo.png",
        "manager_id": mock_current_user["uid"],
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "status": "active"
    }
    mock_doc.id = "test_team_id"
    
    mock_doc_ref = Mock()
    mock_doc_ref.get.return_value = mock_doc
    
    mock_teams_ref = Mock()
    mock_teams_ref.document.return_value = mock_doc_ref
    mock_firestore.collection.return_value = mock_teams_ref

    # テストの実行
    response = router.get("/test_team_id")

    # 結果の検証
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "test_team_id"
    assert response.json()["name"] == "Test Team"

def test_list_teams(mock_firestore, mock_current_user):
    """チームリスト取得機能のテスト"""
    # モックの設定
    mock_teams = [
        Mock(
            to_dict=lambda: {
                "name": f"Test Team {i}",
                "description": f"Test Description {i}",
                "logo_url": f"http://example.com/logo{i}.png",
                "manager_id": mock_current_user["uid"],
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP,
                "status": "active"
            },
            id=f"test_team_id_{i}"
        )
        for i in range(3)
    ]
    
    mock_teams_ref = Mock()
    mock_teams_ref.where.return_value.get.return_value = mock_teams
    mock_firestore.collection.return_value = mock_teams_ref

    # テストの実行
    response = router.get("/")

    # 結果の検証
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3
    for i, team in enumerate(response.json()):
        assert team["name"] == f"Test Team {i}"
        assert team["id"] == f"test_team_id_{i}"

def test_update_team(mock_firestore, mock_current_user):
    """チーム情報更新機能のテスト"""
    # モックの設定
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "name": "Test Team",
        "description": "Test Description",
        "logo_url": "http://example.com/logo.png",
        "manager_id": mock_current_user["uid"],
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "status": "active"
    }
    mock_doc.id = "test_team_id"
    
    mock_doc_ref = Mock()
    mock_doc_ref.get.return_value = mock_doc
    mock_doc_ref.update.return_value = None
    
    mock_teams_ref = Mock()
    mock_teams_ref.document.return_value = mock_doc_ref
    mock_firestore.collection.return_value = mock_teams_ref

    # テストデータ
    update_data = {
        "name": "Updated Team",
        "description": "Updated Description"
    }

    # テストの実行
    response = router.put("/test_team_id", json=update_data)

    # 結果の検証
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Team"
    assert response.json()["description"] == "Updated Description" 