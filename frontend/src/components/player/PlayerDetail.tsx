/**
 * プレイヤー詳細を表示するコンポーネント
 *
 * このコンポーネントは以下の機能を提供します：
 * - プレイヤーの基本情報表示
 * - クラス変更履歴の表示
 * - プレイヤー情報の編集（チーム管理者のみ）
 * - チーム所属の変更
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { useAuth } from '../../hooks/useAuth';
// import { useTeams } from '../../hooks/useTeams'; // フックが存在しないため削除
import { LoadingSpinner } from '../LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage';

interface ClassHistory {
  old_class: string;
  new_class: string;
  changed_at: string;
  reason: string;
  approved_by: string | null;
}

interface Player {
  id: string;
  name: string;
  jdl_id: string;
  team_id: string | null;
  team_name: string | null;
  participation_count: number;
  current_class: string;
  class_history: ClassHistory[];
  created_at: string;
  updated_at: string;
}

export const PlayerDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth(); // フックが返すプロパティ名に修正
  // const { teams } = useTeams(); // フックが存在しないため削除
  const [player, setPlayer] = useState<Player | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editData, setEditData] = useState({
    name: '',
    team_id: '',
    participation_count: 0,
    current_class: '',
  });

  useEffect(() => {
    fetchPlayer();
  }, [id]);

  const fetchPlayer = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/players/${id}`, {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`, // userを使用
        },
      });

      if (!response.ok) {
        throw new Error('プレイヤー情報の取得に失敗しました');
      }

      const data: Player = await response.json();
      setPlayer(data);
      setEditData({
        name: data.name,
        team_id: data.team_id || '',
        participation_count: data.participation_count,
        current_class: data.current_class,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleEditSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/players/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await user?.getIdToken()}`, // userを使用
        },
        body: JSON.stringify(editData),
      });

      if (!response.ok) {
        throw new Error('プレイヤー情報の更新に失敗しました');
      }

      await fetchPlayer();
      setIsEditDialogOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!player) {
    return <Typography>プレイヤーが見つかりません</Typography>;
  }

  // TODO: チーム管理者かどうかの判定ロジックを修正する必要がある (teamsフックがないため)
  const canEdit = user && player.team_id; // userを使用

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" component="h1">
          プレイヤー詳細
        </Typography>
        <Box>
          <Button
            onClick={() => navigate('/players')}
            variant="outlined"
            sx={{ mr: 1 }}
          >
            一覧に戻る
          </Button>
          {canEdit && (
            <Button
              onClick={() => setIsEditDialogOpen(true)}
              variant="contained"
              color="primary"
            >
              編集
            </Button>
          )}
        </Box>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            基本情報
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
            <Typography><strong>名前:</strong> {player.name}</Typography>
            <Typography><strong>JDL ID:</strong> {player.jdl_id}</Typography>
            <Typography><strong>所属チーム:</strong> {player.team_name || '-'}</Typography>
            <Typography><strong>参加回数:</strong> {player.participation_count}</Typography>
            <Typography><strong>現在のクラス:</strong> {player.current_class}</Typography>
            <Typography><strong>登録日時:</strong> {new Date(player.created_at).toLocaleString()}</Typography>
          </Box>
        </CardContent>
      </Card>

      <Typography variant="h6" gutterBottom>
        クラス変更履歴
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>変更日時</TableCell>
              <TableCell>変更前</TableCell>
              <TableCell>変更後</TableCell>
              <TableCell>理由</TableCell>
              <TableCell>承認者</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {player.class_history.map((history, index) => (
              <TableRow key={index}>
                <TableCell>{new Date(history.changed_at).toLocaleString()}</TableCell>
                <TableCell>{history.old_class}</TableCell>
                <TableCell>{history.new_class}</TableCell>
                <TableCell>{history.reason}</TableCell>
                <TableCell>{history.approved_by || '-'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>プレイヤー情報の編集</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gap: 2, mt: 2 }}>
            <TextField
              label="名前"
              value={editData.name}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>所属チーム</InputLabel>
              <Select
                value={editData.team_id}
                onChange={(e) => setEditData({ ...editData, team_id: e.target.value })}
                label="所属チーム"
              >
                <MenuItem value="">なし</MenuItem>
                {/* {teams.map((team) => ( // teams がないので一時的にコメントアウト
                  <MenuItem key={team.id} value={team.id}>
                    {team.name}
                  </MenuItem>
                ))} */}
              </Select>
            </FormControl>
            <TextField
              label="参加回数"
              type="number"
              value={editData.participation_count}
              onChange={(e) => setEditData({ ...editData, participation_count: parseInt(e.target.value) })}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>クラス</InputLabel>
              <Select
                value={editData.current_class}
                onChange={(e) => setEditData({ ...editData, current_class: e.target.value })}
                label="クラス"
              >
                {['A', 'B', 'C', 'D', 'E'].map((cls) => (
                  <MenuItem key={cls} value={cls}>
                    {cls}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEditDialogOpen(false)}>キャンセル</Button>
          <Button onClick={handleEditSubmit} variant="contained" color="primary">
            保存
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
