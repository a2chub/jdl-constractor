/**
 * トーナメント一覧を表示するコンポーネント
 *
 * このコンポーネントは以下の機能を提供します：
 * - トーナメントの一覧表示
 * - ステータスによるフィルタリング
 * - ページネーション
 * - トーナメント詳細へのリンク
 * - トーナメント作成ボタン（管理者のみ）
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
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Box,
  Pagination,
  Chip,
  SelectChangeEvent, // SelectChangeEvent をインポート
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { LoadingSpinner } from '../LoadingSpinner'; // パス修正
import { ErrorMessage } from '../ErrorMessage'; // パス修正

type TournamentStatus = 'draft' | 'entry_open' | 'entry_closed' | 'in_progress' | 'completed' | 'cancelled';

interface Tournament {
  id: string;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  entry_start_date: string;
  entry_end_date: string;
  venue: string;
  entry_fee: number;
  status: TournamentStatus;
  current_entries: number;
}

interface TournamentListResponse {
  items: Tournament[];
  total: number;
}

const statusLabels: Record<TournamentStatus, string> = {
  draft: '下書き',
  entry_open: 'エントリー受付中',
  entry_closed: 'エントリー締切',
  in_progress: '開催中',
  completed: '終了',
  cancelled: 'キャンセル',
};

const statusColors: Record<TournamentStatus, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
  draft: 'default',
  entry_open: 'success',
  entry_closed: 'warning',
  in_progress: 'primary',
  completed: 'secondary',
  cancelled: 'error',
};

export const TournamentList: React.FC = () => {
  const { user } = useAuth(); // isAdmin を削除
  // TODO: 管理者判定ロジックを実装する (例: user?.customClaims?.admin)
  const isAdmin = !!user; // 一時的にログインユーザーなら管理者とみなす
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<TournamentStatus | ''>('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchTournaments();
  }, [selectedStatus, page]);

  const fetchTournaments = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        limit: itemsPerPage.toString(),
        offset: ((page - 1) * itemsPerPage).toString(),
      });

      if (selectedStatus) {
        params.append('status', selectedStatus);
      }

      const response = await fetch(`/api/tournaments?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('トーナメント一覧の取得に失敗しました');
      }

      const data: TournamentListResponse = await response.json();
      setTournaments(data.items);
      setTotalPages(Math.ceil(data.total / itemsPerPage));
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = (event: SelectChangeEvent<TournamentStatus | ''>) => { // 型を修正
    setSelectedStatus(event.target.value as TournamentStatus | '');
    setPage(1);
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
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" component="h1">
          トーナメント一覧
        </Typography>
        {isAdmin && (
          <Button
            component={RouterLink}
            to="/tournaments/new"
            variant="contained"
            color="primary"
          >
            トーナメントを作成
          </Button>
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl size="small" sx={{ width: 200 }}>
          <InputLabel>ステータスでフィルター</InputLabel>
          <Select
            value={selectedStatus}
            onChange={handleStatusChange}
            label="ステータスでフィルター"
          >
            <MenuItem value="">すべて</MenuItem>
            {Object.entries(statusLabels).map(([value, label]) => (
              <MenuItem key={value} value={value}>
                {label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>名前</TableCell>
              <TableCell>開催場所</TableCell>
              <TableCell>開催期間</TableCell>
              <TableCell>エントリー期間</TableCell>
              <TableCell>参加費</TableCell>
              <TableCell>エントリー数</TableCell>
              <TableCell>ステータス</TableCell>
              <TableCell>アクション</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tournaments.map((tournament) => (
              <TableRow key={tournament.id}>
                <TableCell>{tournament.name}</TableCell>
                <TableCell>{tournament.venue}</TableCell>
                <TableCell>
                  {new Date(tournament.start_date).toLocaleDateString()} ～{' '}
                  {new Date(tournament.end_date).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {new Date(tournament.entry_start_date).toLocaleDateString()} ～{' '}
                  {new Date(tournament.entry_end_date).toLocaleDateString()}
                </TableCell>
                <TableCell>¥{tournament.entry_fee.toLocaleString()}</TableCell>
                <TableCell>{tournament.current_entries}</TableCell>
                <TableCell>
                  <Chip
                    label={statusLabels[tournament.status]}
                    color={statusColors[tournament.status]}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Button
                    component={RouterLink}
                    to={`/tournaments/${tournament.id}`}
                    size="small"
                    color="primary"
                  >
                    詳細
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
        <Pagination
          count={totalPages}
          page={page}
          onChange={handlePageChange}
          color="primary"
        />
      </Box>
    </Box>
  );
};
