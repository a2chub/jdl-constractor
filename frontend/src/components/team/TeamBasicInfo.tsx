import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { Team } from '../../types/team';
import { LoadingSpinner } from '../LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage';

/**
 * チームの基本情報を表示するコンポーネント
 * @param {Object} props - コンポーネントのプロパティ
 * @param {string} props.teamId - チームID
 */
interface TeamBasicInfoProps {
  teamId: string;
}

const TeamBasicInfo: React.FC<TeamBasicInfoProps> = ({ teamId }) => {
  const [team, setTeam] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTeam = async () => {
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

    fetchTeam();
  }, [teamId]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!team) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h2">
          {team.name}
        </Typography>
        <Typography color="textSecondary">
          作成日: {new Date(team.createdAt).toLocaleDateString()}
        </Typography>
        <Typography variant="body2" component="p">
          {team.description}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default TeamBasicInfo; 