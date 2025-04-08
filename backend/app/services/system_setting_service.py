# backend/app/services/system_setting_service.py
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter # FieldFilterをインポート

try:
    from app.core.firebase import db
    from app.models.system_setting import SystemSettingResponse, SystemSettingUpdate, SystemSettingCreate
except ImportError as e:
    logging.error(f"システム設定サービスの初期化に必要なモジュールのインポートに失敗: {e}")
    db = None
    SystemSettingResponse = None
    SystemSettingUpdate = None
    SystemSettingCreate = None

logger = logging.getLogger(__name__)

SETTINGS_COLLECTION = "system_settings"

class SystemSettingService:
    """システム設定のCRUD操作を行うサービス"""

    def __init__(self, firestore_db: firestore.Client = db):
        if firestore_db is None:
            raise ValueError("Firestore client (db) is not available.")
        self.db = firestore_db
        self.settings_ref = self.db.collection(SETTINGS_COLLECTION)

    async def get_all_settings(self) -> List[SystemSettingResponse]:
        """全てのシステム設定を取得する"""
        logger.info("Fetching all system settings.")
        settings = []
        try:
            # stream() は同期的なので async for は使わない
            docs = self.settings_ref.stream()
            for doc in docs:
                 data = doc.to_dict()
                 if data:
                     # created_at, updated_at が Timestamp の場合 datetime に変換
                     # Firestore V1 client library returns datetime objects directly for Timestamps
                     # No explicit conversion needed unless dealing with older versions or specific cases
                     # Check type just in case
                     if 'created_at' in data and not isinstance(data['created_at'], datetime):
                          logger.warning(f"Setting '{doc.id}' has unexpected type for created_at: {type(data['created_at'])}. Setting to None.")
                          data['created_at'] = None
                     if 'updated_at' in data and not isinstance(data['updated_at'], datetime):
                          logger.warning(f"Setting '{doc.id}' has unexpected type for updated_at: {type(data['updated_at'])}. Setting to None.")
                          data['updated_at'] = None

                     # モデルに変換してリストに追加
                     try:
                          setting = SystemSettingResponse(key=doc.id, **data)
                          settings.append(setting)
                     except Exception as pydantic_error: # Pydantic validation error
                          logger.error(f"Failed to parse setting '{doc.id}' into SystemSettingResponse: {pydantic_error}. Data: {data}")

            logger.info(f"Found {len(settings)} system settings.")
            return settings
        except Exception as e:
            logger.exception(f"Error fetching all system settings: {e}")
            raise # Re-raise the exception to be handled by the caller

    async def get_setting(self, key: str) -> Optional[SystemSettingResponse]:
        """指定されたキーのシステム設定を取得する"""
        logger.info(f"Fetching system setting with key: {key}")
        try:
            doc_ref = self.settings_ref.document(key)
            # get() は非同期ではない (google-cloud-firestore >= 2.0)
            # 非同期クライアント (google-cloud-firestore[async]) を使っている場合は await が必要
            # ここでは同期クライアントを想定
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                # Type checking for dates (similar to get_all_settings)
                if 'created_at' in data and not isinstance(data['created_at'], datetime): data['created_at'] = None
                if 'updated_at' in data and not isinstance(data['updated_at'], datetime): data['updated_at'] = None

                logger.info(f"System setting '{key}' found.")
                try:
                    return SystemSettingResponse(key=doc.id, **data)
                except Exception as pydantic_error:
                    logger.error(f"Failed to parse setting '{key}' into SystemSettingResponse: {pydantic_error}. Data: {data}")
                    return None # またはエラーを示す別の方法
            else:
                logger.warning(f"System setting '{key}' not found.")
                return None
        except Exception as e:
            logger.exception(f"Error fetching system setting '{key}': {e}")
            raise

    async def update_setting(self, key: str, setting_update: SystemSettingUpdate) -> Optional[SystemSettingResponse]:
        """指定されたキーのシステム設定を更新する"""
        logger.info(f"Updating system setting with key: {key}")
        doc_ref = self.settings_ref.document(key)
        try:
            # 更新データを作成 (Noneを除外し、updated_atは強制的に更新)
            update_data = setting_update.model_dump(exclude_unset=True)

            if not update_data or ('value' not in update_data and 'description' not in update_data):
                 logger.warning(f"No meaningful fields to update for setting '{key}'. Skipping update.")
                 return await self.get_setting(key) # 現在の値を返す

            # updated_at をサーバータイムスタンプに設定
            update_data['updated_at'] = firestore.SERVER_TIMESTAMP

            # update() は非同期ではない
            doc_ref.update(update_data)
            logger.info(f"System setting '{key}' update initiated successfully.")

            # 更新後のデータを取得して返す (SERVER_TIMESTAMPが解決されるまで少しラグがある可能性)
            # 少し待ってから取得するか、クライアント側で楽観的更新を行う
            # ここでは即時取得を試みる
            updated_doc = doc_ref.get()
            if updated_doc.exists:
                 data = updated_doc.to_dict()
                 # SERVER_TIMESTAMPはまだ解決されていない可能性があるため、Noneにするか、推定値を入れる
                 if isinstance(data.get('updated_at'), firestore.SERVER_TIMESTAMP.__class__):
                      data['updated_at'] = datetime.now(datetime.timezone.utc) # 推定値として現在時刻(UTC)
                 elif not isinstance(data.get('updated_at'), datetime):
                      data['updated_at'] = None # 予期せぬ型

                 if 'created_at' in data and not isinstance(data['created_at'], datetime): data['created_at'] = None

                 try:
                      return SystemSettingResponse(key=updated_doc.id, **data)
                 except Exception as pydantic_error:
                      logger.error(f"Failed to parse updated setting '{key}' into SystemSettingResponse: {pydantic_error}. Data: {data}")
                      return None
            else:
                 # 更新直後に消えるのは異常
                 logger.error(f"Setting '{key}' not found immediately after update.")
                 return None

        except Exception as e:
            logger.exception(f"Error updating system setting '{key}': {e}")
            raise

    async def create_setting(self, setting_create: SystemSettingCreate) -> SystemSettingResponse:
        """新しいシステム設定を作成する"""
        key = setting_create.key
        logger.info(f"Creating new system setting with key: {key}")
        doc_ref = self.settings_ref.document(key)
        try:
            # 既に存在するかチェック
            existing_doc = doc_ref.get()
            if existing_doc.exists:
                 logger.error(f"System setting with key '{key}' already exists.")
                 # ここではエラーを発生させる
                 raise ValueError(f"Setting with key '{key}' already exists.")

            # 作成データ (keyを除外)
            create_data = setting_create.model_dump(exclude={'key'})
            # created_at, updated_at をサーバータイムスタンプに設定
            create_data['created_at'] = firestore.SERVER_TIMESTAMP
            create_data['updated_at'] = firestore.SERVER_TIMESTAMP

            # set() は非同期ではない
            doc_ref.set(create_data)
            logger.info(f"System setting '{key}' creation initiated successfully.")

            # 作成後のデータを取得して返す (ここでもSERVER_TIMESTAMPは未解決の可能性)
            created_doc = doc_ref.get()
            if created_doc.exists:
                 data = created_doc.to_dict()
                 now_utc = datetime.now(datetime.timezone.utc) # 推定値
                 if isinstance(data.get('created_at'), firestore.SERVER_TIMESTAMP.__class__): data['created_at'] = now_utc
                 if isinstance(data.get('updated_at'), firestore.SERVER_TIMESTAMP.__class__): data['updated_at'] = now_utc
                 # 型チェック
                 if 'created_at' in data and not isinstance(data['created_at'], datetime): data['created_at'] = None
                 if 'updated_at' in data and not isinstance(data['updated_at'], datetime): data['updated_at'] = None

                 try:
                      return SystemSettingResponse(key=key, **data)
                 except Exception as pydantic_error:
                      logger.error(f"Failed to parse created setting '{key}' into SystemSettingResponse: {pydantic_error}. Data: {data}")
                      # 作成はされたがパース失敗。エラーを上げるか？
                      raise RuntimeError(f"Setting '{key}' created but failed to parse response.") from pydantic_error
            else:
                 logger.error(f"Failed to retrieve created setting '{key}' immediately after creation.")
                 raise RuntimeError("Failed to retrieve created setting.")

        except ValueError as ve: # Key exists error
             raise ve # そのまま上に投げる
        except Exception as e:
            logger.exception(f"Error creating system setting '{key}': {e}")
            raise

    async def delete_setting(self, key: str) -> None:
        """指定されたキーのシステム設定を削除する"""
        logger.warning(f"Deleting system setting with key: {key}") # 削除は警告レベル
        doc_ref = self.settings_ref.document(key)
        try:
            # delete() は非同期ではない
            delete_result = doc_ref.delete()
            # delete_result には削除時刻などが含まれる
            logger.info(f"System setting '{key}' deleted successfully at {delete_result.read_time}.")
        except Exception as e:
            logger.exception(f"Error deleting system setting '{key}': {e}")
            raise
