// frontend/src/types/admin.ts

/**
 * 管理者ダッシュボードのサマリーデータ型
 * バックエンドの /admin/dashboard/summary のレスポンスに対応
 */
export interface AdminDashboardSummary {
  users_count: number;
  teams_count: number;
  players_count: number;
  tournaments_count: number;
  // 必要に応じて他のサマリー情報を追加
  // active_tournaments_count?: number;
}

// 他の管理者関連の型定義をここに追加
// 例: システム設定の型
// export interface SystemSettings {
//   setting_key: string;
//   value: any;
// }
