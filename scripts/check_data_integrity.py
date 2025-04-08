#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
データ整合性チェックスクリプト

Firestoreデータベース内のデータの整合性をチェックし、
問題が見つかった場合は管理者にメールで通知します。

実行方法:
  python scripts/check_data_integrity.py [--admin-email admin@example.com]

引数:
  --admin-email: 通知先の管理者メールアドレス (任意、環境変数 ADMIN_EMAIL でも設定可能)
"""

import argparse
import asyncio
import logging
import os
import sys
import json
from dotenv import load_dotenv

# プロジェクトルートをsys.pathに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# backend/app 内のモジュールをインポート可能にする
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
     sys.path.insert(0, backend_path)

# .envファイルから環境変数を読み込む
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print(f".env ファイルを読み込みました: {dotenv_path}")
else:
    print(f".env ファイルが見つかりません: {dotenv_path}")

# 必要なモジュールをインポート
try:
    from app.services.data_integrity_service import DataIntegrityService
    from app.utils.notifications import send_email_notification
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
except ImportError as e:
    print(f"必要なモジュールのインポートに失敗しました: {e}", file=sys.stderr)
    print("PYTHONPATH:", sys.path, file=sys.stderr)
    sys.exit(1)

async def main(admin_email: str):
    """整合性チェックのメイン関数"""
    logger.info("データ整合性チェックを開始します...")

    try:
        integrity_service = DataIntegrityService()
        check_results = integrity_service.run_all_checks()
    except Exception as e:
        logger.exception(f"データ整合性チェックサービスの初期化または実行中にエラーが発生しました: {e}")
        # エラー発生時も通知を試みる
        if admin_email:
            subject = "[JDL Constractor] データ整合性チェックエラー"
            body = f"データ整合性チェックの実行中にエラーが発生しました。\n\nエラー:\n{e}"
            try:
                # メール送信設定の確認
                required_env_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'FROM_EMAIL']
                missing_vars = [var for var in required_env_vars if not os.getenv(var)]
                if missing_vars:
                    logger.error(f"メール送信に必要な環境変数が設定されていません: {', '.join(missing_vars)}")
                else:
                    await send_email_notification(admin_email, subject, body)
                    logger.info("エラー発生について管理者にメール通知しました。")
            except Exception as mail_err:
                logger.error(f"管理者へのエラー通知メール送信中にさらにエラーが発生しました: {mail_err}")
        sys.exit(1) # エラーで終了

    inconsistencies_found = False
    report_body = "データ整合性チェックの結果:\n\n"

    for check_name, results in check_results.items():
        report_body += f"--- {check_name} ---\n"
        if results:
            # エラーが発生した場合の表示
            if isinstance(results[0], dict) and "error" in results[0]:
                 report_body += f"エラーが発生しました: {results[0]['error']}\n"
                 inconsistencies_found = True # エラーも問題として扱う
            else:
                 inconsistencies_found = True
                 report_body += f"検出された問題 ({len(results)}件):\n"
                 # 結果を整形して表示 (例: JSON形式)
                 for item in results:
                     # datetimeオブジェクトなどを安全にシリアライズ
                     report_body += f"- {json.dumps(item, ensure_ascii=False, default=str)}\n"
        else:
            report_body += "問題は見つかりませんでした。\n"
        report_body += "\n"

    logger.info("データ整合性チェックが完了しました。")
    print(report_body) # コンソールにも結果を表示

    # 問題が見つかった場合のみ管理者に通知
    if inconsistencies_found and admin_email:
        logger.info(f"データの不整合が見つかったため、管理者にメール通知を試みます: {admin_email}")
        subject = "[JDL Constractor] データ整合性チェック結果（要確認）"
        try:
            # メール送信に必要な環境変数が設定されているか確認 (syncスクリプトと同様)
            required_env_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'FROM_EMAIL']
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            if missing_vars:
                logger.error(f"メール送信に必要な環境変数が設定されていません: {', '.join(missing_vars)}")
                raise ValueError("メール設定が不十分です。")

            await send_email_notification(admin_email, subject, report_body)
            logger.info("管理者へのメール通知が完了しました。")
        except Exception as e:
            logger.error(f"管理者へのメール通知中にエラーが発生しました: {e}")
    elif not inconsistencies_found:
         logger.info("データの不整合は見つかりませんでした。通知は行いません。")
    elif not admin_email:
        logger.warning("データの不整合が見つかりましたが、管理者メールアドレスが設定されていないため、通知メールは送信されませんでした。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="データ整合性チェックスクリプト")
    parser.add_argument("--admin-email", help="通知先の管理者メールアドレス (環境変数 ADMIN_EMAIL でも設定可能)")

    args = parser.parse_args()

    admin_email_address = args.admin_email or os.getenv("ADMIN_EMAIL")
    logger.info(f"管理者メールアドレス: {admin_email_address if admin_email_address else '未設定'}")

    try:
        asyncio.run(main(admin_email_address))
        logger.info("スクリプト実行完了。")
    except Exception as e:
        logger.exception(f"スクリプト実行中に予期せぬエラーが発生しました: {e}")
        sys.exit(1)
