import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Divider,
  CircularProgress,
} from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import CancelIcon from '@mui/icons-material/Cancel';
import type { AssetParams } from '../../types/asset';

interface AssetConfirmationDialogProps {
  open: boolean;
  params: AssetParams | null;
  onConfirm: (updatedParams: AssetParams) => void;
  onCancel: () => void;
  loading?: boolean;
}

export const AssetConfirmationDialog: React.FC<AssetConfirmationDialogProps> = ({
  open,
  params,
  onConfirm,
  onCancel,
  loading = false,
}) => {
  const [editableParams, setEditableParams] = useState<AssetParams>({
    ip: '',
    branchId: 0,
  });

  useEffect(() => {
    if (params) {
      setEditableParams(params);
    }
  }, [params]);

  const handleFieldChange = (field: keyof AssetParams, value: any) => {
    setEditableParams((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const getCategoryName = (classify1Id?: number) => {
    const categories: Record<number, string> = {
      0: '未知',
      1: '服务器',
      2: '终端',
      5: '网络设备',
      6: 'IoT设备',
      7: '移动设备',
      8: '安全设备',
    };
    return categories[classify1Id || 0] || '未知';
  };

  const getMagnitudeName = (magnitude?: string) => {
    return magnitude === 'core' ? '核心' : '普通';
  };

  if (!params) return null;

  return (
    <Dialog open={open} onClose={onCancel} maxWidth="sm" fullWidth>
      <DialogTitle>确认添加资产</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          我识别到您想添加以下资产，请确认信息：
        </Typography>

        <Divider sx={{ my: 2 }} />

        {/* 可编辑字段 */}
        <TextField
          label="IP 地址"
          value={editableParams.ip}
          onChange={(e) => handleFieldChange('ip', e.target.value)}
          fullWidth
          margin="normal"
          required
          disabled={loading}
        />

        <TextField
          label="资产名称"
          value={editableParams.assetName || ''}
          onChange={(e) => handleFieldChange('assetName', e.target.value)}
          fullWidth
          margin="normal"
          disabled={loading}
          placeholder="可选"
        />

        <Divider sx={{ my: 2 }} />

        {/* 只读字段 */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Typography variant="body2">
            <strong>操作系统：</strong>
            {editableParams.type || 'Unknown'}
          </Typography>

          <Typography variant="body2">
            <strong>资产分类：</strong>
            {getCategoryName(editableParams.classify1Id)}
          </Typography>

          <Typography variant="body2">
            <strong>重要级别：</strong>
            {getMagnitudeName(editableParams.magnitude)}
          </Typography>

          <Typography variant="body2">
            <strong>资产组：</strong>
            {editableParams.branchId}
          </Typography>

          {editableParams.mac && (
            <Typography variant="body2">
              <strong>MAC 地址：</strong>
              {editableParams.mac}
            </Typography>
          )}

          {editableParams.hostName && (
            <Typography variant="body2">
              <strong>主机名：</strong>
              {editableParams.hostName}
            </Typography>
          )}

          {editableParams.tags && editableParams.tags.length > 0 && (
            <Typography variant="body2">
              <strong>标签：</strong>
              {editableParams.tags.join(', ')}
            </Typography>
          )}

          {editableParams.comment && (
            <Typography variant="body2">
              <strong>备注：</strong>
              {editableParams.comment}
            </Typography>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={onCancel}
          disabled={loading}
          startIcon={<CancelIcon />}
        >
          取消
        </Button>
        <Button
          onClick={() => onConfirm(editableParams)}
          variant="contained"
          disabled={loading || !editableParams.ip}
          startIcon={loading ? <CircularProgress size={20} /> : <CheckIcon />}
        >
          {loading ? '添加中...' : '确认添加'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
