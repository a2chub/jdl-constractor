/**
 * 認証状態を管理するためのコンテキスト
 * 
 * このコンテキストは以下の機能を提供します：
 * - ユーザーの認証状態の管理
 * - ログイン・ログアウト機能
 * - 認証状態の変更監視
 * - ユーザー情報の提供
 */

import { createContext, useContext, useEffect, useState, ReactNode, FC } from 'react';
import { 
  User,
  signInWithPopup,
  GoogleAuthProvider,
  signOut as firebaseSignOut,
  onAuthStateChanged
} from 'firebase/auth';
import { auth } from '../config/firebase';

interface AuthContextType {
  /** 現在のユーザー情報 */
  currentUser: User | null;
  /** ログイン処理中かどうか */
  loading: boolean;
  /** Googleアカウントでログインする関数 */
  signInWithGoogle: () => Promise<void>;
  /** ログアウトする関数 */
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * 認証状態を提供するプロバイダーコンポーネント
 */
export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 認証状態の変更を監視
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setCurrentUser(user);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  /**
   * Googleアカウントでログインする
   */
  const signInWithGoogle = async (): Promise<void> => {
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error('Googleログインエラー:', error);
      throw error;
    }
  };

  /**
   * ログアウトする
   */
  const signOut = async (): Promise<void> => {
    try {
      await firebaseSignOut(auth);
    } catch (error) {
      console.error('ログアウトエラー:', error);
      throw error;
    }
  };

  const value = {
    currentUser,
    loading,
    signInWithGoogle,
    signOut,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * 認証コンテキストを使用するためのカスタムフック
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 