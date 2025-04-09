/**
 * チームメンバーの型定義
 */
export interface TeamMember {
  id: string;
  name: string;
  role: string;
  joinedAt: string;
}

/**
 * チームの型定義
 */
export interface Team {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  members: TeamMember[];
}

/**
 * チーム権限の型定義
 */
export interface TeamPermission {
  id: string;
  teamId: string;
  userId: string;
  role: string;
  grantedAt: string;
  grantedBy: string;
} 