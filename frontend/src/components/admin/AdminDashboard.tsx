// frontend/src/components/admin/AdminDashboard.tsx
import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, CircularProgress, Alert, Button } from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import GroupIcon from '@mui/icons-material/Group';
import PersonIcon from '@mui/icons-material/Person';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import SettingsIcon from '@mui/icons-material/Settings'; // 例: 設定アイコン
import HistoryIcon from '@mui/icons-material/History'; // 例: 監査ログアイコン
import { Link as RouterLink } from 'react-router-dom'; // ルーティング用

import { AdminDashboardSummary } from '../../types/admin';
import { getAdminDashboardSummary } from '../../lib/api/admin';
// 共通コンポーネントのインポートパスを確認・修正
// import { LoadingSpinner } from '../common/LoadingSpinner';
// import { ErrorMessage } from '../common/ErrorMessage';

// サマリー項目表示用のコンポーネント
interface SummaryCardProps {
  title: string;
  value: number;
  icon: React.ReactElement;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ title, value, icon }) => (
  <Paper elevation={3} sx={{ p: 2, display: 'flex', alignItems: 'center', height: '100%', borderRadius: 2 }}>
    {React.cloneElement(icon, { sx: { fontSize: 40, mr: 2, color: 'primary.main' } })}
    <Box>
      <Typography color="text.secondary" gutterBottom>
        {title}
      </Typography>
      <Typography variant="h5" component="div" fontWeight="bold">
        {/* 値が存在しない場合やエラーの場合の表示を考慮 */}
        {typeof value === 'number' ? value.toLocaleString() : '-'}
      </Typography>
    </Box>
  </Paper>
);


export const AdminDashboard: React.FC = () => {
  const [summary, setSummary] = useState<AdminDashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getAdminDashboardSummary();
        setSummary(data);
      } catch (err) {
         console.error("Failed to fetch admin summary:", err);
         // ユーザーフレンドリーなエラーメッセージを設定
         setError(err instanceof Error ? err.message : 'ダッシュボード情報の取得中にエラーが発生しました。');
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []); // 初回レンダリング時にのみ実行

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}> {/* レスポンシブなパディング */}
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3 }}>
        管理者ダッシュボード
      </Typography>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      )}

      {summary && !loading && !error && (
        <Grid container spacing={3}>
          {/* サマリーカード */}
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard title="ユーザー数" value={summary.users_count} icon={<PeopleIcon />} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard title="チーム数" value={summary.teams_count} icon={<GroupIcon />} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard title="プレイヤー数" value={summary.players_count} icon={<PersonIcon />} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard title="トーナメント数" value={summary.tournaments_count} icon={<EmojiEventsIcon />} />
          </Grid>

          {/* 管理メニューへのリンク */}
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 2, mt: 2, borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom>
                管理メニュー
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                {/* TODO: 各管理機能へのリンクを実装 */}
                <Button
                  variant="outlined"
                  startIcon={<PeopleIcon />}
                  component={RouterLink}
                  to="/admin/users" // 仮のパス
                  disabled // 未実装のため無効化
                >
                  ユーザー管理
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                  component={RouterLink}
                  to="/admin/settings" // 仮のパス
                  disabled // 未実装のため無効化
                >
                  システム設定
                </Button>
                 <Button
                  variant="outlined"
                  startIcon={<HistoryIcon />}
                  component={RouterLink}
                  to="/admin/audit-logs" // 仮のパス
                  disabled // 未実装のため無効化
                >
                  監査ログ
                </Button>
                 {/* 他のメニュー項目 */}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* ルーティング設定が不明なため、ユーザーへの注意喚起 */}
      {!loading && (
        <Alert severity="info" sx={{ mt: 4 }}>
          <strong>開発者向け情報:</strong> このダッシュボードを表示するには、アプリケーションのルーティング設定ファイル（例: App.tsx, main.tsx, routes.tsxなど）に <code>/admin/dashboard</code> というパスを追加し、この <code>AdminDashboard</code> コンポーネントをレンダリングするように設定してください。また、管理者権限を持つユーザーのみがアクセスできるように、<code>PrivateRoute</code> や同様のガードコンポーネントでルートを保護する必要があります。
        </Alert>
      )}
    </Box>
  );
};

// デフォルトエクスポートを追加 (ファイルがモジュールとして認識されるように)
export default AdminDashboard;
