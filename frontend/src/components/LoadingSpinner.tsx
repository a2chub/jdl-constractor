/**
 * ローディングスピナーコンポーネント
 * 
 * このコンポーネントは以下の機能を提供します：
 * - カスタマイズ可能なサイズとカラーのスピナーアニメーション
 * - アクセシビリティ対応（aria-label付き）
 */

import { FC } from 'react';

interface LoadingSpinnerProps {
  /**
   * スピナーのサイズ（ピクセル）
   */
  size?: number;
  
  /**
   * スピナーの色
   */
  color?: string;
}

/**
 * ローディング中を表示するスピナーコンポーネント
 */
export const LoadingSpinner: FC<LoadingSpinnerProps> = ({ 
  size = 24, 
  color = '#4F46E5' 
}) => {
  return (
    <div
      style={{ width: size, height: size }}
      className="animate-spin"
      role="status"
      aria-label="読み込み中"
    >
      <svg
        className="w-full h-full"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke={color}
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill={color}
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
}; 