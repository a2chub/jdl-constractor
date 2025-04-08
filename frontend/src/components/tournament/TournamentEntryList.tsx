/**
 * トーナメントのエントリー一覧を表示するコンポーネント
 *
 * このコンポーネントは以下の機能を提供します：
 * - エントリー一覧の表示
 * - エントリーのステータス管理（管理者のみ）
 * - エントリー情報の詳細表示
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
  Chip,
  Box,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import { useAuth } from '../../hooks/useAuth';
import { Entry } from '../../types/tournament';

interface TournamentEntryListProps {
  tournamentId: string;
  entries: Entry[];
  onEntryStatusChange?: (entryId: string, newStatus: string) => Promise<void>;
}

const entryStatusLabels: Record<string, string> = {
  pending: '承認待ち',
  approved: '承認済み',
  rejected: '却下',
  cancelled: 'キャンセル',
};

const entryStatusColors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
  pending: 'warning',
  approved: 'success',
  rejected: 'error',
  cancelled: 'default',
};

export const TournamentEntryList: React.FC<TournamentEntryListProps> = ({
  tournamentId,
  entries,
  onEntryStatusChange,
}) => {
  const { isAdmin } = useAuth();
  const [selectedEntry, setSelectedEntry] = useState<Entry | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStatusChange = async (entry: Entry, newStatus: string) => {
    try {
      setError(null);
      if (onEntryStatusChange) {
        await onEntryStatusChange(entry.player_id, newStatus);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    }
  };

  const handleEntryClick = (entry: Entry) => {
    setSelectedEntry(entry);
    setIsDialogOpen(true);
  };

  return (
    <>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>プレイヤー</TableCell>
              <TableCell>チーム</TableCell>
              <TableCell>エントリー日時</TableCell>
              <TableCell>ステータス</TableCell>
              {isAdmin && <TableCell>アクション</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {entries.map((entry) => (
              <TableRow
                key={`${entry.player_id}-${entry.team_id}`}
                hover
                onClick={() => handleEntryClick(entry)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell>{entry.player_name || entry.player_id}</TableCell>
                <TableCell>{entry.team_name || entry.team_id}</TableCell>
                <TableCell>
                  {new Date(entry.entry_date).toLocaleString()}
                </TableCell>
                <TableCell>
                  <Chip
                    label={entryStatusLabels[entry.status]}
                    color={entryStatusColors[entry.status]}
                    size="small"
                  />
                </TableCell>
                {isAdmin && (
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      {Object.entries(entryStatusLabels).map(([value, label]) => (
                        <Button
                          key={value}
                          variant="outlined"
                          size="small"
                          disabled={entry.status === value}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStatusChange(entry, value);
                          }}
                        >
                          {label}に変更
                        </Button>
                      ))}
                    </Box>
                  </TableCell>
                )}
              </TableRow>
            ))}
            {entries.length === 0 && (
              <TableRow>
                <TableCell colSpan={isAdmin ? 5 : 4} align="center">
                  エントリーはありません
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>エントリー詳細</DialogTitle>
        {selectedEntry && (
          <DialogContent>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  プレイヤー
                </Typography>
                <Typography variant="body1">
                  {selectedEntry.player_name || selectedEntry.player_id}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  チーム
                </Typography>
                <Typography variant="body1">
                  {selectedEntry.team_name || selectedEntry.team_id}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  エントリー日時
                </Typography>
                <Typography variant="body1">
                  {new Date(selectedEntry.entry_date).toLocaleString()}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  ステータス
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip
                    label={entryStatusLabels[selectedEntry.status]}
                    color={entryStatusColors[selectedEntry.status]}
                  />
                </Box>
              </Box>
            </Box>
          </DialogContent>
        )}
        <DialogActions>
          <Button onClick={() => setIsDialogOpen(false)}>
            閉じる
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}; 