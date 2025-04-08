# backend/app/services/jdl_master_sync_service.py
import csv
from datetime import datetime
import logging
from typing import Dict, List, Tuple

from google.cloud import firestore
from pydantic import ValidationError

from app.core.firebase import db
from app.models.player import PlayerBase, PlayerUpdate  # PlayerUpdateは直接使わないが参照用に

logger = logging.getLogger(__name__)

class JdlMasterSyncService:
    """JDL IDマスターデータ同期サービス"""

    def __init__(self, firestore_db: firestore.Client = db):
        self.db = firestore_db
        self.players_ref = self.db.collection('players')

    def sync_from_csv(self, csv_file_path: str) -> Tuple[int, int, List[str]]:
        """
        CSVファイルからマスターデータを読み込み、Firestoreのプレイヤーデータを同期する。

        Args:
            csv_file_path (str): 同期するCSVファイルのパス。

        Returns:
            Tuple[int, int, List[str]]: (更新されたプレイヤー数, スキップされたプレイヤー数, エラーリスト)
        """
        updated_count = 0
        skipped_count = 0
        errors = []
        master_data = {}

        # 1. CSVファイルを読み込み、検証する
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    line_num = i + 2  # ヘッダー行を考慮
                    try:
                        # データ検証 (Pydanticモデルを利用)
                        # PlayerBaseに必要なフィールドを抽出して検証
                        player_data = {
                            "name": row.get("player_name"),
                            "jdl_id": row.get("jdl_id"),
                            # team_id はマスターデータに含まれないためNone
                            "team_id": None,
                            "participation_count": int(row.get("participation_count", 0)),
                            "current_class": row.get("current_class"),
                            # last_updated_by_master は同期時に設定
                        }
                        # PlayerBaseで基本的な型とフォーマットを検証
                        validated_data = PlayerBase(**player_data)

                        # last_updated はCSVから取得し、datetimeに変換
                        last_updated_str = row.get("last_updated")
                        if last_updated_str:
                            try:
                                # ISO 8601形式を想定 (例: 2023-10-27T10:00:00Z or 2023-10-27T19:00:00+09:00)
                                # タイムゾーン情報がない場合はUTCとみなすか、エラーとするか検討
                                # ここでは fromisoformat を使用し、タイムゾーンがあればそれを使い、なければnaiveなdatetimeとする
                                last_updated_dt = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00')) # Zをオフセットに置換
                            except ValueError:
                                raise ValueError(f"last_updated の日付形式が無効です (ISO 8601形式を期待): {last_updated_str}")
                        else:
                            raise ValueError("last_updated フィールドが存在しません")

                        master_data[validated_data.jdl_id] = {
                            "data": validated_data,
                            "last_updated": last_updated_dt,
                            "line_num": line_num
                        }

                    except (ValidationError, ValueError, TypeError) as e:
                        error_msg = f"CSV L{line_num}: データ検証エラー - {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        skipped_count += 1
                    except Exception as e:
                        error_msg = f"CSV L{line_num}: 予期せぬエラー - {e}"
                        logger.exception(error_msg) # スタックトレースも記録
                        errors.append(error_msg)
                        skipped_count += 1

        except FileNotFoundError:
            error_msg = f"CSVファイルが見つかりません: {csv_file_path}"
            logger.error(error_msg)
            errors.append(error_msg)
            return 0, 0, errors
        except Exception as e:
            error_msg = f"CSVファイルの読み込み中にエラーが発生しました: {e}"
            logger.exception(error_msg)
            errors.append(error_msg)
            return 0, skipped_count, errors

        if not master_data and not errors: # 有効データがなく、ファイル読み込みエラーもない場合
             logger.warning("CSVファイルから有効なデータが読み込めませんでした。")
             return 0, skipped_count, errors # ここまでのエラーを返す
        elif not master_data and errors: # ファイル読み込みエラーがある場合
             return 0, skipped_count, errors # そのエラーを返す

        # 2. Firestoreから既存のプレイヤーデータを取得 (JDL IDをキーにする)
        existing_players = {}
        try:
            docs = self.players_ref.stream()
            for doc in docs:
                player_data = doc.to_dict()
                if player_data and 'jdl_id' in player_data:
                    # FirestoreのTimestampをdatetimeに変換
                    if 'last_updated_by_master' in player_data and isinstance(player_data['last_updated_by_master'], firestore.SERVER_TIMESTAMP.__class__):
                         # SERVER_TIMESTAMPはまだ書き込まれていない可能性があるのでNone扱いにするか、
                         # 書き込み後の取得を想定してエラーにするか。ここではNone扱い。
                         player_data['last_updated_by_master'] = None
                    elif 'last_updated_by_master' in player_data and isinstance(player_data['last_updated_by_master'], datetime):
                         pass # そのまま使う
                    elif 'last_updated_by_master' in player_data:
                         logger.warning(f"JDL ID {player_data['jdl_id']} の last_updated_by_master の型が不正です: {type(player_data['last_updated_by_master'])}。Noneとして扱います。")
                         player_data['last_updated_by_master'] = None


                    existing_players[player_data['jdl_id']] = {"id": doc.id, "data": player_data}
        except Exception as e:
            error_msg = f"Firestoreからのプレイヤーデータ取得中にエラーが発生しました: {e}"
            logger.exception(error_msg)
            errors.append(error_msg)
            return updated_count, skipped_count, errors # ここまでのエラーを返す

        # 3. 同期処理 (バッチ書き込みを使用)
        batch = self.db.batch()
        sync_time = datetime.now() # naive datetime

        for jdl_id, master_info in master_data.items():
            master_player_data = master_info["data"]
            master_last_updated = master_info["last_updated"] # aware or naive
            line_num = master_info["line_num"]

            if jdl_id in existing_players:
                existing_player_info = existing_players[jdl_id]
                existing_player_doc_id = existing_player_info["id"]
                existing_player_data = existing_player_info["data"]
                player_ref = self.players_ref.document(existing_player_doc_id)

                firestore_last_updated_by_master = existing_player_data.get("last_updated_by_master") # aware or naive or None

                should_update = True
                if firestore_last_updated_by_master and isinstance(firestore_last_updated_by_master, datetime):
                    # タイムゾーン情報の有無を考慮した比較
                    master_is_aware = master_last_updated.tzinfo is not None and master_last_updated.tzinfo.utcoffset(master_last_updated) is not None
                    firestore_is_aware = firestore_last_updated_by_master.tzinfo is not None and firestore_last_updated_by_master.tzinfo.utcoffset(firestore_last_updated_by_master) is not None

                    try:
                        if master_is_aware and firestore_is_aware:
                            # 両方awareならそのまま比較
                            if firestore_last_updated_by_master >= master_last_updated:
                                should_update = False
                        elif not master_is_aware and not firestore_is_aware:
                            # 両方naiveならそのまま比較 (UTC前提)
                             if firestore_last_updated_by_master >= master_last_updated:
                                should_update = False
                        else:
                            # awareとnaiveの比較は危険なため、ログを出して更新する
                            logger.warning(f"JDL ID {jdl_id}: last_updated_by_master のタイムゾーン情報が一致しません (Master: {master_is_aware}, Firestore: {firestore_is_aware})。強制的に更新します。")

                    except TypeError as e:
                         logger.error(f"JDL ID {jdl_id}: 日時比較エラー - {e}。強制的に更新します。")


                if not should_update:
                     logger.info(f"CSV L{line_num}: JDL ID {jdl_id} は既に最新のためスキップします。")
                     skipped_count += 1
                     continue # 次のJDL IDへ

                # 更新実行
                update_data = {
                    "name": master_player_data.name,
                    "participation_count": master_player_data.participation_count,
                    "current_class": master_player_data.current_class,
                    "last_updated_by_master": master_last_updated, # aware or naive
                    "updated_at": sync_time # naive datetime (FirestoreはUTCで保存)
                }
                batch.update(player_ref, update_data)
                updated_count += 1
                logger.info(f"CSV L{line_num}: JDL ID {jdl_id} のデータを更新対象に追加します。")

            else:
                logger.warning(f"CSV L{line_num}: JDL ID {jdl_id} はシステムに存在しません。スキップします。")
                skipped_count += 1

        # 4. バッチ書き込みを実行
        try:
            if updated_count > 0:
                commit_results = batch.commit()
                logger.info(f"{len(commit_results)}件の書き込み操作が完了しました ({updated_count}プレイヤー)。")
                # commit_results の内容を確認して詳細なログを出すことも可能
            else:
                logger.info("更新対象のプレイヤーデータはありませんでした。")
        except Exception as e:
            error_msg = f"Firestoreへのバッチ書き込み中にエラーが発生しました: {e}"
            logger.exception(error_msg)
            errors.append(error_msg)
            # エラーが発生した場合、更新数は0に戻す
            updated_count = 0

        return updated_count, skipped_count, errors
