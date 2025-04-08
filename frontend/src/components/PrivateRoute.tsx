/**
 * 認証状態に基づいてルーティングを制御するコンポーネント
 * 
 * このコンポーネントは以下の機能を提供します：
 * - 認証が必要なルートの保護
 * - 未認証ユーザーのリダイレクト
 * - ローディング中の表示制御
 */

import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../contexts/AuthContext';
import { LoadingSpinner } from './LoadingSpinner';

interface PrivateRouteProps {
  /** 保護されたコンテンツ */
  children: ReactNode;
  /** リダイレクト先のパス（デフォルト: /login） */
  redirectTo?: string;
}

/**
 * 認証状態に基づいてルーティングを制御するコンポーネント
 */
export const PrivateRoute = ({ 
  children, 
  redirectTo = '/login' 
}: PrivateRouteProps) => {
  const { user, loading } = useAuthContext();
  const location = useLocation();

  // ローディング中はスピナーを表示
  if (loading) {
    return <LoadingSpinner />;
  }

  // 未認証の場合はリダイレクト
  if (!user) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // 認証済みの場合は保護されたコンテンツを表示
  return <>{children}</>;
}; 