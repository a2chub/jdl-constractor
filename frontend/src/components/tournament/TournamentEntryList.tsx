/**
 * トーナメントのエントリー一覧を表示するコンポーネント
 *
 * このコンポーネントは以下の機能を提供します：
 * - エントリー一覧の表示
 * - エントリーのステータス管理（管理者のみ）
 * - エントリー情報の詳細表示
 */

import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useAuth } from '../../hooks/useAuth';

interface TournamentEntryListProps {
  tournamentId: string;
}

export const TournamentEntryList: React.FC<TournamentEntryListProps> = () => {
  const { user } = useAuth();
  const isAdmin = user?.getIdTokenResult().then(token => token.claims.admin) ?? false;

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        エントリー一覧
      </Typography>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>チーム名</TableCell>
              <TableCell>エントリー日時</TableCell>
              <TableCell>ステータス</TableCell>
              {isAdmin && <TableCell>操作</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {/* エントリー一覧を表示 */}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}; 