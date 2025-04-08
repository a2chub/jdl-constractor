/**
 * エラーメッセージコンポーネント
 * 
 * このコンポーネントは以下の機能を提供します：
 * - エラーメッセージの表示
 * - エラーの種類に応じたスタイリング
 * - アクセシビリティ対応（role="alert"付き）
 */

import { FC } from 'react';

interface ErrorMessageProps {
  /**
   * エラーメッセージの内容
   */
  message: string;
  
  /**
   * エラーの種類
   * - error: 重大なエラー（赤色）
   * - warning: 警告（黄色）
   */
  type?: 'error' | 'warning';
}

/**
 * エラーメッセージを表示するコンポーネント
 */
export const ErrorMessage: FC<ErrorMessageProps> = ({ 
  message, 
  type = 'error' 
}) => {
  const baseClasses = 'rounded-md p-4 mb-4 text-sm font-medium';
  const typeClasses = {
    error: 'bg-red-50 text-red-700 border border-red-200',
    warning: 'bg-yellow-50 text-yellow-700 border border-yellow-200'
  };

  return (
    <div 
      className={`${baseClasses} ${typeClasses[type]}`}
      role="alert"
    >
      <div className="flex items-center">
        {type === 'error' ? (
          <svg
            className="w-5 h-5 mr-2"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        ) : (
          <svg
            className="w-5 h-5 mr-2"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        )}
        {message}
      </div>
    </div>
  );
}; 