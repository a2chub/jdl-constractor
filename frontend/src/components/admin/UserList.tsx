// frontend/src/components/admin/UserList.tsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Pagination,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  debounce, // Debounce search input
  IconButton, // IconButtonを追加
  Tooltip, // Tooltipを追加
} from '@mui/material';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import PersonIcon from '@mui/icons-material/Person';
import EditIcon from '@mui/icons-material/Edit'; // 編集アイコン
import LockOpenIcon from '@mui/icons-material/LockOpen'; // ロック解除アイコン
import LockIcon from '@mui/icons-material/Lock'; // ロックアイコン

// 型定義とAPIクライアントをインポート (パスを確認)
import { UserResponse } from '@/types/user'; // エイリアスパスに変更
import { listUsers, updateUserAdminStatus, updateUserLockStatus } from '@/lib/api/admin'; // updateUserLockStatus をインポート

const ITEMS_PER_PAGE = 10;

export const UserList: React.FC = () => {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAdmin, setFilterAdmin] = useState<'true' | 'false' | ''>(''); // Selectは文字列値を扱う

  // Debounced search term for API call
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');

  // Debounce function using useMemo to avoid recreating it on every render
  const debouncedSetSearch = useMemo(
    () => debounce((term: string) => {
      setDebouncedSearchTerm(term);
      setPage(1); // Reset page when search term changes
    }, 500), // 500ms delay
    []
  );

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params: any = { // Use 'any' temporarily or define ListUsersParams if exported
        page: page,
        limit: ITEMS_PER_PAGE,
      };
      if (debouncedSearchTerm) {
        params.search = debouncedSearchTerm;
      }
      if (filterAdmin !== '') {
        params.is_admin = filterAdmin === 'true';
      }

      const data = await listUsers(params);
      setUsers(data.items);
      setTotalUsers(data.total);
      setTotalPages(Math.ceil(data.total / ITEMS_PER_PAGE));
    } catch (err) {
      console.error("Failed to fetch users:", err);
      setError(err instanceof Error ? err.message : 'ユーザー一覧の取得中にエラーが発生しました。');
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearchTerm, filterAdmin]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]); // fetchUsers is memoized with useCallback

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newSearchTerm = event.target.value;
    setSearchTerm(newSearchTerm);
    debouncedSetSearch(newSearchTerm);
  };

  const handleFilterChange = (event: SelectChangeEvent<string>) => {
    setFilterAdmin(event.target.value as 'true' | 'false' | '');
    setPage(1); // Reset page when filter changes
  };

  // TODO: Implement these handlers
  const handleEditUser = (userId: string) => {
    console.log("Edit user:", userId);
    // Navigate to edit page or open modal
   };

   const handleToggleLock = async (userId: string, currentIsLocked: boolean) => {
     const newIsLocked = !currentIsLocked;
     const actionText = newIsLocked ? 'ロック' : 'ロック解除';
     // 確認ダイアログ省略
     // if (!window.confirm(`ユーザー ${userId} を${actionText}しますか？`)) {
     //   return;
     // }
     setError(null);

     try {
       const updatedUser = await updateUserLockStatus(userId, newIsLocked);
       setUsers(prevUsers =>
         prevUsers.map(u => (u.id === userId ? updatedUser : u))
       );
       console.log(`ユーザー ${userId} を${actionText}しました。`);
       // Snackbar などでフィードバック表示
     } catch (err) {
       console.error(`Failed to toggle lock status for user ${userId}:`, err);
       setError(err instanceof Error ? err.message : `ユーザー(${userId})のロック状態更新中にエラーが発生しました。`);
     }
   };

   const handleToggleAdmin = async (userId: string, currentIsAdmin: boolean) => {
     const newIsAdmin = !currentIsAdmin;
     const actionText = newIsAdmin ? '付与' : '剥奪';
     // 確認ダイアログを省略 (本番では window.confirm や Material UI Dialog を使用)
     // if (!window.confirm(`ユーザー ${userId} の管理者権限を${actionText}しますか？`)) {
     //   return;
     // }

     // ローディング表示やエラーハンドリングを追加可能
     setError(null); // エラーをクリア

     try {
       const updatedUser = await updateUserAdminStatus(userId, newIsAdmin);
       // リストの状態を更新
       setUsers(prevUsers =>
         prevUsers.map(u => (u.id === userId ? updatedUser : u))
       );
       // 成功メッセージ (Snackbarなど)
       console.log(`ユーザー ${userId} の管理者権限を${actionText}しました。`);
     } catch (err) {
       console.error(`Failed to toggle admin status for user ${userId}:`, err);
       setError(err instanceof Error ? err.message : `ユーザー(${userId})の権限更新中にエラーが発生しました。`);
     }
   };


  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3 }}>
        ユーザー管理
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters and Search */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          label="名前 or メール検索"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={handleSearchChange}
          sx={{ flexGrow: 1, minWidth: '200px' }}
        />
        <FormControl size="small" sx={{ minWidth: '150px' }}>
          <InputLabel>管理者権限</InputLabel>
          <Select
            value={filterAdmin}
            label="管理者権限"
            onChange={handleFilterChange}
          >
            <MenuItem value="">すべて</MenuItem>
            <MenuItem value="true">管理者のみ</MenuItem>
            <MenuItem value="false">一般ユーザーのみ</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {!loading && (
        <>
          <TableContainer component={Paper} elevation={2}>
            <Table>
              <TableHead>
                <TableRow>
                  {/* <TableCell sx={{ fontWeight: 'bold' }}>ID</TableCell> */}
                  <TableCell sx={{ fontWeight: 'bold' }}>名前</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>メールアドレス</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>管理者</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>登録日時</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', textAlign: 'right' }}>アクション</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} hover>
                    {/* <TableCell sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>{user.id}</TableCell> */}
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Tooltip title={user.is_admin ? "管理者権限を剥奪" : "管理者権限を付与"}>
                        <Chip
                          icon={user.is_admin ? <AdminPanelSettingsIcon /> : <PersonIcon />}
                          label={user.is_admin ? "管理者" : "一般"}
                          color={user.is_admin ? "success" : "default"}
                          size="small"
                          variant="outlined"
                          onClick={() => handleToggleAdmin(user.id, user.is_admin ?? false)} // is_adminがundefinedの場合を考慮
                          clickable
                        />
                      </Tooltip>
                    </TableCell>
                    <TableCell>
                      {user.created_at ? new Date(user.created_at).toLocaleString() : '-'}
                    </TableCell>
                    <TableCell sx={{ textAlign: 'right' }}>
                       {/* アクションボタン (編集、ロックなど) */}
                       <Tooltip title="編集 (未実装)">
                         <span> {/* IconButtonが無効な場合にTooltipを表示するため */}
                           <IconButton size="small" onClick={() => handleEditUser(user.id)} disabled>
                             <EditIcon fontSize="small" />
                           </IconButton>
                         </span>
                       </Tooltip>
                       <Tooltip title={user.is_locked ? "アカウントロック解除" : "アカウントロック"}>
                         <IconButton
                           size="small"
                           onClick={() => handleToggleLock(user.id, user.is_locked ?? false)}
                           color={user.is_locked ? "warning" : "default"}
                         >
                           {user.is_locked ? <LockIcon fontSize="small" /> : <LockOpenIcon fontSize="small" />}
                         </IconButton>
                       </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
                {users.length === 0 && !loading && ( // ローディング中でない場合のみ表示
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      該当するユーザーが見つかりません。
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                showFirstButton showLastButton // ページネーションのボタンを追加
              />
            </Box>
          )}
        </>
      )}

       {/* ルーティング設定が不明なため、ユーザーへの注意喚起 */}
       <Alert severity="info" sx={{ mt: 4 }}>
         <strong>開発者向け情報:</strong> このユーザー管理画面を表示するには、アプリケーションのルーティング設定に <code>/admin/users</code> パスを追加し、<code>UserList</code> コンポーネントをレンダリングするように設定してください。管理者権限での保護も必要です。
       </Alert>
    </Box>
  );
};

export default UserList;
