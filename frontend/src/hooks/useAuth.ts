/**
 * 認証状態を管理するカスタムフック
 * 
 * このフックは以下の機能を提供します：
 * - Firebase Authenticationを使用したユーザー認証状態の管理
 * - ログイン/ログアウト機能
 * - ユーザー情報の取得
 * - ローディング状態の管理
 */

import { useState, useEffect } from 'react';
import { 
  getAuth, 
  signInWithPopup, 
  GoogleAuthProvider, 
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User
} from 'firebase/auth';

interface AuthState {
  /** 現在のユーザー情報 */
  user: User | null;
  /** ローディング状態 */
  loading: boolean;
  /** エラー情報 */
  error: Error | null;
}

/**
 * 認証状態を管理するカスタムフック
 * @returns AuthState & 認証関連の関数
 */
export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(
      auth,
      (user) => {
        setAuthState((prev) => ({
          ...prev,
          user,
          loading: false,
          error: null,
        }));
      },
      (error) => {
        setAuthState((prev) => ({
          ...prev,
          error: error as Error,
          loading: false,
        }));
      }
    );

    return () => unsubscribe();
  }, []);

  /**
   * Googleアカウントでログインする
   */
  const signIn = async () => {
    try {
      setAuthState((prev) => ({ ...prev, loading: true, error: null }));
      const auth = getAuth();
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    } catch (error) {
      setAuthState((prev) => ({
        ...prev,
        error: error as Error,
        loading: false,
      }));
    }
  };

  /**
   * ログアウトする
   */
  const signOut = async () => {
    try {
      setAuthState((prev) => ({ ...prev, loading: true, error: null }));
      const auth = getAuth();
      await firebaseSignOut(auth);
    } catch (error) {
      setAuthState((prev) => ({
        ...prev,
        error: error as Error,
        loading: false,
      }));
    }
  };

  return {
    ...authState,
    signIn,
    signOut,
  };
}; 