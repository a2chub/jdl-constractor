// vitest 用のテストセットアップファイル
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Firebase Auth functions globally
vi.mock('firebase/auth', () => ({
    // Explicitly return mocked functions
    getAuth: vi.fn(() => ({
      currentUser: {
        uid: 'mock-user-uid',
        email: 'mock@example.com',
        getIdToken: async () => 'mock-id-token-global',
        getIdTokenResult: async () => ({
            claims: { admin: true }
        })
      }
    })),
    onAuthStateChanged: vi.fn((auth, callback) => {
      const mockUser = {
        uid: 'mock-user-uid',
        email: 'mock@example.com',
        getIdToken: async () => 'mock-id-token-global',
        getIdTokenResult: async () => ({
            claims: { admin: true }
        })
      };
      callback(mockUser);
      return vi.fn(); // unsubscribe function
    }),
    // Add mocks for other auth functions if they are used directly in the codebase
}));

// Mock initializeApp to prevent the "no app" error if it's called somewhere unexpected
vi.mock('firebase/app', () => ({
    initializeApp: vi.fn(),
    getApp: vi.fn(() => ({
        name: '[DEFAULT]',
        options: {},
    })),
    getApps: vi.fn(() => [{ name: '[DEFAULT]', options: {} }]),
}));
