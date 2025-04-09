import React, { useEffect, useState } from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { TeamMember } from '../../types/team';
import { LoadingSpinner } from '../LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage';

/**
 * チームメンバーリストを表示するコンポーネント
 * @param {Object} props - コンポーネントのプロパティ
 * @param {string} props.teamId - チームID
 */
interface TeamMemberListProps {
  teamId: string;
}

const TeamMemberList: React.FC<TeamMemberListProps> = ({ teamId }) => {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const response = await fetch(`/api/teams/${teamId}/members`);
        if (!response.ok) {
          throw new Error('メンバー情報の取得に失敗しました');
        }
        const data = await response.json();
        setMembers(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    fetchMembers();
  }, [teamId]);

  const handleRemoveMember = async (memberId: string) => {
    try {
      const response = await fetch(`/api/teams/${teamId}/members/${memberId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('メンバーの削除に失敗しました');
      }
      setMembers(members.filter(member => member.id !== memberId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        メンバー一覧
      </Typography>
      {members.length > 0 ? (
        <List>
          {members.map((member) => (
            <ListItem key={member.id}>
              <ListItemText
                primary={member.name}
                secondary={member.role}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => handleRemoveMember(member.id)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography color="textSecondary">
          メンバーが登録されていません。
        </Typography>
      )}
    </div>
  );
};

export default TeamMemberList; 