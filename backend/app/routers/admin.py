# backend/app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
from google.cloud import firestore # firestore をインポート

# Firestoreクライアントと認証関連の依存関係をインポート
# (get_current_admin_user は仮の関数名。実際の認証実装に合わせる)
try:
    from app.core.firebase import db
    # Userモデルをインポート (get_current_admin_userが返す型)
    # 実際のUserモデルのパスに合わせて修正が必要な場合がある
    from app.models.user import User
    # 実際の認証依存関係をインポート (存在する場合)
    # from app.dependencies import get_current_admin_user
except ImportError as e:
     logging.error(f"管理者ルーターの初期化に必要なモジュールのインポートに失敗: {e}")
     # 実行時エラーを防ぐためにダミーを設定するか、エラーを発生させる
     db = None
     User = None
     # get_current_admin_user = None # ダミー関数で上書きするので不要

logger = logging.getLogger(__name__)

# --- 仮の管理者認証依存関係 ---
# TODO: 実際の管理者認証ロジックに置き換える
async def get_current_admin_user() -> User:
    """
    【仮実装】現在のユーザーが管理者であることを確認する依存関係。
    実際の認証メカニズム（例: Firebase Authトークン検証、DBでのロール確認）に置き換える必要があります。
    """
    logger.warning("仮の管理者認証依存関係 (get_current_admin_user) が使用されています。")
    # ここでは、認証済みで、かつ is_admin フラグが True であることを想定したダミーユーザーを返します。
    # 実際のアプリケーションでは、リクエストヘッダーからトークンを取得し、
    # Firebase Admin SDK などで検証し、ユーザー情報を取得して is_admin を確認します。
    # 例:
    # token = request.headers.get("Authorization")
    # decoded_token = auth.verify_id_token(token)
    # user_id = decoded_token['uid']
    # user_doc = db.collection('users').document(user_id).get()
    # if not user_doc.exists or not user_doc.to_dict().get('is_admin'):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    # return User(**user_doc.to_dict(), id=user_doc.id)

    # ダミー実装:
    if User: # Userモデルがインポートできている場合のみダミーを生成
        dummy_admin = User(id="dummy_admin_id", email="admin@example.com", name="Dummy Admin", is_admin=True, created_at=None, updated_at=None) # created_at/updated_atはOptionalならNone
        return dummy_admin
    else:
        # Userモデルがインポートできていない場合はエラー
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User model not available for admin check")

    # 認証失敗時の例
    # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # 管理者権限なし時の例
    # raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
# --- ここまで仮の依存関係 ---


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)], # このルーター全体に管理者認証を適用
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Admin privileges required"},
        404: {"description": "Not found"}
    },
)

@router.get("/dashboard/summary", response_model=Dict[str, int])
async def get_dashboard_summary(
    # current_user: User = Depends(get_current_admin_user) # ルーター全体で適用済みなら不要な場合も
) -> Dict[str, int]:
    """
    管理者ダッシュボード用の概要情報（各種カウント）を取得します。
    """
    logger.info("管理者ダッシュボードのサマリー取得リクエスト")
    if db is None:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database client not initialized")

    summary = {}
    # カウント対象のコレクション名をリストアップ
    collections_to_count = ["users", "teams", "players", "tournaments"]

    try:
        for collection_name in collections_to_count:
            logger.debug(f"Counting documents in collection: {collection_name}")
            # Firestoreのcount()アグリゲーションを使用 (google-cloud-firestore v2.7.0 以降)
            # count()は同期的に結果を返すオブジェクトを生成する
            count_agg = db.collection(collection_name).count()
            # .get() で結果を取得
            result = count_agg.get()
            # 結果はリストのリストで返る [[<AggregateQueryResponse value=...>]]
            if result and result[0]:
                 count = result[0][0].value
                 summary[collection_name + "_count"] = count
                 logger.debug(f"Collection '{collection_name}' count: {count}")
            else:
                 # 結果が取得できなかった場合（通常は発生しないはず）
                 summary[collection_name + "_count"] = 0
                 logger.warning(f"Could not retrieve count for collection: {collection_name}")


            # # stream() を使う場合の代替コード (非効率)
            # try:
            #     docs_stream = db.collection(collection_name).stream()
            #     count = sum(1 for _ in docs_stream)
            #     summary[collection_name + "_count"] = count
            #     logger.debug(f"Collection '{collection_name}' count (via stream): {count}")
            # except Exception as stream_e:
            #     logger.error(f"Error counting collection '{collection_name}' via stream: {stream_e}")
            #     summary[collection_name + "_count"] = -1 # エラーを示す値

        # 必要に応じて他のサマリー情報も追加
        # summary["active_tournaments_count"] = ...
        logger.info(f"Dashboard summary generated: {summary}")
        return summary
    except Exception as e:
        logger.exception(f"Failed to retrieve dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard summary: {str(e)}"
        )

