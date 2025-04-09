"""
通知機能に関するユーティリティモジュール

このモジュールでは、メール通知やアプリ内通知などの
通知機能を提供します。
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from google.cloud import firestore
from datetime import datetime
import os

from .logger import get_logger

logger = get_logger(__name__)

async def send_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = 'system'
) -> None:
    """通知を送信する

    Args:
        user_id (str): 通知先ユーザーID
        title (str): 通知タイトル
        message (str): 通知メッセージ
        notification_type (str, optional): 通知タイプ. Defaults to 'system'.

    Raises:
        Exception: 通知の送信に失敗した場合
    """
    try:
        # Firestoreに通知を保存
        db = firestore.Client()
        notification_ref = db.collection('notifications').document()
        
        notification_data = {
            'id': notification_ref.id,
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'created_at': datetime.utcnow(),
            'read': False
        }
        
        notification_ref.set(notification_data)

        # メール通知の送信（管理者向け）
        if notification_type == 'admin':
            await send_email_notification(
                os.getenv('ADMIN_EMAIL'),
                title,
                message
            )

    except Exception as e:
        logger.error(f"通知の送信に失敗しました: {str(e)}")
        raise

async def send_email_notification(
    to_email: str,
    subject: str,
    body: str
) -> None:
    """メール通知を送信する

    Args:
        to_email (str): 送信先メールアドレス
        subject (str): メール件名
        body (str): メール本文

    Raises:
        Exception: メールの送信に失敗した場合
    """
    try:
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL')

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

    except Exception as e:
        logger.error(f"メール通知の送信に失敗しました: {str(e)}")
        raise

async def mark_notification_as_read(notification_id: str) -> None:
    """通知を既読にする

    Args:
        notification_id (str): 通知ID

    Raises:
        Exception: 通知の更新に失敗した場合
    """
    try:
        db = firestore.Client()
        notification_ref = db.collection('notifications').document(notification_id)
        notification_ref.update({'read': True})

    except Exception as e:
        logger.error(f"通知の既読化に失敗しました: {str(e)}")
        raise

async def get_unread_notifications(user_id: str) -> list:
    """未読通知を取得する

    Args:
        user_id (str): ユーザーID

    Returns:
        list: 未読通知のリスト

    Raises:
        Exception: 通知の取得に失敗した場合
    """
    try:
        db = firestore.Client()
        notifications = (
            db.collection('notifications')
            .where('user_id', '==', user_id)
            .where('read', '==', False)
            .order_by('created_at', direction=firestore.Query.DESCENDING)
            .stream()
        )

        return [doc.to_dict() for doc in notifications]

    except Exception as e:
        logger.error(f"未読通知の取得に失敗しました: {str(e)}")
        raise 