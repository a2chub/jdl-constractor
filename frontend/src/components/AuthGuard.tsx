/**
 * 認証状態に基づいてルーティングを制御するコンポーネント
 * 
 * このコンポーネントは以下の機能を提供します：
 * - 認証が必要なルートの保護
 * - 未認証ユーザーのリダイレクト
 * - ローディング中の表示制御
 */

import { type ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LoadingSpinner } from './LoadingSpinner';

interface AuthGuardProps {
  /** 保護するコンポーネント */
  children: ReactNode;
  /** リダイレクト先のパス（デフォルト: /login） */
  redirectTo?: string;
}

/**
 * 認証ガードコンポーネント
 * @param props AuthGuardProps
 * @returns JSX.Element
 */
export const AuthGuard = ({
  children,
  redirectTo = '/login',
}: AuthGuardProps): JSX.Element => {
  const { user, loading } = useAuth();

  // ローディング中はスピナーを表示
  if (loading) {
    return <LoadingSpinner />;
  }

  // 未認証の場合はリダイレクト
  if (!user) {
    return <Navigate to={redirectTo} replace />;
  }

  // 認証済みの場合は子コンポーネントを表示
  return <>{children}</>;
}; 