# --- System Settings Endpoints ---

from app.services.system_setting_service import SystemSettingService
# --- User Management Imports ---
from app.models.user import UserResponse # UserListモデルがあればそれを使う
from fastapi import Query
from typing import Optional, List # List を追加
from pydantic import BaseModel # BaseModel を追加
from datetime import datetime # datetime を追加
from google.cloud.firestore_v1.base_query import FieldFilter # FieldFilter を追加
from app.models.system_setting import SystemSettingResponse, SystemSettingUpdate, SystemSettingCreate
from typing import List

@router.get("/settings", response_model=List[SystemSettingResponse])
async def get_all_system_settings(
    setting_service: SystemSettingService = Depends(SystemSettingService)
):
    """全てのシステム設定を取得します。"""
    try:
        return await setting_service.get_all_settings()
    except Exception as e:
        logger.exception("Failed to get all system settings")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve system settings")

@router.get("/settings/{key}", response_model=SystemSettingResponse)
async def get_system_setting(
    key: str,
    setting_service: SystemSettingService = Depends(SystemSettingService)
):
    """指定されたキーのシステム設定を取得します。"""
    setting = await setting_service.get_setting(key)
    if setting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting with key '{key}' not found")
    return setting

@router.put("/settings/{key}", response_model=SystemSettingResponse)
async def update_system_setting(
    key: str,
    setting_update: SystemSettingUpdate,
    setting_service: SystemSettingService = Depends(SystemSettingService)
):
    """指定されたキーのシステム設定を更新します。"""
    try:
        updated_setting = await setting_service.update_setting(key, setting_update)
        if updated_setting is None:
             # update_setting内で見つからない場合Noneが返る可能性がある
             # あるいは更新対象がない場合もNoneが返る可能性がある（サービス実装による）
             # ここでは404を返すのが適切か、あるいは更新がスキップされたことを示すか？
             # サービスがNoneを返すのは「見つからない」場合のみと仮定
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting with key '{key}' not found or no update performed")
        return updated_setting
    except ValueError as ve: # 例: バリデーションエラーなど
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.exception(f"Failed to update system setting '{key}'")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update system setting")

@router.post("/settings", response_model=SystemSettingResponse, status_code=status.HTTP_201_CREATED)
async def create_system_setting(
    setting_create: SystemSettingCreate,
    setting_service: SystemSettingService = Depends(SystemSettingService)
):
    """新しいシステム設定を作成します。"""
    try:
        created_setting = await setting_service.create_setting(setting_create)
        return created_setting
    except ValueError as ve: # キー重複エラーなど
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        logger.exception("Failed to create system setting")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create system setting")

