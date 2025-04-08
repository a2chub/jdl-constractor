// frontend/src/types/user.ts

/**
 * バックエンドAPIからのユーザーレスポンスモデル。
 * adminルーターでの使用状況と一般的な属性に基づいています。
 * 実際のバックエンド UserResponse モデルとの照合が必要です。
 */
export interface UserResponse {
  id: string;
  name: string;
  email: string;
  is_admin?: boolean; // 管理者フラグ (オプショナルまたは必須)
  is_locked?: boolean; // ロック状態 (オプショナルまたは必須)
  created_at?: string | null; // ISO 8601 文字列または null
  updated_at?: string | null; // ISO 8601 文字列または null
  // 他のフィールドがあれば追加 (例: photo_url, last_login)
}

// 他のユーザー関連の型定義が必要であればここに追加
// export interface UserProfileUpdate { ... }
