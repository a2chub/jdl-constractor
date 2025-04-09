/**
 * チーム管理画面コンポーネント
 * 
 * @description
 * チームの基本情報、メンバー管理、権限管理などの機能を提供します。
 * また、権限変更履歴を表示する機能も含まれています。
 */
import React from 'react';
import { Box, Typography, Divider } from '@mui/material';
import TeamBasicInfo from './TeamBasicInfo';
import TeamMemberList from './TeamMemberList';
import TeamPermissionManagement from './TeamPermissionManagement';
import { TeamPermissionHistory } from './TeamPermissionHistory';

interface TeamManagementProps {
  teamId: string;
}

export const TeamManagement: React.FC<TeamManagementProps> = ({ teamId }) => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        チーム管理
      </Typography>

      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          基本情報
        </Typography>
        <TeamBasicInfo teamId={teamId} />
      </Box>

      <Divider sx={{ my: 4 }} />

      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          メンバー管理
        </Typography>
        <TeamMemberList teamId={teamId} />
      </Box>

      <Divider sx={{ my: 4 }} />

      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          権限管理
        </Typography>
        <TeamPermissionManagement teamId={teamId} />
      </Box>

      <Divider sx={{ my: 4 }} />

      <Box>
        <Typography variant="h5" component="h2" gutterBottom>
          権限変更履歴
        </Typography>
        <TeamPermissionHistory teamId={teamId} />
      </Box>
    </Box>
  );
}; 