@router.delete("/settings/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_setting(
    key: str,
    setting_service: SystemSettingService = Depends(SystemSettingService)
):
    """指定されたキーのシステム設定を削除します。"""
    try:
        # 存在確認をしてから削除するか、サービス側でNotFoundをハンドルするか
        setting = await setting_service.get_setting(key)
        if setting is None:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting with key '{key}' not found")
        await setting_service.delete_setting(key)
        return # No content
    except HTTPException as http_exc: # 404エラーを再throw
         raise http_exc
    except Exception as e:
            logger.exception(f"Failed to delete system setting '{key}'")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete system setting")


    # --- User Management Endpoints ---

    # UserListモデルがない場合、List[UserResponse] を使う
    # 必要であればページネーション用のモデルを定義
    class UserListResponse(BaseModel):
         items: List[UserResponse]
         total: int

    @router.get("/users", response_model=UserListResponse) # UserListモデルがあればそれに変更
    async def list_users(
        page: int = Query(1, ge=1, description="ページ番号"),
        limit: int = Query(10, ge=1, le=100, description="1ページあたりのアイテム数"),
        search: Optional[str] = Query(None, description="検索クエリ（名前 or メールアドレス）"),
        is_admin: Optional[bool] = Query(None, description="管理者フラグでフィルタリング")
    ):
        """ユーザー一覧を取得します（ページネーション、検索、フィルタリング対応）。"""
        logger.info(f"Listing users: page={page}, limit={limit}, search='{search}', is_admin={is_admin}")
        if db is None:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database client not initialized")

        users_query = db.collection("users")
        conditions = [] # フィルタ条件を格納するリスト

        # フィルタリング条件の作成
        if is_admin is not None:
            conditions.append(FieldFilter("is_admin", "==", is_admin))

        # 検索条件の作成 (Firestoreの制限を考慮)
        # 注意: is_admin でフィルタリングしている場合、他のフィールドでの inequality filter は使えない
        # 注意: OR検索は直接サポートされていない
        # ここでは is_admin フィルタがある場合は検索を無視するか、クライアント側で処理する
        if search and is_admin is None: # is_adminフィルタがない場合のみ部分的な検索を試みる
             search_lower = search.lower()
             # Firestoreは部分一致を直接サポートしないため、>= と < を使った範囲クエリで擬似的に行うか、
             # 全件取得してフィルタリングする必要がある（非効率）。
             # ここでは全件取得＆フィルタリング方式を採用。
             logger.warning("Search query provided without specific filters, may be inefficient.")
             pass # 検索ロジックは後段のPythonフィルタリングで行う
        elif search and is_admin is not None:
             logger.warning("Search query ignored because is_admin filter is active (Firestore limitation).")
             search = None # 検索を無効化

        # クエリの組み立て
        if conditions:
             # 複数の where を使う場合、Firestoreは複合インデックスを要求することがある
             # ここでは is_admin のみなので問題ないはず
             for condition in conditions:
                  users_query = users_query.where(filter=condition)
        else:
             # フィルタがない場合は全件取得 (順序付けが必要なら orderBy を追加)
             users_query = users_query.order_by("name") # 例: 名前順

        # 全件取得 (フィルタリング後)
        try:
             all_users_snapshot = users_query.stream()
        except Exception as e:
             logger.exception(f"Error querying users from Firestore: {e}")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to query users")

        filtered_users = []
        for doc in all_users_snapshot:
             user_data = doc.to_dict()
             if not user_data: continue # データがないドキュメントはスキップ

             user_data["id"] = doc.id # IDを追加

             # Python側での検索フィルタリング (search が有効な場合)
             if search:
                  search_lower = search.lower()
                  name_match = user_data.get("name") and search_lower in user_data["name"].lower()
                  email_match = user_data.get("email") and search_lower in user_data["email"].lower()
                  if not (name_match or email_match):
                       continue # 検索条件に合致しない場合はスキップ

             # 日付の型チェックと変換
             if 'created_at' in user_data and not isinstance(user_data['created_at'], datetime): user_data['created_at'] = None
             if 'updated_at' in user_data and not isinstance(user_data['updated_at'], datetime): user_data['updated_at'] = None

             # UserResponseモデルに変換
             try:
                  # UserResponseに必要なフィールドが揃っているか確認
                  # UserResponseの定義によっては不足フィールドでエラーになる可能性あり
                  filtered_users.append(UserResponse(**user_data))
             except Exception as p_err:
                  logger.error(f"Failed to parse user data for doc {doc.id}: {p_err}. Data: {user_data}")


        # ページネーション (Python側で処理)
        total_users = len(filtered_users)
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_users = filtered_users[start_index:end_index]

        logger.info(f"Found {total_users} users matching criteria. Returning page {page} with {len(paginated_users)} users.")

        # TODO: Firestoreのカーソルベースページネーションを実装して効率化する
        # https://firebase.google.com/docs/firestore/query-data/query-cursors

        return UserListResponse(items=paginated_users, total=total_users)

    class UpdateAdminStatusPayload(BaseModel):
        is_admin: bool

    @router.put("/users/{user_id}/admin", response_model=UserResponse)
    async def update_user_admin_status(
        user_id: str,
        payload: UpdateAdminStatusPayload
        # current_admin: User = Depends(get_current_admin_user) # ルーターレベルで適用済み
    ):
        """指定されたユーザーの管理者権限を更新します。"""
        logger.info(f"Updating admin status for user {user_id} to {payload.is_admin}")
        if db is None:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database client not initialized")

        user_ref = db.collection("users").document(user_id)
        try:
            # ユーザーが存在するか確認
            user_doc = user_ref.get()
            if not user_doc.exists:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id '{user_id}' not found")

            # 自分自身の権限は変更できないようにする (任意だが推奨)
            # if user_id == current_admin.id:
            #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own admin status")

            # is_admin フラグと updated_at を更新
            update_data = {
                "is_admin": payload.is_admin,
                "updated_at": firestore.SERVER_TIMESTAMP
            }
            user_ref.update(update_data)
            logger.info(f"Admin status for user {user_id} updated successfully.")

            # 更新後のユーザー情報を取得して返す
            updated_user_doc = user_ref.get()
            if updated_user_doc.exists:
                 data = updated_user_doc.to_dict()
                 data["id"] = updated_user_doc.id
                 # 日付の型チェック
                 if 'created_at' in data and not isinstance(data['created_at'], datetime): data['created_at'] = None
                 if isinstance(data.get('updated_at'), firestore.SERVER_TIMESTAMP.__class__):
                      data['updated_at'] = datetime.now(datetime.timezone.utc) # 推定値
                 elif not isinstance(data.get('updated_at'), datetime):
                      data['updated_at'] = None

                 try:
                      return UserResponse(**data)
                 except Exception as p_err:
                      logger.error(f"Failed to parse updated user data for doc {user_id}: {p_err}")
                      # 更新は成功したがレスポンス生成失敗
                      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User updated but failed to generate response")
            else:
                 logger.error(f"User {user_id} not found immediately after update.")
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User updated but failed to retrieve updated data")

        except HTTPException as http_exc:
             raise http_exc # 404などを再throw
        except Exception as e:
            logger.exception(f"Failed to update admin status for user {user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update admin status")

    class UpdateLockStatusPayload(BaseModel):
        is_locked: bool

    @router.put("/users/{user_id}/lock", response_model=UserResponse)
    async def update_user_lock_status(
        user_id: str,
        payload: UpdateLockStatusPayload
    ):
        """指定されたユーザーのアカウントロック状態を更新します。"""
        logger.info(f"Updating lock status for user {user_id} to {payload.is_locked}")
        if db is None:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database client not initialized")

        user_ref = db.collection("users").document(user_id)
        try:
            user_doc = user_ref.get()
            if not user_doc.exists:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id '{user_id}' not found")

            # is_locked フラグと updated_at を更新
            update_data = {
                "is_locked": payload.is_locked,
                "updated_at": firestore.SERVER_TIMESTAMP
            }
            user_ref.update(update_data)
            logger.info(f"Lock status for user {user_id} updated successfully.")

            # 更新後のユーザー情報を取得して返す
            updated_user_doc = user_ref.get()
            if updated_user_doc.exists:
                 data = updated_user_doc.to_dict()
                 data["id"] = updated_user_doc.id
                 # 日付の型チェック
                 if 'created_at' in data and not isinstance(data['created_at'], datetime): data['created_at'] = None
                 if isinstance(data.get('updated_at'), firestore.SERVER_TIMESTAMP.__class__):
                      data['updated_at'] = datetime.now(datetime.timezone.utc) # 推定値
                 elif not isinstance(data.get('updated_at'), datetime):
                      data['updated_at'] = None

                 try:
                      return UserResponse(**data)
                 except Exception as p_err:
                      logger.error(f"Failed to parse updated user data for doc {user_id}: {p_err}")
                      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User updated but failed to generate response")
            else:
                 logger.error(f"User {user_id} not found immediately after update.")
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User updated but failed to retrieve updated data")

        except HTTPException as http_exc:
             raise http_exc
        except Exception as e:
            logger.exception(f"Failed to update lock status for user {user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update lock status")


    # 他のユーザー管理エンドポイント (ロックなど) をここに追加


    # 他の管理者用エンドポイントをここに追加していく
