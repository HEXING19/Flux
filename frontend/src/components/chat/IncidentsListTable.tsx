import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Chip,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import type { IncidentsListTableProps } from '../../types/incidents';

const getSeverityInfo = (severity: number) => {
  const severityMap = {
    0: { label: '信息', color: 'info' as const, icon: '🔵' },
    1: { label: '低危', color: 'success' as const, icon: '🟢' },
    2: { label: '中危', color: 'warning' as const, icon: '🟡' },
    3: { label: '高危', color: 'warning' as const, icon: '🟠' },
    4: { label: '严重', color: 'error' as const, icon: '🔴' },
  };
  return severityMap[severity] || { label: '未知', color: 'default' as const, icon: '⚪' };
};

const getDealStatusInfo = (status: number) => {
  const statusMap = {
    0: { label: '待处置', color: 'default' as const },
    10: { label: '处置中', color: 'info' as const },
    30: { label: '已防护', color: 'success' as const },
    40: { label: '已处置', color: 'success' as const },
    50: { label: '已挂起', color: 'default' as const },
    60: { label: '接受风险', color: 'warning' as const },
    70: { label: '已遏制', color: 'success' as const },
  };
  return statusMap[status] || { label: '未知', color: 'default' as const };
};

const formatTimestamp = (timestamp: number): string => {
  if (!timestamp || timestamp === 0) return '未知';
  return new Date(timestamp * 1000).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const IncidentsListTable: React.FC<IncidentsListTableProps> = ({ incidents, total }) => {
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <WarningIcon color="error" fontSize="small" />
        <Typography variant="subtitle2" color="text.primary" fontWeight={600}>
          查询成功！找到 {total} 条安全事件
        </Typography>
      </Box>

      <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ bgcolor: 'grey.50' }}>
              <TableCell sx={{ fontWeight: 600 }}>序号</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>事件名称</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>等级</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>主机IP</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>时间</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>状态</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {incidents.slice(0, 10).map((incident, index) => {
              const severityInfo = getSeverityInfo(incident.incidentSeverity);
              const dealStatusInfo = getDealStatusInfo(incident.dealStatus ?? 0);
              return (
                <TableRow key={incident.uuId} hover>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {incident.name}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${severityInfo.icon} ${severityInfo.label}`}
                      color={severityInfo.color}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{incident.hostIp || '未知'}</TableCell>
                  <TableCell>{formatTimestamp(incident.endTime)}</TableCell>
                  <TableCell>
                    <Chip
                      label={dealStatusInfo.label}
                      color={dealStatusInfo.color}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {total > 10 && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          显示前10条，共{total}条
        </Typography>
      )}
    </Box>
  );
};
