"""
Firebase初期化とFirestore設定を管理するモジュール

このモジュールは、Firebase Admin SDKの初期化、Firestoreクライアントの設定、
および認証トークンの検証機能を提供します。
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import Dict, Any

# Firebase初期化
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS', 'firebase-credentials.json'))
firebase_admin.initialize_app(cred)

# Firestoreクライアント
db = firestore.client()

def verify_id_token(token: str) -> Dict[str, Any]:
    """
    Firebaseの認証トークンを検証し、ユーザー情報を取得します。

    Args:
        token (str): 検証するFirebase IDトークン

    Returns:
        Dict[str, Any]: ユーザー情報を含む辞書

    Raises:
        firebase_admin.auth.InvalidIdTokenError: トークンが無効な場合
        firebase_admin.auth.ExpiredIdTokenError: トークンの有効期限が切れている場合
        firebase_admin.auth.RevokedIdTokenError: トークンが失効している場合
    """
    decoded_token = auth.verify_id_token(token)
    return decoded_token

def get_user_role(user_id: str) -> str:
    """
    ユーザーのロールを取得します。

    Args:
        user_id (str): ユーザーID

    Returns:
        str: ユーザーロール ('admin', 'manager', 'general' のいずれか)
    """
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        return 'general'
    return user_doc.to_dict().get('role', 'general')

# Firestoreコレクション参照
teams_ref = db.collection('teams')
players_ref = db.collection('players')
tournaments_ref = db.collection('tournaments')
users_ref = db.collection('users')
