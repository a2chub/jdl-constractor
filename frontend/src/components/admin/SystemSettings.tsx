// frontend/src/components/admin/SystemSettings.tsx
import React, { useState, useEffect, useCallback } from 'react';
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
  IconButton,
  Tooltip,
  Snackbar, // Snackbarを追加
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';
import CancelIcon from '@mui/icons-material/Cancel';
// import DeleteIcon from '@mui/icons-material/Delete'; // 削除機能用

import { SystemSettingResponse, SystemSettingUpdate } from '../../types/system_setting';
import { getAllSystemSettings, updateSystemSetting } from '../../lib/api/admin'; // deleteSystemSetting も必要ならインポート

interface EditableSetting extends SystemSettingResponse {
  isEditing?: boolean;
  editValue?: any; // 編集中の値
}

export const SystemSettings: React.FC = () => {
  const [settings, setSettings] = useState<EditableSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<Record<string, boolean>>({}); // keyごとの保存状態
  const [snackbarOpen, setSnackbarOpen] = useState(false); // Snackbar表示状態
  const [snackbarMessage, setSnackbarMessage] = useState(''); // Snackbarメッセージ

  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getAllSystemSettings();
      setSettings(data.map(s => ({ ...s, isEditing: false, editValue: s.value })));
    } catch (err) {
      console.error("Failed to fetch system settings:", err);
      setError(err instanceof Error ? err.message : 'システム設定の取得中にエラーが発生しました。');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const handleEditToggle = (key: string) => {
    setSettings(prevSettings =>
      prevSettings.map(s =>
        s.key === key ? { ...s, isEditing: !s.isEditing, editValue: s.value } : { ...s, isEditing: false } // 他の行の編集はキャンセル
      )
    );
     setError(null); // 編集中はエラーをクリア
  };

  const handleValueChange = (key: string, newValue: any) => {
    setSettings(prevSettings =>
      prevSettings.map(s =>
        s.key === key ? { ...s, editValue: newValue } : s
      )
    );
  };

  const handleSave = async (key: string) => {
    const settingToSave = settings.find(s => s.key === key);
    if (!settingToSave || !settingToSave.isEditing) return;

    // 簡単なバリデーション（例：空でないか）を追加することも可能
    // if (settingToSave.editValue === null || settingToSave.editValue === '') {
    //   setError(`設定値 (${key}) は空にできません。`);
    //   return;
    // }

    setSaving(prev => ({ ...prev, [key]: true }));
    setError(null);

    try {
      // 値の型変換（例：文字列を数値に）
      let finalValue = settingToSave.editValue;
      const originalSetting = await getAllSystemSettings().then(all => all.find(s => s.key === key)); // 元の型情報を取得（非効率かも）
      if (originalSetting && typeof originalSetting.value === 'number') {
        const numValue = Number(finalValue);
        if (!isNaN(numValue)) {
          finalValue = numValue;
        } else {
          throw new Error(`設定値 (${key}) は数値である必要があります。`);
        }
      } else if (originalSetting && typeof originalSetting.value === 'boolean') {
         if (String(finalValue).toLowerCase() === 'true') finalValue = true;
         else if (String(finalValue).toLowerCase() === 'false') finalValue = false;
         else throw new Error(`設定値 (${key}) は true または false である必要があります。`);
      }
      // 他の型（JSONなど）のバリデーションもここに追加可能

      const updatePayload: SystemSettingUpdate = {
        value: finalValue,
      };
      const updatedSetting = await updateSystemSetting(key, updatePayload);

      // 保存成功したら状態を更新し、編集モードを解除
      setSettings(prevSettings =>
        prevSettings.map(s =>
          s.key === key ? { ...updatedSetting, isEditing: false, editValue: updatedSetting.value } : s // APIからの返り値で更新
        )
      );
      setSnackbarMessage(`設定 (${key}) を保存しました。`);
      setSnackbarOpen(true);
    } catch (err) {
      console.error(`Failed to save system setting ${key}:`, err);
      setError(err instanceof Error ? err.message : `設定 (${key}) の保存中にエラーが発生しました。`);
    } finally {
      setSaving(prev => ({ ...prev, [key]: false }));
    }
  };

   const handleSnackbarClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
     if (reason === 'clickaway') {
       return;
     }
     setSnackbarOpen(false);
   };

  // 削除ハンドラ (必要であれば)
  // const handleDelete = async (key: string) => { ... }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3 }}>
        システム設定
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}> {/* エラーを閉じれるように */}
          {error}
        </Alert>
      )}

      <TableContainer component={Paper} elevation={2}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', width: '20%' }}>キー</TableCell>
              <TableCell sx={{ fontWeight: 'bold', width: '40%' }}>値</TableCell>
              <TableCell sx={{ fontWeight: 'bold', width: '30%' }}>説明</TableCell>
              <TableCell sx={{ fontWeight: 'bold', textAlign: 'right', width: '10%' }}>アクション</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {settings.map((setting) => (
              <TableRow key={setting.key} hover>
                <TableCell sx={{ verticalAlign: 'top' }}>
                  <Typography variant="body2" sx={{ fontWeight: 'medium' }}>{setting.key}</Typography>
                </TableCell>
                <TableCell sx={{ verticalAlign: 'top' }}>
                  {setting.isEditing ? (
                    <TextField
                      variant="outlined"
                      size="small"
                      fullWidth
                      value={setting.editValue ?? ''}
                      onChange={(e) => handleValueChange(setting.key, e.target.value)}
                      // 型に応じた入力タイプ (例)
                      type={typeof setting.value === 'number' ? 'number' : 'text'}
                      multiline={typeof setting.value === 'string' && setting.value.length > 50} // 長い文字列は複数行
                      rows={typeof setting.value === 'string' && setting.value.length > 50 ? 3 : 1}
                      disabled={saving[setting.key]}
                      error={!!error && settings.find(s=>s.key===setting.key)?.isEditing} // エラー時に編集中なら枠を赤くする
                    />
                  ) : (
                    <Typography variant="body2" sx={{ wordBreak: 'break-all', whiteSpace: 'pre-wrap' }}>
                      {typeof setting.value === 'boolean' ? (setting.value ? '有効' : '無効') :
                       typeof setting.value === 'object' ? JSON.stringify(setting.value, null, 2) : // オブジェクトは整形表示
                       String(setting.value)}
                    </Typography>
                  )}
                </TableCell>
                <TableCell sx={{ verticalAlign: 'top' }}>
                  <Typography variant="body2" color="text.secondary">
                    {setting.description || '-'}
                  </Typography>
                </TableCell>
                <TableCell sx={{ verticalAlign: 'top', textAlign: 'right' }}>
                  {setting.isEditing ? (
                    <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
                      <Tooltip title="保存">
                        <span> {/* IconButtonが無効な場合にTooltipを表示するため */}
                          <IconButton
                            color="primary"
                            onClick={() => handleSave(setting.key)}
                            disabled={saving[setting.key]}
                            size="small"
                          >
                            {saving[setting.key] ? <CircularProgress size={20} color="inherit" /> : <SaveIcon fontSize="small" />}
                          </IconButton>
                        </span>
                      </Tooltip>
                      <Tooltip title="キャンセル">
                         <span>
                          <IconButton
                            color="default"
                            onClick={() => handleEditToggle(setting.key)}
                            disabled={saving[setting.key]}
                            size="small"
                          >
                            <CancelIcon fontSize="small" />
                          </IconButton>
                        </span>
                      </Tooltip>
                    </Box>
                  ) : (
                    <Tooltip title="編集">
                      <IconButton color="default" onClick={() => handleEditToggle(setting.key)} size="small">
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                  {/* 削除ボタン */}
                  {/*
                  <Tooltip title="削除">
                    <IconButton color="error" onClick={() => handleDelete(setting.key)} size="small" sx={{ ml: 0.5 }}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  */}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* ルーティング設定が不明なため、ユーザーへの注意喚起 */}
      <Alert severity="info" sx={{ mt: 4 }}>
        <strong>開発者向け情報:</strong> この設定画面を表示するには、アプリケーションのルーティング設定に <code>/admin/settings</code> パスを追加し、<code>SystemSettings</code> コンポーネントをレンダリングするように設定してください。管理者権限での保護も必要です。
      </Alert>

       {/* 保存成功メッセージ */}
       <Snackbar
         open={snackbarOpen}
         autoHideDuration={6000}
         onClose={handleSnackbarClose}
         message={snackbarMessage}
         anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
       />
    </Box>
  );
};

export default SystemSettings;
