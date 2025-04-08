"""
クラス変更機能のテストモジュール

このモジュールでは、クラス変更リクエスト、承認、履歴取得の
機能テストを実装します。
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from app.models.class_change import (
    ClassChangeRequest,
    ClassChangeApproval,
    ClassChangeHistory
)

@pytest.fixture
def mock_db():
    """Firestoreクライアントのモック"""
    with patch('google.cloud.firestore.Client') as mock:
        yield mock

@pytest.fixture
def mock_current_user():
    """現在のユーザー情報のモック"""
    return {
        'uid': 'test_user_id',
        'email': 'test@example.com',
        'role': 'admin'
    }

@pytest.fixture
def mock_player_data():
    """プレイヤーデータのモック"""
    return {
        'id': 'test_player_id',
        'name': 'Test Player',
        'team_id': 'test_team_id',
        'current_class': 'B',
        'updated_at': datetime.utcnow()
    }

@pytest.fixture
def mock_team_data():
    """チームデータのモック"""
    return {
        'id': 'test_team_id',
        'name': 'Test Team',
        'manager_id': 'test_user_id'
    }

async def test_request_class_change_success(
    mock_db,
    mock_current_user,
    mock_player_data,
    mock_team_data
):
    """クラス変更リクエストの成功ケースをテスト"""
    # モックの設定
    player_ref = MagicMock()
    player_ref.get.return_value.exists = True
    player_ref.get.return_value.to_dict.return_value = mock_player_data

    team_ref = MagicMock()
    team_ref.get.return_value.exists = True
    team_ref.get.return_value.to_dict.return_value = mock_team_data

    history_ref = MagicMock()
    history_ref.id = 'test_history_id'

    mock_db.return_value.collection.side_effect = lambda name: {
        'players': MagicMock(document=lambda id: player_ref),
        'teams': MagicMock(document=lambda id: team_ref),
        'class_change_history': MagicMock(document=lambda: history_ref)
    }[name]

    # リクエストの作成
    request = ClassChangeRequest(
        player_id='test_player_id',
        new_class='A',
        reason='Test reason'
    )

    # テスト実行
    from app.routers.class_change import request_class_change
    result = await request_class_change(request, mock_current_user, mock_db())

    # 検証
    assert result.player_id == request.player_id
    assert result.new_class == request.new_class
    assert result.status == 'pending'
    assert result.requested_by == mock_current_user['uid']

async def test_request_class_change_invalid_player(mock_db, mock_current_user):
    """存在しないプレイヤーに対するリクエストをテスト"""
    # モックの設定
    player_ref = MagicMock()
    player_ref.get.return_value.exists = False

    mock_db.return_value.collection.return_value.document.return_value = player_ref

    # リクエストの作成
    request = ClassChangeRequest(
        player_id='invalid_player_id',
        new_class='A',
        reason='Test reason'
    )

    # テスト実行と検証
    from app.routers.class_change import request_class_change
    with pytest.raises(HTTPException) as exc_info:
        await request_class_change(request, mock_current_user, mock_db())
    assert exc_info.value.status_code == 404

async def test_approve_class_change_success(
    mock_db,
    mock_current_user,
    mock_player_data
):
    """クラス変更承認の成功ケースをテスト"""
    # モックの設定
    history_data = {
        'id': 'test_history_id',
        'player_id': 'test_player_id',
        'old_class': 'B',
        'new_class': 'A',
        'status': 'pending',
        'requested_by': 'test_requester_id',
        'requested_at': datetime.utcnow()
    }

    history_ref = MagicMock()
    history_ref.get.return_value.exists = True
    history_ref.get.return_value.to_dict.return_value = history_data

    player_ref = MagicMock()
    player_ref.get.return_value.exists = True
    player_ref.get.return_value.to_dict.return_value = mock_player_data

    mock_db.return_value.collection.side_effect = lambda name: {
        'class_change_history': MagicMock(document=lambda id: history_ref),
        'players': MagicMock(document=lambda id: player_ref)
    }[name]

    # 承認リクエストの作成
    approval = ClassChangeApproval(
        approved=True,
        comment='Approved'
    )

    # テスト実行
    from app.routers.class_change import approve_class_change
    result = await approve_class_change('test_history_id', approval, mock_current_user, mock_db())

    # 検証
    assert result.status == 'approved'
    assert result.approved_by == mock_current_user['uid']
    assert result.comment == approval.comment

async def test_get_class_change_history(mock_db, mock_current_user):
    """クラス変更履歴取得のテスト"""
    # モックの設定
    history_data = [{
        'id': f'history_{i}',
        'player_id': 'test_player_id',
        'old_class': 'B',
        'new_class': 'A',
        'status': 'approved',
        'requested_by': 'test_requester_id',
        'requested_at': datetime.utcnow() - timedelta(days=i)
    } for i in range(3)]

    mock_query = MagicMock()
    mock_query.stream.return_value = [
        type('MockDoc', (), {'to_dict': lambda: data})
        for data in history_data
    ]

    mock_db.return_value.collection.return_value.where.return_value = mock_query
    mock_db.return_value.collection.return_value.where.return_value.order_by.return_value = mock_query
    mock_db.return_value.collection.return_value.where.return_value.order_by.return_value.offset.return_value = mock_query
    mock_db.return_value.collection.return_value.where.return_value.order_by.return_value.offset.return_value.limit.return_value = mock_query

    # テスト実行
    from app.routers.class_change import get_class_change_history
    result = await get_class_change_history('test_player_id', mock_current_user, mock_db())

    # 検証
    assert len(result) == 3
    assert all(isinstance(item, ClassChangeHistory) for item in result)
    assert result[0].player_id == 'test_player_id' 