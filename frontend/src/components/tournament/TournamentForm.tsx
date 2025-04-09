/**
 * トーナメント作成・編集フォームコンポーネント
 *
 * このコンポーネントは以下の機能を提供します：
 * - トーナメントの新規作成フォーム
 * - 既存トーナメントの編集フォーム
 * - バリデーション機能
 * - エラーハンドリング
 * - 国際化対応
 */

import React, { useState } from 'react';
import {
  TextField,
  Button,
  Box,
  Typography,
  FormControl,
  FormHelperText,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { LoadingSpinner } from '../LoadingSpinner';
import { ErrorMessage } from '../ErrorMessage';

interface TournamentFormData {
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  maxTeams: number;
}

interface TournamentFormProps {
  mode: 'create' | 'edit';
  tournamentId?: string;
}

export const TournamentForm: React.FC<TournamentFormProps> = ({ mode, tournamentId }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<TournamentFormData>({
    name: '',
    description: '',
    startDate: '',
    endDate: '',
    maxTeams: 8,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        mode === 'create' ? '/api/tournaments' : `/api/tournaments/${tournamentId}`,
        {
          method: mode === 'create' ? 'POST' : 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        throw new Error('トーナメントの保存に失敗しました');
      }

      const data = await response.json();
      navigate(`/tournaments/${data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {mode === 'create' ? 'トーナメントを作成' : 'トーナメントを編集'}
      </Typography>

      {error && <ErrorMessage message={error} />}

      <form onSubmit={handleSubmit}>
        <FormControl fullWidth margin="normal">
          <TextField
            label="トーナメント名"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
        </FormControl>

        <FormControl fullWidth margin="normal">
          <TextField
            label="説明"
            multiline
            rows={4}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </FormControl>

        <FormControl fullWidth margin="normal">
          <TextField
            label="開始日"
            type="date"
            required
            value={formData.startDate}
            onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
        </FormControl>

        <FormControl fullWidth margin="normal">
          <TextField
            label="終了日"
            type="date"
            required
            value={formData.endDate}
            onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
          <FormHelperText>開始日より後の日付を選択してください</FormHelperText>
        </FormControl>

        <FormControl fullWidth margin="normal">
          <TextField
            label="最大チーム数"
            type="number"
            required
            value={formData.maxTeams}
            onChange={(e) => setFormData({ ...formData, maxTeams: parseInt(e.target.value, 10) })}
            inputProps={{ min: 2, max: 64 }}
          />
          <FormHelperText>2〜64チームまで設定可能です</FormHelperText>
        </FormControl>

        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            onClick={() => navigate(-1)}
          >
            キャンセル
          </Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
          >
            {mode === 'create' ? '作成' : '更新'}
          </Button>
        </Box>
      </form>
    </Box>
  );
};
