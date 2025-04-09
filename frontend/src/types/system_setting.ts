// frontend/src/types/system_setting.ts

/**
 * システム設定の基本情報（レスポンス、更新時などに使用）
 * バックエンドの SystemSettingBase に対応
 */
export interface SystemSettingBase {
  value: any; // 設定値の型は任意
  description?: string | null; // 説明 (オプショナル)
}

/**
 * システム設定のレスポンス型 (API GET /settings, /settings/{key} など)
 * バックエンドの SystemSettingResponse に対応
 */
export interface SystemSettingResponse extends SystemSettingBase {
  key: string; // 設定キー
  created_at?: string | null; // ISO 8601 形式の文字列 or null
  updated_at?: string | null; // ISO 8601 形式の文字列 or null
}

/**
 * システム設定の更新リクエスト型 (API PUT /settings/{key})
 * バックエンドの SystemSettingUpdate に対応
 */
export interface SystemSettingUpdate {
  value?: any; // 更新する値 (オプショナル)
  description?: string | null; // 更新する説明 (オプショナル)
  // updated_at はバックエンドで設定されるため、通常フロントからは送信しない
}

/**
 * システム設定の作成リクエスト型 (API POST /settings)
 * バックエンドの SystemSettingCreate に対応
 */
export interface SystemSettingCreate extends SystemSettingBase {
  key: string; // 作成する設定のキー
  // created_at, updated_at はバックエンドで設定されるため、通常フロントからは送信しない
}
