# backend/tests/test_jdl_master_sync.py
import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import os
import csv
from io import StringIO
from datetime import datetime, timezone, timedelta

# テスト対象のモジュールをインポートするためにパスを追加
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Pydanticモデルやサービスをインポート
try:
    from app.services.jdl_master_sync_service import JdlMasterSyncService
    from app.models.player import PlayerBase # 検証用
    # Firestoreのモックに必要なものをインポート (もし使うなら)
    # from google.cloud import firestore
except ImportError as e:
    print(f"テストに必要なモジュールのインポートに失敗: {e}")
    print("PYTHONPATH:", sys.path)
    # テスト実行前にエラーがわかるように例外を発生させるか、マークするなど
    raise

# --- テスト用のダミーデータ ---
VALID_CSV_DATA = """jdl_id,player_name,participation_count,current_class,last_updated
JDL000001,Player One,10,A,2025-04-09T10:00:00Z
JDL000002,Player Two,5,B,2025-04-09T11:00:00+09:00
JDL000003,Player Three Updated,15,C,2025-04-08T12:00:00Z
JDL000004,Player Four New,1,D,2025-04-09T00:00:00Z
"""

INVALID_CSV_DATA = """jdl_id,player_name,participation_count,current_class,last_updated
JDL000001,Player One,10,A,2025-04-09T10:00:00Z
JDLINVALID,Invalid Player,5,B,2025-04-09T11:00:00Z
JDL000003,Player Three,-5,C,2025-04-08T12:00:00Z
JDL000004,Player Four,1,X,2025-04-09T00:00:00Z
JDL000005,Player Five,,E,2025-04-09T01:00:00Z
JDL000006,Player Six,10,A,invalid-date
JDL000007,Player Seven,10,A,
"""

EMPTY_CSV_DATA = "jdl_id,player_name,participation_count,current_class,last_updated\n"

# Firestoreの既存データを模倣
# タイムゾーン付き(aware)とタイムゾーンなし(naive)のdatetimeを混在させる
UTC = timezone.utc
JST = timezone(timedelta(hours=9))

EXISTING_FIRESTORE_DATA = {
    "JDL000001": {"id": "doc1", "data": {"jdl_id": "JDL000001", "name": "Player One Old", "participation_count": 8, "current_class": "B", "last_updated_by_master": datetime(2025, 4, 8, 10, 0, 0, tzinfo=UTC)}}, # 更新されるべき (CSV: 2025-04-09 10:00 UTC)
    "JDL000002": {"id": "doc2", "data": {"jdl_id": "JDL000002", "name": "Player Two", "participation_count": 5, "current_class": "B", "last_updated_by_master": datetime(2025, 4, 9, 11, 0, 0, tzinfo=JST)}}, # 更新されない (CSV: 2025-04-09 11:00 JST と同じ)
    "JDL000003": {"id": "doc3", "data": {"jdl_id": "JDL000003", "name": "Player Three", "participation_count": 10, "current_class": "D", "last_updated_by_master": None}}, # 更新される (last_updated_by_masterがNone)
    "JDLEXISTING": {"id": "doc_existing", "data": {"jdl_id": "JDLEXISTING", "name": "Existing Only", "participation_count": 1, "current_class": "E"}} # CSVにないので影響なし
}

