/**
 * チーム一覧コンポーネントのテスト
 */

import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TeamList } from '../TeamList';
import { useAuth } from '../../../hooks/useAuth';

// useAuthのモック
jest.mock('../../../hooks/useAuth');
const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

// fetchのモック
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('TeamList', () => {
  const mockTeams = [
    {
      id: '1',
      name: 'Test Team 1',
      description: 'Test Description 1',
      logo_url: 'http://example.com/logo1.png',
      manager_id: 'user1',
      status: 'active',
    },
    {
      id: '2',
      name: 'Test Team 2',
      description: 'Test Description 2',
      logo_url: 'http://example.com/logo2.png',
      manager_id: 'user2',
      status: 'active',
    },
  ];

  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      user: { uid: 'user1' },
      loading: false,
      error: null,
    });
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockTeams,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('チーム一覧を表示する', async () => {
    render(
      <MemoryRouter>
        <TeamList />
      </MemoryRouter>
    );

    // ローディング状態の確認
    expect(screen.getByRole('status')).toBeInTheDocument();

    // チーム一覧の表示を確認
    await waitFor(() => {
      expect(screen.getByText('Test Team 1')).toBeInTheDocument();
      expect(screen.getByText('Test Team 2')).toBeInTheDocument();
    });
  });

  it('エラー時にエラーメッセージを表示する', async () => {
    mockFetch.mockRejectedValue(new Error('Failed to fetch'));

    render(
      <MemoryRouter>
        <TeamList />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('エラーが発生しました')).toBeInTheDocument();
    });
  });

  it('チームが存在しない場合に適切なメッセージを表示する', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(
      <MemoryRouter>
        <TeamList />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(
        screen.getByText('チームが登録されていません。新しいチームを作成してください。')
      ).toBeInTheDocument();
    });
  });

  it('ログインユーザーにチーム作成ボタンを表示する', async () => {
    render(
      <MemoryRouter>
        <TeamList />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('チームを作成')).toBeInTheDocument();
    });
  });

  it('未ログインユーザーにチーム作成ボタンを表示しない', async () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      error: null,
    });

    render(
      <MemoryRouter>
        <TeamList />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.queryByText('チームを作成')).not.toBeInTheDocument();
    });
  });
}); 