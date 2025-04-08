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

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  SelectChangeEvent, // Import SelectChangeEvent
} from '@mui/material';
import { useAuth } from '../../hooks/useAuth';
import { LoadingSpinner } from '../LoadingSpinner'; // Corrected path

interface TournamentFormData {
  name: string;
  description: string;
  venue: string;
  entry_fee: number;
  start_date: string;
  end_date: string;
  entry_start_date: string;
  entry_end_date: string;
  status: 'draft' | 'entry_open' | 'entry_closed' | 'in_progress' | 'completed' | 'cancelled';
}

interface TournamentFormProps {
  tournamentId?: string;
  initialData?: Partial<TournamentFormData>;
  onSubmit: (data: TournamentFormData) => Promise<void>;
}

const defaultFormData: TournamentFormData = {
  name: '',
  description: '',
  venue: '',
  entry_fee: 0,
  start_date: '',
  end_date: '',
  entry_start_date: '',
  entry_end_date: '',
  status: 'draft',
};

const statusLabels: Record<TournamentFormData['status'], string> = {
  draft: '下書き',
  entry_open: 'エントリー受付中',
  entry_closed: 'エントリー締切',
  in_progress: '開催中',
  completed: '終了',
  cancelled: 'キャンセル',
};

export const TournamentForm: React.FC<TournamentFormProps> = ({
  tournamentId,
  initialData,
  onSubmit,
}) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { t } = useTranslation('tournament'); // Specify the namespace
  const [formData, setFormData] = useState<TournamentFormData>({ ...defaultFormData, ...initialData });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Partial<Record<keyof TournamentFormData, string>>>({});

  const validateForm = (): boolean => {
    const errors: Partial<Record<keyof TournamentFormData, string>> = {};

    if (!formData.name.trim()) {
      errors.name = t('form.validation.required.name'); // Remove 'tournament.' prefix
    }

    if (!formData.venue.trim()) {
      errors.venue = t('form.validation.required.venue'); // Remove 'tournament.' prefix
    }

    if (formData.entry_fee < 0) {
      errors.entry_fee = t('form.validation.invalid.entry_fee'); // Remove 'tournament.' prefix
    }

    const startDate = new Date(formData.start_date);
    const endDate = new Date(formData.end_date);
    const entryStartDate = new Date(formData.entry_start_date);
    const entryEndDate = new Date(formData.entry_end_date);

    if (isNaN(startDate.getTime())) {
      errors.start_date = t('form.validation.required.start_date'); // Remove 'tournament.' prefix
    }

    if (isNaN(endDate.getTime())) {
      errors.end_date = t('form.validation.required.end_date'); // Remove 'tournament.' prefix
    }

    if (isNaN(entryStartDate.getTime())) {
      errors.entry_start_date = t('form.validation.required.entry_start_date'); // Remove 'tournament.' prefix
    }

    if (isNaN(entryEndDate.getTime())) {
      errors.entry_end_date = t('form.validation.required.entry_end_date'); // Remove 'tournament.' prefix
    }

    if (startDate >= endDate) {
      errors.end_date = t('form.validation.invalid.end_date'); // Remove 'tournament.' prefix
    }

    if (entryStartDate >= entryEndDate) {
      errors.entry_end_date = t('form.validation.invalid.entry_end_date.after_start'); // Remove 'tournament.' prefix
    }

    if (entryEndDate >= startDate) {
      errors.entry_end_date = t('form.validation.invalid.entry_end_date.before_start'); // Remove 'tournament.' prefix
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await onSubmit(formData);
      navigate('/tournaments');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('form.messages.error.unexpected')); // Remove 'tournament.' prefix
    } finally {
      setLoading(false);
    }
  };

  // TextField 用の汎用ハンドラ
  const handleInputChange = (field: keyof Omit<TournamentFormData, 'status'>) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const { value } = e.target;
    setFormData(prev => ({
      ...prev,
      [field]: field === 'entry_fee' ? parseInt(value, 10) || 0 : value, // entry_fee は数値に変換
    }));
    // フィールドが変更されたら、そのフィールドのバリデーションエラーをクリア
    if (validationErrors[field]) {
      setValidationErrors(prev => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  // Select (ステータス) 用のハンドラ
  const handleStatusChange = (event: SelectChangeEvent<TournamentFormData['status']>) => {
    const { value } = event.target;
    setFormData(prev => ({
      ...prev,
      status: value as TournamentFormData['status'],
    }));
     // ステータスフィールドのバリデーションエラーをクリア (もしあれば)
     if (validationErrors.status) {
      setValidationErrors(prev => ({
        ...prev,
        status: undefined,
      }));
    }
  };


  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          {tournamentId
            ? t('form.title.edit') // Remove 'tournament.' prefix
            : t('form.title.create')} {/* Remove 'tournament.' prefix */}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              label={t('form.fields.name.label')} // Remove 'tournament.' prefix
              placeholder={t('form.fields.name.placeholder')} // Remove 'tournament.' prefix
              value={formData.name}
              onChange={handleInputChange('name')}
              error={!!validationErrors.name}
              helperText={validationErrors.name}
              fullWidth
              required
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              label={t('form.fields.description.label')} // Remove 'tournament.' prefix
              placeholder={t('form.fields.description.placeholder')} // Remove 'tournament.' prefix
              value={formData.description}
              onChange={handleInputChange('description')}
              multiline
              rows={4}
              fullWidth
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label={t('form.fields.venue.label')} // Remove 'tournament.' prefix
              placeholder={t('form.fields.venue.placeholder')} // Remove 'tournament.' prefix
              value={formData.venue}
              onChange={handleInputChange('venue')}
              error={!!validationErrors.venue}
              helperText={validationErrors.venue}
              fullWidth
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label={t('form.fields.entry_fee.label')} // Remove 'tournament.' prefix
              placeholder={t('form.fields.entry_fee.placeholder')} // Remove 'tournament.' prefix
              type="number"
              value={formData.entry_fee}
              onChange={handleInputChange('entry_fee')}
              error={!!validationErrors.entry_fee}
              helperText={validationErrors.entry_fee}
              fullWidth
              required
              InputProps={{
                inputProps: { min: 0 },
              }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label={t('form.fields.start_date.label')} // Remove 'tournament.' prefix
              type="datetime-local"
              value={formData.start_date}
              onChange={handleInputChange('start_date')}
              error={!!validationErrors.start_date}
              helperText={validationErrors.start_date}
              fullWidth
              required
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label={t('form.fields.end_date.label')} // Remove 'tournament.' prefix
              type="datetime-local"
              value={formData.end_date}
              onChange={handleInputChange('end_date')}
              error={!!validationErrors.end_date}
              helperText={validationErrors.end_date}
              fullWidth
              required
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label={t('form.fields.entry_start_date.label')} // Remove 'tournament.' prefix
              type="datetime-local"
              value={formData.entry_start_date}
              onChange={handleInputChange('entry_start_date')}
              error={!!validationErrors.entry_start_date}
              helperText={validationErrors.entry_start_date}
              fullWidth
              required
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label={t('form.fields.entry_end_date.label')} // Remove 'tournament.' prefix
              type="datetime-local"
              value={formData.entry_end_date}
              onChange={handleInputChange('entry_end_date')}
              error={!!validationErrors.entry_end_date}
              helperText={validationErrors.entry_end_date}
              fullWidth
              required
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth error={!!validationErrors.status}>
              <InputLabel>{t('form.fields.status.label')}</InputLabel> {/* Remove 'tournament.' prefix */}
              <Select
                value={formData.status}
                onChange={handleStatusChange} // Use specific handler
                label={t('form.fields.status.label')} // Remove 'tournament.' prefix
              >
                {Object.entries(statusLabels).map(([value, label]) => ( // label is unused here, t() is used below
                  <MenuItem key={value} value={value}>
                    {t(`form.fields.status.options.${value}`)} {/* Remove 'tournament.' prefix */}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
          >
            {tournamentId
              ? t('form.buttons.update') // Remove 'tournament.' prefix
              : t('form.buttons.create')} {/* Remove 'tournament.' prefix */}
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/tournaments')}
            disabled={loading}
          >
            {t('form.buttons.cancel')} {/* Remove 'tournament.' prefix */}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};
