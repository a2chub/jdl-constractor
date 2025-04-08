/**
 * チーム詳細コンポーネント
 * 
 * このコンポーネントは以下の機能を提供します：
 * - チームの詳細情報の表示
 * - チーム情報の編集（管理者のみ）
 * - メンバー一覧の表示
 * - ローディング状態の表示
 * - エラー状態の表示
 */

import { FC, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LoadingSpinner } from '../LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage';
import { useAuth } from '../../hooks/useAuth';

interface TeamMember {
  id: string;
  name: string;
  jdl_id: string;
  joined_at: string;
}

interface Team {
  id: string;
  name: string;
  description: string;
  logo_url: string;
  manager_id: string;
  status: string;
  members: TeamMember[];
}

export const TeamDetail: FC = () => {
  const { teamId } = useParams<{ teamId: string }>();
  const [team, setTeam] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    const fetchTeamDetail = async () => {
      try {
        const response = await fetch(`/api/teams/${teamId}`);
        if (!response.ok) {
          throw new Error('チーム情報の取得に失敗しました');
        }
        const data = await response.json();
        setTeam(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    fetchTeamDetail();
  }, [teamId]);

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

  if (!team) {
    return <ErrorMessage message="チームが見つかりません" />;
  }

  const isTeamManager = user && user.uid === team.manager_id;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="relative h-48 md:h-64">
          <img
            src={team.logo_url || '/default-team-logo.png'}
            alt={`${team.name}のロゴ`}
            className="w-full h-full object-cover"
          />
          {isTeamManager && (
            <button
              onClick={() => navigate(`/teams/${team.id}/edit`)}
              className="absolute top-4 right-4 bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-800 font-medium py-2 px-4 rounded-md shadow-md transition-all duration-200"
            >
              編集
            </button>
          )}
        </div>

        <div className="p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{team.name}</h1>
          <p className="text-gray-600 mb-6">{team.description}</p>

          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              メンバー一覧
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {team.members?.map((member) => (
                <div
                  key={member.id}
                  className="bg-gray-50 rounded-lg p-4"
                >
                  <h3 className="font-medium text-gray-900">{member.name}</h3>
                  <p className="text-sm text-gray-600">JDL ID: {member.jdl_id}</p>
                  <p className="text-sm text-gray-500">
                    加入日: {new Date(member.joined_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>

            {(!team.members || team.members.length === 0) && (
              <p className="text-gray-600 text-center py-4">
                メンバーが登録されていません
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 flex justify-center">
        <button
          onClick={() => navigate('/teams')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-6 rounded-md transition-colors duration-200"
        >
          チーム一覧に戻る
        </button>
      </div>
    </div>
  );
}; 