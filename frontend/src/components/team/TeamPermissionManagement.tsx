import React, { useState, useEffect } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Typography,
  Box,
} from '@mui/material';
import { TeamMember } from '../../types/team';
import { LoadingSpinner } from '../LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage';

/**
 * チームメンバーの権限管理コンポーネント
 * @param {Object} props - コンポーネントのプロパティ
 * @param {string} props.teamId - チームID
 */
interface TeamPermissionManagementProps {
  teamId: string;
}

const TeamPermissionManagement: React.FC<TeamPermissionManagementProps> = ({ teamId }) => {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [selectedMember, setSelectedMember] = useState<string>('');
  const [selectedRole, setSelectedRole] = useState<string>('');
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedMember && selectedRole) {
      try {
        const response = await fetch(`/api/teams/${teamId}/permissions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            memberId: selectedMember,
            role: selectedRole,
          }),
        });

        if (!response.ok) {
          throw new Error('権限の更新に失敗しました');
        }

        // メンバーリストを更新
        const updatedMembers = members.map(member =>
          member.id === selectedMember
            ? { ...member, role: selectedRole }
            : member
        );
        setMembers(updatedMembers);
        setSelectedMember('');
        setSelectedRole('');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'エラーが発生しました');
      }
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        権限管理
      </Typography>
      <form onSubmit={handleSubmit}>
        <FormControl fullWidth margin="normal">
          <InputLabel>メンバー</InputLabel>
          <Select
            value={selectedMember}
            onChange={(e) => setSelectedMember(e.target.value as string)}
          >
            {members.map((member) => (
              <MenuItem key={member.id} value={member.id}>
                {member.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl fullWidth margin="normal">
          <InputLabel>権限</InputLabel>
          <Select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value as string)}
          >
            <MenuItem value="admin">管理者</MenuItem>
            <MenuItem value="member">メンバー</MenuItem>
            <MenuItem value="viewer">閲覧者</MenuItem>
          </Select>
        </FormControl>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          disabled={!selectedMember || !selectedRole}
          sx={{ mt: 2 }}
        >
          権限を更新
        </Button>
      </form>
    </Box>
  );
};

export default TeamPermissionManagement; 