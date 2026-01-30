/**
 * Status Indicator Component
 * Displays system status with Material Design style
 */

import { Box, Typography, Chip } from '@mui/material';
import { FiberManualRecord } from '@mui/icons-material';
import type { SystemStatus } from '../../../types/cockpit';

interface StatusIndicatorProps {
  status: SystemStatus;
  lastUpdate?: number;
}

const statusConfig = {
  online: {
    label: '在线',
    color: 'success' as const,
  },
  warning: {
    label: '警告',
    color: 'warning' as const,
  },
  offline: {
    label: '离线',
    color: 'error' as const,
  },
};

export function StatusIndicator({ status, lastUpdate }: StatusIndicatorProps) {
  const config = statusConfig[status];

  // Format last update time
  const formatLastUpdate = (timestamp: number) => {
    const now = Date.now();
    const diff = now - timestamp * 1000;
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}小时前`;
    const days = Math.floor(hours / 24);
    return `${days}天前`;
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
      {/* Status Dot */}
      <FiberManualRecord
        sx={{
          fontSize: 12,
          color: config.color === 'success' ? '#527A50' : config.color === 'warning' ? '#F2B8B5' : '#B3261E',
        }}
      />

      {/* Status Chip */}
      <Chip
        label={config.label}
        size="small"
        color={config.color}
        variant="filled"
      />

      {/* Last Update */}
      {lastUpdate && (
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          更新于 {formatLastUpdate(lastUpdate)}
        </Typography>
      )}
    </Box>
  );
}
