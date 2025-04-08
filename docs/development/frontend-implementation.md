# フロントエンド実装仕様書

## 1. 状態管理

### 1.1 グローバル状態
```typescript
// src/store/auth.ts
import { create } from 'zustand';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: Error | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
}

const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  error: null,
  login: async () => {
    // 実装
  },
  logout: async () => {
    // 実装
  },
}));
```

### 1.2 キャッシュ戦略
```typescript
// src/lib/query-client.ts
import { QueryClient } from 'react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5分
      cacheTime: 30 * 60 * 1000, // 30分
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

## 2. コンポーネント設計

### 2.1 エラー表示
```typescript
// src/components/common/ErrorBoundary.tsx
import { ErrorBoundary } from 'react-error-boundary';

const ErrorFallback = ({ error, resetErrorBoundary }) => (
  <div role="alert" className="error-container">
    <h2>エラーが発生しました</h2>
    <pre>{error.message}</pre>
    <button onClick={resetErrorBoundary}>再試行</button>
  </div>
);

// 使用例
<ErrorBoundary FallbackComponent={ErrorFallback}>
  <ComponentThatMayError />
</ErrorBoundary>
```

### 2.2 ローディング表示
```typescript
// src/components/common/Loading.tsx
const Loading = () => (
  <div className="loading-container">
    <div className="loading-spinner" />
    <p>読み込み中...</p>
  </div>
);

// 使用例
const TeamList = () => {
  const { data, isLoading } = useQuery('teams', fetchTeams);
  
  if (isLoading) return <Loading />;
  return <div>{/* チーム一覧表示 */}</div>;
};
```

## 3. フォーム実装

### 3.1 バリデーション
```typescript
// src/lib/validation.ts
import * as z from 'zod';

export const teamSchema = z.object({
  name: z.string()
    .min(1, '必須項目です')
    .max(50, '50文字以内で入力してください'),
  description: z.string()
    .max(200, '200文字以内で入力してください')
    .optional(),
});

// src/components/team/TeamForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const TeamForm = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(teamSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      {errors.name && <span>{errors.name.message}</span>}
      {/* その他のフィールド */}
    </form>
  );
};
```

## 4. API通信

### 4.1 APIクライアント
```typescript
// src/lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 5000,
});

apiClient.interceptors.request.use(async (config) => {
  const token = await getFirebaseToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 認証エラー処理
    }
    return Promise.reject(error);
  }
);
```

### 4.2 APIフック
```typescript
// src/hooks/useTeams.ts
import { useQuery, useMutation } from 'react-query';

export const useTeams = () => {
  return useQuery('teams', () => 
    apiClient.get('/teams').then(res => res.data)
  );
};

export const useCreateTeam = () => {
  return useMutation(
    (newTeam) => apiClient.post('/teams', newTeam),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('teams');
      },
    }
  );
};
```

## 5. エラーハンドリング

### 5.1 グローバルエラーハンドリング
```typescript
// src/lib/error-handler.ts
export const handleGlobalError = (error: Error) => {
  if (error.name === 'NetworkError') {
    // ネットワークエラー処理
    showToast('ネットワークエラーが発生しました');
  } else if (error.name === 'AuthError') {
    // 認証エラー処理
    redirectToLogin();
  } else {
    // その他のエラー
    showToast('予期せぬエラーが発生しました');
  }
};

// _app.tsxでの設定
window.onerror = (message, source, lineno, colno, error) => {
  handleGlobalError(error);
};
```

### 5.2 コンポーネントレベルのエラー処理
```typescript
const TeamList = () => {
  const { data, error, isError } = useQuery('teams', fetchTeams);

  if (isError) {
    return (
      <div className="error-message">
        <p>チーム情報の取得に失敗しました</p>
        <button onClick={() => queryClient.invalidateQueries('teams')}>
          再試行
        </button>
      </div>
    );
  }

  return <div>{/* チーム一覧表示 */}</div>;
};
``` 