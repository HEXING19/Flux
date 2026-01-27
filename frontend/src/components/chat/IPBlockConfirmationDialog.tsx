import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Divider,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import CancelIcon from '@mui/icons-material/Cancel';
import BlockIcon from '@mui/icons-material/Block';
import type { IPBlockParams } from '../../types/ipblock';

interface IPBlockConfirmationDialogProps {
  open: boolean;
  params: IPBlockParams | null;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
  error?: string | null;
}

export const IPBlockConfirmationDialog: React.FC<IPBlockConfirmationDialogProps> = ({
  open,
  params,
  onConfirm,
  onCancel,
  loading = false,
  error = null,
}) => {
  if (!params) return null;

  const getDurationText = () => {
    if (params.time_type === 'forever') {
      return '永久封禁';
    } else if (params.time_value) {
      const unitMap: Record<string, string> = {
        d: '天',
        h: '小时',
        m: '分钟',
      };
      return `${params.time_value} ${unitMap[params.time_unit] || params.time_unit}`;
    }
    return '永久封禁';
  };

  const getBlockTypeText = () => {
    const typeMap: Record<string, string> = {
      SRC_IP: '源IP',
      DST_IP: '目的IP',
      URL: 'URL链接',
      DNS: '域名',
    };
    return typeMap[params.block_type] || params.block_type;
  };

  return (
    <Dialog open={open} onClose={onCancel} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <BlockIcon color="error" />
          确认IP封禁
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          我将为您执行以下IP封禁操作，请确认信息：
        </Typography>

        <Divider sx={{ my: 2 }} />

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* 封禁参数列表 */}
        <List>
          <ListItem>
            <ListItemText
              primary="IP 地址"
              secondary={params.ip}
              primaryTypographyProps={{ variant: 'subtitle2', color: 'text.primary' }}
              secondaryTypographyProps={{ variant: 'body1', fontWeight: 'bold', color: 'error.main' }}
            />
          </ListItem>

          <ListItem>
            <ListItemText
              primary="封禁设备"
              secondary={`${params.device_name} (${params.device_type})`}
              primaryTypographyProps={{ variant: 'subtitle2', color: 'text.primary' }}
              secondaryTypographyProps={{ variant: 'body1' }}
            />
          </ListItem>

          <ListItem>
            <ListItemText
              primary="封禁类型"
              secondary={getBlockTypeText()}
              primaryTypographyProps={{ variant: 'subtitle2', color: 'text.primary' }}
              secondaryTypographyProps={{ variant: 'body1' }}
            />
          </ListItem>

          <ListItem>
            <ListItemText
              primary="封禁时长"
              secondary={getDurationText()}
              primaryTypographyProps={{ variant: 'subtitle2', color: 'text.primary' }}
              secondaryTypographyProps={{ variant: 'body1' }}
            />
          </ListItem>

          {params.reason && (
            <ListItem>
              <ListItemText
                primary="封禁原因"
                secondary={params.reason}
                primaryTypographyProps={{ variant: 'subtitle2', color: 'text.primary' }}
                secondaryTypographyProps={{ variant: 'body1' }}
              />
            </ListItem>
          )}

          {params.device_status && (
            <ListItem>
              <ListItemText
                primary="设备状态"
                secondary={
                  params.device_status === 'online' ? '在线' : `离线 (${params.device_status})`
                }
                primaryTypographyProps={{ variant: 'subtitle2', color: 'text.primary' }}
                secondaryTypographyProps={{
                  variant: 'body1',
                  color: params.device_status === 'online' ? 'success.main' : 'error.main',
                }}
              />
            </ListItem>
          )}
        </List>

        <Alert severity="warning" sx={{ mt: 2 }}>
          <Typography variant="body2">
            ⚠️ 封禁操作将立即生效，请确保IP地址和设备信息正确无误
          </Typography>
        </Alert>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button
          onClick={onCancel}
          disabled={loading}
          startIcon={<CancelIcon />}
          color="secondary"
        >
          取消
        </Button>
        <Button
          onClick={onConfirm}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <CheckIcon />}
          variant="contained"
          color="error"
          autoFocus
        >
          {loading ? '执行中...' : '确认封禁'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