class TestJdlMasterSyncService(unittest.TestCase):

    def setUp(self):
        # Firestoreクライアントと関連メソッドをモック
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_batch = MagicMock()
        self.mock_db.collection.return_value = self.mock_collection
        self.mock_db.batch.return_value = self.mock_batch

        # Firestoreのstream()が返すイテレータをモックする関数
        def mock_stream():
            mock_docs = []
            for player_info in EXISTING_FIRESTORE_DATA.values():
                mock_doc = MagicMock()
                mock_doc.id = player_info["id"]
                # FirestoreのTimestamp型を模倣する場合
                # data = player_info["data"].copy()
                # if data.get("last_updated_by_master"):
                #     data["last_updated_by_master"] = Timestamp.from_datetime(data["last_updated_by_master"])
                # mock_doc.to_dict.return_value = data
                mock_doc.to_dict.return_value = player_info["data"]
                mock_docs.append(mock_doc)
            return iter(mock_docs)

        self.mock_collection.stream = mock_stream # 関数を割り当て

        # サービスインスタンス化 (モックDBを渡す)
        self.sync_service = JdlMasterSyncService(firestore_db=self.mock_db)


    @patch('builtins.open', new_callable=mock_open, read_data=VALID_CSV_DATA)
    @patch('app.services.jdl_master_sync_service.logger') # loggerもモック
    def test_sync_from_csv_success(self, mock_logger, mock_file):
        """正常系のテスト: 有効なCSVで正しく同期される"""
        updated_count, skipped_count, errors = self.sync_service.sync_from_csv("dummy/path/valid.csv")

        # 期待される結果
        expected_updated_count = 2 # JDL000001, JDL000003
        expected_skipped_count = 2 # JDL000002 (最新), JDL000004 (Firestoreにない)
        expected_errors = []

        self.assertEqual(updated_count, expected_updated_count)
        self.assertEqual(skipped_count, expected_skipped_count)
        self.assertEqual(errors, expected_errors)

        # Firestoreへの書き込み内容を確認
        self.assertEqual(self.mock_batch.update.call_count, expected_updated_count)
        self.mock_batch.commit.assert_called_once()

        # 更新内容の詳細を確認 (例: JDL000001)
        expected_update_data_jdl1 = {
            "name": "Player One",
            "participation_count": 10,
            "current_class": "A",
            "last_updated_by_master": datetime(2025, 4, 9, 10, 0, 0, tzinfo=timezone.utc),
            "updated_at": unittest.mock.ANY # datetime.now() はANYで比較
        }
        # batch.updateの呼び出し引数を取得して検証
        update_calls = self.mock_batch.update.call_args_list
        jdl1_call_found = False
        for call_args in update_calls:
            # call_args は ((doc_ref_mock, update_data), kwargs) の形式
            doc_ref_mock = call_args[0][0] # 第一引数はドキュメント参照のモック
            update_data = call_args[0][1] # 第二引数が更新データ
            # ドキュメント参照のIDが期待通りか確認 (setUpで設定したID)
            if hasattr(doc_ref_mock, 'id') and doc_ref_mock.id == EXISTING_FIRESTORE_DATA["JDL000001"]["id"]:
                 # updated_atを除いて比較
                 actual_updated_at = update_data.pop("updated_at")
                 expected_updated_at = expected_update_data_jdl1.pop("updated_at")
                 self.assertDictEqual(update_data, expected_update_data_jdl1)
                 # updated_atがdatetime型であることだけ確認
                 self.assertIsInstance(actual_updated_at, datetime)
                 jdl1_call_found = True
                 # 元に戻す（他のアサーションに影響しないように）
                 update_data["updated_at"] = actual_updated_at
                 expected_update_data_jdl1["updated_at"] = expected_updated_at
                 break
        self.assertTrue(jdl1_call_found, "JDL000001の更新呼び出しが見つかりません")


        # ログ出力の確認 (任意)
        # ANYは特定の呼び出しがあったかどうかの確認に便利
        mock_logger.info.assert_any_call("CSV L3: JDL ID JDL000002 は既に最新のためスキップします。") # 行番号修正
        mock_logger.warning.assert_any_call("CSV L5: JDL ID JDL000004 はシステムに存在しません。スキップします。") # 行番号修正
        mock_logger.info.assert_any_call(f"{expected_updated_count}件の書き込み操作が完了しました ({expected_updated_count}プレイヤー)。")


    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('app.services.jdl_master_sync_service.logger')
    def test_sync_from_csv_file_not_found(self, mock_logger, mock_file):
        """ファイルが見つからない場合のテスト"""
        updated_count, skipped_count, errors = self.sync_service.sync_from_csv("dummy/path/nonexistent.csv")

        self.assertEqual(updated_count, 0)
        self.assertEqual(skipped_count, 0)
        self.assertTrue(len(errors) == 1)
        self.assertIn("CSVファイルが見つかりません", errors[0])
        mock_logger.error.assert_called_with("CSVファイルが見つかりません: dummy/path/nonexistent.csv")
        self.mock_batch.commit.assert_not_called()

    @patch('builtins.open', new_callable=mock_open, read_data=INVALID_CSV_DATA)
    @patch('app.services.jdl_master_sync_service.logger')
    def test_sync_from_csv_invalid_data(self, mock_logger, mock_file):
        """無効なデータを含むCSVのテスト"""
        updated_count, skipped_count, errors = self.sync_service.sync_from_csv("dummy/path/invalid.csv")

        # JDL000001は有効なので更新される
        # 他の行は検証エラーでスキップされる
        expected_updated_count = 1 # JDL000001のみ
        expected_skipped_count = 6 # 無効な6行
        self.assertEqual(updated_count, expected_updated_count)
        self.assertEqual(skipped_count, expected_skipped_count)
        self.assertEqual(len(errors), expected_skipped_count) # エラー数とスキップ数が一致

        # エラー内容の確認 (一部)
        self.assertTrue(any("JDL IDは" in e for e in errors if "L3" in e)) # JDLINVALID 行番号確認
        self.assertTrue(any("participation_count" in e for e in errors if "L4" in e)) # -5 行番号確認
        self.assertTrue(any("クラスはA, B, C, D, E" in e for e in errors if "L5" in e)) # X 行番号確認
        self.assertTrue(any("participation_count" in e for e in errors if "L6" in e)) # 空文字 行番号確認
        self.assertTrue(any("日付形式が無効です" in e for e in errors if "L7" in e)) # invalid-date 行番号確認
        self.assertTrue(any("last_updated フィールドが存在しません" in e for e in errors if "L8" in e)) # 空文字 行番号確認

        self.assertEqual(self.mock_batch.update.call_count, expected_updated_count)
        self.mock_batch.commit.assert_called_once()
        self.assertTrue(mock_logger.error.call_count >= expected_skipped_count) # エラーログが出力されているはず

    @patch('builtins.open', new_callable=mock_open, read_data=EMPTY_CSV_DATA)
    @patch('app.services.jdl_master_sync_service.logger')
    def test_sync_from_csv_empty_data(self, mock_logger, mock_file):
        """空のCSVデータ（ヘッダーのみ）のテスト"""
        updated_count, skipped_count, errors = self.sync_service.sync_from_csv("dummy/path/empty.csv")

        self.assertEqual(updated_count, 0)
        self.assertEqual(skipped_count, 0)
        self.assertEqual(errors, [])
        mock_logger.warning.assert_called_with("CSVファイルから有効なデータが読み込めませんでした。")
        self.mock_batch.commit.assert_not_called() # 更新がないのでcommitは呼ばれない

    @patch('builtins.open', new_callable=mock_open, read_data=VALID_CSV_DATA)
    @patch('app.services.jdl_master_sync_service.logger')
    def test_sync_firestore_read_error(self, mock_logger, mock_file):
        """Firestoreからの読み込みエラーテスト"""
        # streamでエラーを発生させるように再設定
        self.mock_collection.stream = MagicMock(side_effect=Exception("Firestore read failed"))

        updated_count, skipped_count, errors = self.sync_service.sync_from_csv("dummy/path/valid.csv")

        self.assertEqual(updated_count, 0)
        # CSVの読み込みは成功しているので、skipped_countはCSV検証時のもの
        self.assertEqual(skipped_count, 0) # VALID_CSVは検証エラーなし
        self.assertTrue(len(errors) == 1)
        self.assertIn("Firestoreからのプレイヤーデータ取得中にエラーが発生しました", errors[0])
        mock_logger.exception.assert_called_with("Firestoreからのプレイヤーデータ取得中にエラーが発生しました: Firestore read failed")
        self.mock_batch.commit.assert_not_called()

    @patch('builtins.open', new_callable=mock_open, read_data=VALID_CSV_DATA)
    @patch('app.services.jdl_master_sync_service.logger')
    def test_sync_firestore_write_error(self, mock_logger, mock_file):
        """Firestoreへの書き込みエラーテスト"""
        self.mock_batch.commit.side_effect = Exception("Firestore write failed")

        updated_count, skipped_count, errors = self.sync_service.sync_from_csv("dummy/path/valid.csv")

        # 更新処理自体は試みられるが、commitで失敗する
        expected_updated_attempted = 2 # JDL000001, JDL000003
        expected_skipped_count = 2 # JDL000002, JDL000004

        self.assertEqual(updated_count, 0) # commit失敗したので0になる
        self.assertEqual(skipped_count, expected_skipped_count)
        self.assertTrue(len(errors) == 1)
        self.assertIn("Firestoreへのバッチ書き込み中にエラーが発生しました", errors[0])
        mock_logger.exception.assert_called_with("Firestoreへのバッチ書き込み中にエラーが発生しました: Firestore write failed")
        # commitは呼び出されるが、例外が発生する
        self.mock_batch.commit.assert_called_once()


if __name__ == '__main__':
    # unittest.main() を直接呼び出すと引数処理で問題が起きることがある
    # テストランナー経由での実行を推奨 (e.g., python -m unittest backend/tests/test_jdl_master_sync.py)
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestJdlMasterSyncService))
    runner = unittest.TextTestRunner()
    runner.run(suite)
