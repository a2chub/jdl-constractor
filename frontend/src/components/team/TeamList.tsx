/**
 * チーム一覧コンポーネント
 * 
 * このコンポーネントは以下の機能を提供します：
 * - チームの一覧表示
 * - チーム作成ボタン（管理者のみ）
 * - チーム詳細へのリンク
 * - ローディング状態の表示
 * - エラー状態の表示
 */

import { FC, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LoadingSpinner } from '../LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage';
import { useAuth } from '../../hooks/useAuth';

interface Team {
  id: string;
  name: string;
  description: string;
  logo_url: string;
  manager_id: string;
  status: string;
}

export const TeamList: FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await fetch('/api/teams');
        if (!response.ok) {
          throw new Error('チームの取得に失敗しました');
        }
        const data = await response.json();
        setTeams(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">チーム一覧</h1>
        {user && (
          <button
            onClick={() => navigate('/teams/new')}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
          >
            チームを作成
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {teams.map((team) => (
          <div
            key={team.id}
            className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200"
          >
            <div className="aspect-w-16 aspect-h-9">
              <img
                src={team.logo_url || '/default-team-logo.png'}
                alt={`${team.name}のロゴ`}
                className="object-cover w-full h-full"
              />
            </div>
            <div className="p-4">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {team.name}
              </h2>
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                {team.description}
              </p>
              <button
                onClick={() => navigate(`/teams/${team.id}`)}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-4 rounded-md transition-colors duration-200"
              >
                詳細を見る
              </button>
            </div>
          </div>
        ))}
      </div>

      {teams.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600">
            チームが登録されていません。新しいチームを作成してください。
          </p>
        </div>
      )}
    </div>
  );
}; 