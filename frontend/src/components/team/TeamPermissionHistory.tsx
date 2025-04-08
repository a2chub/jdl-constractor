/**
 * チーム権限の変更履歴を表示するコンポーネント
 *
 * このコンポーネントは以下の機能を提供します：
 * - 権限変更履歴の一覧表示
 * - チームまたはユーザーによるフィルタリング
 * - ページネーション
 */

import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Typography,
  Pagination,
  Alert,
  Chip,
} from '@mui/material';
import { useAuth } from '../../hooks/useAuth';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';

interface PermissionHistory {
  id: string;
  team_id: string;
  user_id: string;
  role: string;
  action: string;
  changed_by: string;
  changed_at: string;
  reason?: string;
}

interface PermissionHistoryListResponse {
  items: PermissionHistory[];
  total: number;
}

interface TeamPermissionHistoryProps {
  teamId?: string;
  userId?: string;
}

const actionLabels: Record<string, string> = {
  add: '追加',
  remove: '削除',
  update: '更新',
};

const roleLabels: Record<string, string> = {
  manager: '管理者',
  member: 'メンバー',
};

const actionColors: Record<string, 'success' | 'error' | 'warning'> = {
  add: 'success',
  remove: 'error',
  update: 'warning',
};

export const TeamPermissionHistory: React.FC<TeamPermissionHistoryProps> = ({
  teamId,
  userId,
}) => {
  const { user } = useAuth();
  const [histories, setHistories] = useState<PermissionHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchHistories();
  }, [teamId, userId, page]);

  const fetchHistories = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        limit: itemsPerPage.toString(),
        offset: ((page - 1) * itemsPerPage).toString(),
      });

      if (teamId) {
        params.append('team_id', teamId);
      }
      if (userId) {
        params.append('user_id', userId);
      }

      const response = await fetch(`/api/team-permissions/histories?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('権限変更履歴の取得に失敗しました');
      }

      const data: PermissionHistoryListResponse = await response.json();
      setHistories(data.items);
      setTotalPages(Math.ceil(data.total / itemsPerPage));
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
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
        権限変更履歴
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>変更日時</TableCell>
              <TableCell>変更内容</TableCell>
              <TableCell>権限</TableCell>
              <TableCell>対象ユーザー</TableCell>
              <TableCell>変更者</TableCell>
              <TableCell>変更理由</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {histories.map((history) => (
              <TableRow key={history.id}>
                <TableCell>
                  {new Date(history.changed_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  <Chip
                    label={actionLabels[history.action]}
                    color={actionColors[history.action]}
                    size="small"
                  />
                </TableCell>
                <TableCell>{roleLabels[history.role]}</TableCell>
                <TableCell>{history.user_id}</TableCell>
                <TableCell>{history.changed_by}</TableCell>
                <TableCell>{history.reason || '-'}</TableCell>
              </TableRow>
            ))}
            {histories.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  変更履歴はありません
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}
    </Box>
  );
}; 