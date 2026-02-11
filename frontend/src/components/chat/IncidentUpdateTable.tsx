import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Paper,
  Typography,
  Chip,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import type { IncidentUpdateTableProps } from '../../types/incidentUpdate';

const getDealStatusInfo = (status: number) => {
  const statusMap: Record<number, { label: string; color: 'default' | 'info' | 'success' | 'warning' | 'error' }> = {
    0: { label: '待处置', color: 'default' },
    10: { label: '处置中', color: 'info' },
    30: { label: '已遏制', color: 'success' },
    40: { label: '已处置', color: 'success' },
    50: { label: '已挂起', color: 'default' },
    60: { label: '接受风险', color: 'warning' },
    // Backward compatibility for historical data
    70: { label: '已遏制', color: 'success' },
  };
  return statusMap[status] || { label: `未知(${status})`, color: 'default' };
};

export const IncidentUpdateTable: React.FC<IncidentUpdateTableProps> = ({ data }) => {
  const statusInfo = getDealStatusInfo(data.statusValue);

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <CheckCircleIcon
          color={data.succeededNum > 0 ? 'success' : data.failedNum > 0 ? 'error' : 'disabled'}
          fontSize="small"
        />
        <Typography variant="subtitle2" color="text.primary" fontWeight={600}>
          批量更新结果
        </Typography>
      </Box>

      {/* Summary Table */}
      <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
        <Table size="small">
          <TableBody>
            <TableRow>
              <TableCell sx={{ fontWeight: 600, width: '30%' }}>总事件数</TableCell>
              <TableCell>{data.total}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell sx={{ fontWeight: 600 }}>成功更新</TableCell>
              <TableCell>
                <Chip
                  label={data.succeededNum}
                  color={data.succeededNum > 0 ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell sx={{ fontWeight: 600 }}>更新失败</TableCell>
              <TableCell>
                <Chip
                  label={data.failedNum}
                  color={data.failedNum > 0 ? 'error' : 'default'}
                  size="small"
                />
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell sx={{ fontWeight: 600 }}>目标状态</TableCell>
              <TableCell>
                <Chip
                  label={data.statusName}
                  color={statusInfo.color}
                  size="small"
                  variant="outlined"
                />
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
