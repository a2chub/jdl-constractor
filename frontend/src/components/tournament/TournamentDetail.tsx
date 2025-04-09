/**
 * トーナメント詳細を表示するコンポーネント
 *
 * このコンポーネントは以下の機能を提供します：
 * - トーナメントの基本情報表示
 * - エントリー一覧の表示
 * - ステータス管理（管理者のみ）
 * - トーナメント情報の編集（管理者のみ）
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
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
  Alert,
} from '@mui/material';
import { useAuth } from '../../hooks/useAuth';
import { LoadingSpinner } from '../LoadingSpinner'; // パス修正
import { ErrorMessage } from '../ErrorMessage'; // パス修正
import { TournamentStatus, statusLabels, statusColors } from '../../types/tournament';
import { TournamentEntryList } from './TournamentEntryList';

interface Entry {
  player_id: string;
  team_id: string;
  entry_date: string;
  status: string;
  player_name?: string;
  team_name?: string;
}

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
  entries: Entry[];
  current_entries: number;
  created_at: string;
  updated_at: string;
}

export const TournamentDetail: React.FC = () => {
  const { tournamentId } = useParams<{ tournamentId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth(); // isAdmin を削除
  // TODO: 管理者判定ロジックを実装する (例: user?.customClaims?.admin)
  const isAdmin = !!user; // 一時的にログインユーザーなら管理者とみなす
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editData, setEditData] = useState<Partial<Tournament>>({});

  useEffect(() => {
    fetchTournamentDetails();
  }, [tournamentId]);

  const fetchTournamentDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/tournaments/${tournamentId}`, {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('トーナメント情報の取得に失敗しました');
      }

      const data: Tournament = await response.json();
      setTournament(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleEditSubmit = async () => {
    try {
      setError(null);

      const response = await fetch(`/api/tournaments/${tournamentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
        body: JSON.stringify(editData),
      });

      if (!response.ok) {
        throw new Error('トーナメント情報の更新に失敗しました');
      }

      const updatedTournament = await response.json();
      setTournament(updatedTournament);
      setIsEditDialogOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    }
  };

  const handleStatusChange = async (newStatus: TournamentStatus) => {
    try {
      setError(null);

      const response = await fetch(`/api/tournaments/${tournamentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error('トーナメントステータスの更新に失敗しました');
      }

      const updatedTournament = await response.json();
      setTournament(updatedTournament);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    }
  };

  const handleEntryStatusChange = async (playerId: string, newStatus: string) => {
    try {
      setError(null);

      const response = await fetch(`/api/tournaments/${tournamentId}/entries/${playerId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error('エントリーステータスの更新に失敗しました');
      }

      const updatedTournament = await response.json();
      setTournament(updatedTournament);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!tournament) {
    return <ErrorMessage message="トーナメントが見つかりません" />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1">
          {tournament.name}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {isAdmin && (
            <>
              <Button
                variant="outlined"
                color="primary"
                onClick={() => {
                  setEditData(tournament);
                  setIsEditDialogOpen(true);
                }}
              >
                編集
              </Button>
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => navigate('/tournaments')}
              >
                一覧に戻る
              </Button>
            </>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              基本情報
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  説明
                </Typography>
                <Typography variant="body1">
                  {tournament.description}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  開催期間
                </Typography>
                <Typography variant="body1">
                  {new Date(tournament.start_date).toLocaleDateString()} ～{' '}
                  {new Date(tournament.end_date).toLocaleDateString()}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  エントリー期間
                </Typography>
                <Typography variant="body1">
                  {new Date(tournament.entry_start_date).toLocaleDateString()} ～{' '}
                  {new Date(tournament.entry_end_date).toLocaleDateString()}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  開催場所
                </Typography>
                <Typography variant="body1">
                  {tournament.venue}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  参加費
                </Typography>
                <Typography variant="body1">
                  ¥{tournament.entry_fee.toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  ステータス
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip
                    label={statusLabels[tournament.status]}
                    color={statusColors[tournament.status]}
                  />
                </Box>
              </Grid>
              {isAdmin && (
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    ステータス変更
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {Object.entries(statusLabels).map(([value, label]) => (
                      <Button
                        key={value}
                        variant="outlined"
                        size="small"
                        disabled={tournament.status === value}
                        onClick={() => handleStatusChange(value as TournamentStatus)}
                      >
                        {label}に変更
                      </Button>
                    ))}
                  </Box>
                </Grid>
              )}
            </Grid>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                エントリー一覧
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {tournament.current_entries} エントリー
              </Typography>
            </Box>
            <TournamentEntryList
              tournamentId={tournament.id}
              entries={tournament.entries}
              onEntryStatusChange={handleEntryStatusChange}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              システム情報
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  作成日時
                </Typography>
                <Typography variant="body1">
                  {new Date(tournament.created_at).toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  最終更新
                </Typography>
                <Typography variant="body1">
                  {new Date(tournament.updated_at).toLocaleString()}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      <Dialog
        open={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>トーナメント情報の編集</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gap: 2, mt: 2 }}>
            <TextField
              label="トーナメント名"
              value={editData.name || ''}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="説明"
              value={editData.description || ''}
              onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              multiline
              rows={4}
              fullWidth
            />
            <TextField
              label="開催場所"
              value={editData.venue || ''}
              onChange={(e) => setEditData({ ...editData, venue: e.target.value })}
              fullWidth
            />
            <TextField
              label="参加費"
              type="number"
              value={editData.entry_fee || 0}
              onChange={(e) => setEditData({ ...editData, entry_fee: parseInt(e.target.value) })}
              fullWidth
            />
            <TextField
              label="開始日時"
              type="datetime-local"
              value={editData.start_date?.slice(0, 16) || ''}
              onChange={(e) => setEditData({ ...editData, start_date: new Date(e.target.value).toISOString() })}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="終了日時"
              type="datetime-local"
              value={editData.end_date?.slice(0, 16) || ''}
              onChange={(e) => setEditData({ ...editData, end_date: new Date(e.target.value).toISOString() })}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="エントリー開始日時"
              type="datetime-local"
              value={editData.entry_start_date?.slice(0, 16) || ''}
              onChange={(e) => setEditData({ ...editData, entry_start_date: new Date(e.target.value).toISOString() })}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="エントリー終了日時"
              type="datetime-local"
              value={editData.entry_end_date?.slice(0, 16) || ''}
              onChange={(e) => setEditData({ ...editData, entry_end_date: new Date(e.target.value).toISOString() })}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEditDialogOpen(false)}>
            キャンセル
          </Button>
          <Button onClick={handleEditSubmit} variant="contained" color="primary">
            保存
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
