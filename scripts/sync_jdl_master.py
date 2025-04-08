#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JDL IDマスターデータ同期スクリプト

CSVファイルからプレイヤーデータを読み込み、Firestoreのデータを更新します。
エラーが発生した場合は管理者にメールで通知します。

実行方法:
  python scripts/sync_jdl_master.py <csv_file_path> [--admin-email admin@example.com]

引数:
  csv_file_path: 同期するCSVファイルのパス (必須)
  --admin-email: エラー通知先の管理者メールアドレス (任意、環境変数 ADMIN_EMAIL でも設定可能)
"""

import argparse
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# プロジェクトルートをsys.pathに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# backend/app 内のモジュールをインポート可能にする
# backend ディレクトリ自体をパスに追加
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
     sys.path.insert(0, backend_path)


# .envファイルから環境変数を読み込む (存在する場合)
# .envファイルはプロジェクトルートにあると仮定
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print(f".env ファイルを読み込みました: {dotenv_path}") # デバッグ用
else:
    print(f".env ファイルが見つかりません: {dotenv_path}") # デバッグ用


# 必要なモジュールをインポート
try:
    # backend.app ではなく app からインポートを試みる (PYTHONPATHが通っている前提)
    from app.services.jdl_master_sync_service import JdlMasterSyncService
    from app.utils.notifications import send_email_notification
    # ロガー設定 (app.utils.logger があればそれを使うのが望ましい)
    # from app.utils.logger import get_logger
    # logger = get_logger(__name__)
    # ない場合は basicConfig を使用
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
except ImportError as e:
    print(f"必要なモジュールのインポートに失敗しました: {e}", file=sys.stderr)
    print("PYTHONPATH:", sys.path, file=sys.stderr)
    # 環境変数の確認 (デバッグ用)
    print("ADMIN_EMAIL from env:", os.getenv("ADMIN_EMAIL"), file=sys.stderr)
    print("SMTP_SERVER from env:", os.getenv("SMTP_SERVER"), file=sys.stderr)
    sys.exit(1)


async def main(csv_path: str, admin_email: str):
    """同期処理のメイン関数"""
    logger.info(f"JDLマスターデータ同期を開始します: {csv_path}")

    # Firestoreクライアントの初期化を確認 (サービス内で初期化されるはず)
    # logger.info("Firestoreクライアントを初期化します...") # 不要かも

    sync_service = JdlMasterSyncService()
    updated_count, skipped_count, errors = sync_service.sync_from_csv(csv_path)

    logger.info(f"同期処理完了: 更新={updated_count}, スキップ={skipped_count}")

    if errors:
        logger.error("同期中に以下のエラーが発生しました:")
        for error in errors:
            logger.error(f"- {error}")

        # 管理者へのメール通知
        if admin_email:
            logger.info(f"エラーが発生したため、管理者にメール通知を試みます: {admin_email}")
            subject = "[JDL Constractor] JDLマスター同期エラー通知"
            body = f"JDLマスターデータの同期処理中にエラーが発生しました。\n\n"
            body += f"ファイル: {os.path.basename(csv_path)}\n"
            body += f"更新成功: {updated_count}件\n"
            body += f"スキップ: {skipped_count}件\n"
            body += f"エラー件数: {len(errors)}件\n\n"
            body += "エラー詳細:\n"
            body += "\n".join([f"- {e}" for e in errors])

            try:
                # メール送信に必要な環境変数が設定されているか確認
                required_env_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'FROM_EMAIL']
                missing_vars = [var for var in required_env_vars if not os.getenv(var)]
                if missing_vars:
                    logger.error(f"メール送信に必要な環境変数が設定されていません: {', '.join(missing_vars)}")
                    raise ValueError("メール設定が不十分です。")

                # send_email_notification は async 関数なので await する
                await send_email_notification(admin_email, subject, body)
                logger.info("管理者へのメール通知が完了しました。")
            except Exception as e:
                logger.error(f"管理者へのメール通知中にエラーが発生しました: {e}")
        else:
            logger.warning("管理者メールアドレスが設定されていないため、エラー通知メールは送信されませんでした。")
    else:
        logger.info("同期処理はエラーなく完了しました。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JDLマスターデータ同期スクリプト")
    parser.add_argument("csv_file_path", help="同期するCSVファイルのパス")
    parser.add_argument("--admin-email", help="エラー通知先の管理者メールアドレス (環境変数 ADMIN_EMAIL でも設定可能)")

    args = parser.parse_args()

    # 環境変数または引数から管理者メールアドレスを取得
    admin_email_address = args.admin_email or os.getenv("ADMIN_EMAIL")
    logger.info(f"管理者メールアドレス: {admin_email_address if admin_email_address else '未設定'}")

    # asyncioを使用して非同期関数を実行
    try:
        # Python 3.7+
        asyncio.run(main(args.csv_file_path, admin_email_address))
        logger.info("スクリプト実行完了。")
    except FileNotFoundError:
         logger.error(f"指定されたCSVファイルが見つかりません: {args.csv_file_path}")
         sys.exit(1)
    except ImportError as e:
         # main関数内で再度ImportErrorが発生する可能性は低いが念のため
         logger.critical(f"モジュールのインポートに失敗しました。環境を確認してください: {e}")
         sys.exit(1)
    except Exception as e:
         logger.exception(f"スクリプト実行中に予期せぬエラーが発生しました: {e}")
         sys.exit(1)
