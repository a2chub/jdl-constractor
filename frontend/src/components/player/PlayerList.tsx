/**
 * プレイヤー一覧を表示するコンポーネント
 *
 * このコンポーネントは以下の機能を提供します：
 * - プレイヤーの一覧表示
 * - チームによるフィルタリング
 * - ページネーション
 * - プレイヤー詳細へのリンク
 * - プレイヤー作成ボタン（チーム管理者のみ）
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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Box,
  Pagination,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useTeams } from '../../hooks/useTeams';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';

interface Player {
  id: string;
  name: string;
  jdl_id: string;
  team_id: string | null;
  team_name: string | null;
  participation_count: number;
  current_class: string;
}

interface PlayerListResponse {
  items: Player[];
  total: number;
}

export const PlayerList: React.FC = () => {
  const { user } = useAuth();
  const { teams, loading: teamsLoading } = useTeams();
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchPlayers();
  }, [selectedTeam, page]);

  const fetchPlayers = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        limit: itemsPerPage.toString(),
        offset: ((page - 1) * itemsPerPage).toString(),
      });

      if (selectedTeam) {
        params.append('team_id', selectedTeam);
      }

      const response = await fetch(`/api/players?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('プレイヤー一覧の取得に失敗しました');
      }

      const data: PlayerListResponse = await response.json();
      setPlayers(data.items);
      setTotalPages(Math.ceil(data.total / itemsPerPage));
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleTeamChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSelectedTeam(event.target.value as string);
    setPage(1);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const filteredPlayers = players.filter(player =>
    player.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    player.jdl_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading || teamsLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" component="h1">
          プレイヤー一覧
        </Typography>
        {user && (
          <Button
            component={RouterLink}
            to="/players/new"
            variant="contained"
            color="primary"
          >
            プレイヤーを作成
          </Button>
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          label="プレイヤー検索"
          variant="outlined"
          size="small"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ width: 250 }}
        />
        <FormControl size="small" sx={{ width: 200 }}>
          <InputLabel>チームでフィルター</InputLabel>
          <Select
            value={selectedTeam}
            onChange={handleTeamChange}
            label="チームでフィルター"
          >
            <MenuItem value="">すべて</MenuItem>
            {teams.map((team) => (
              <MenuItem key={team.id} value={team.id}>
                {team.name}
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
              <TableCell>JDL ID</TableCell>
              <TableCell>所属チーム</TableCell>
              <TableCell>参加回数</TableCell>
              <TableCell>クラス</TableCell>
              <TableCell>アクション</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredPlayers.map((player) => (
              <TableRow key={player.id}>
                <TableCell>{player.name}</TableCell>
                <TableCell>{player.jdl_id}</TableCell>
                <TableCell>{player.team_name || '-'}</TableCell>
                <TableCell>{player.participation_count}</TableCell>
                <TableCell>{player.current_class}</TableCell>
                <TableCell>
                  <Button
                    component={RouterLink}
                    to={`/players/${player.id}`}
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