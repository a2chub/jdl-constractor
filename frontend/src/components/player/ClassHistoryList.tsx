/**
 * クラス変更履歴一覧を表示するコンポーネント
 * 
 * @description
 * プレイヤーのクラス変更履歴を表示し、以下の機能を提供します：
 * - 履歴の一覧表示
 * - 日付範囲による検索
 * - クラスによるフィルタリング
 * - 承認状態によるフィルタリング
 * - 日付によるソート
 */
import React, { useState, useMemo } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { ArrowUpward, ArrowDownward } from '@mui/icons-material';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';

interface ClassHistory {
  old_class: string;
  new_class: string;
  changed_at: string;
  reason: string;
  approved_by: string | null;
  status: 'pending' | 'approved' | 'rejected';
}

interface ClassHistoryListProps {
  history: ClassHistory[];
}

export const ClassHistoryList: React.FC<ClassHistoryListProps> = ({ history }) => {
  // 検索とフィルタリングの状態
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [selectedClass, setSelectedClass] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // フィルタリングとソートを適用した履歴データ
  const filteredHistory = useMemo(() => {
    return history
      .filter(item => {
        const itemDate = new Date(item.changed_at);
        const matchesDateRange =
          (!startDate || itemDate >= startDate) &&
          (!endDate || itemDate <= endDate);
        const matchesClass =
          !selectedClass ||
          item.old_class === selectedClass ||
          item.new_class === selectedClass;
        const matchesStatus =
          !selectedStatus || item.status === selectedStatus;

        return matchesDateRange && matchesClass && matchesStatus;
      })
      .sort((a, b) => {
        const dateA = new Date(a.changed_at).getTime();
        const dateB = new Date(b.changed_at).getTime();
        return sortDirection === 'asc' ? dateA - dateB : dateB - dateA;
      });
  }, [history, startDate, endDate, selectedClass, selectedStatus, sortDirection]);

  const handleSortToggle = () => {
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  const classOptions = ['A', 'B', 'C', 'D', 'E'];
  const statusOptions = [
    { value: 'pending', label: '承認待ち' },
    { value: 'approved', label: '承認済み' },
    { value: 'rejected', label: '却下' },
  ];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        クラス変更履歴
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <DatePicker
          label="開始日"
          value={startDate}
          onChange={setStartDate}
          format="yyyy/MM/dd"
          slotProps={{ textField: { size: 'small' } }}
        />
        <DatePicker
          label="終了日"
          value={endDate}
          onChange={setEndDate}
          format="yyyy/MM/dd"
          slotProps={{ textField: { size: 'small' } }}
        />
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>クラス</InputLabel>
          <Select
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            label="クラス"
          >
            <MenuItem value="">すべて</MenuItem>
            {classOptions.map(cls => (
              <MenuItem key={cls} value={cls}>{cls}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>ステータス</InputLabel>
          <Select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            label="ステータス"
          >
            <MenuItem value="">すべて</MenuItem>
            {statusOptions.map(status => (
              <MenuItem key={status.value} value={status.value}>
                {status.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                変更日時
                <IconButton size="small" onClick={handleSortToggle}>
                  {sortDirection === 'asc' ? <ArrowUpward /> : <ArrowDownward />}
                </IconButton>
              </TableCell>
              <TableCell>変更前</TableCell>
              <TableCell>変更後</TableCell>
              <TableCell>理由</TableCell>
              <TableCell>承認者</TableCell>
              <TableCell>ステータス</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredHistory.map((item, index) => (
              <TableRow key={index}>
                <TableCell>
                  {format(new Date(item.changed_at), 'yyyy/MM/dd HH:mm', { locale: ja })}
                </TableCell>
                <TableCell>{item.old_class}</TableCell>
                <TableCell>{item.new_class}</TableCell>
                <TableCell>{item.reason}</TableCell>
                <TableCell>{item.approved_by || '-'}</TableCell>
                <TableCell>
                  {statusOptions.find(s => s.value === item.status)?.label || '-'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredHistory.length === 0 && (
        <Typography sx={{ textAlign: 'center', mt: 2 }}>
          該当する履歴がありません
        </Typography>
      )}
    </Box>
  );
}; 