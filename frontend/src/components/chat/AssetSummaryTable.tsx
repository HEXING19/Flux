import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Paper,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import type { AssetSummary } from '../../types/asset';

interface AssetSummaryTableProps {
  data: AssetSummary;
}

const getCategoryName = (classify1Id?: number): string => {
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

const getMagnitudeColor = (magnitude?: string): 'error' | 'default' => {
  return magnitude === 'core' ? 'error' : 'default';
};

const getMagnitudeLabel = (magnitude?: string): string => {
  return magnitude === 'core' ? '核心' : '普通';
};

export const AssetSummaryTable: React.FC<AssetSummaryTableProps> = ({ data }) => {
  const rows = [
    { label: 'IP 地址', value: data.ip },
    data.assetName && { label: '资产名称', value: data.assetName },
    data.type && { label: '操作系统', value: data.type },
    { label: '资产分类', value: getCategoryName(data.classify1Id) },
    {
      label: '重要级别',
      value: getMagnitudeLabel(data.magnitude),
      isChip: true,
      color: getMagnitudeColor(data.magnitude)
    },
    { label: '资产组', value: String(data.branchId || 0) },
  ].filter(Boolean);

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <CheckCircleIcon color="success" fontSize="small" />
        <Typography variant="subtitle2" color="success.main" fontWeight={600}>
          资产添加成功
        </Typography>
      </Box>

      <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
        <Table size="small">
          <TableBody>
            {rows.map((row: any, index) => (
              <TableRow key={index} sx={{ '&:last-child td': { border: 0 } }}>
                <TableCell
                  component="th"
                  scope="row"
                  sx={{ fontWeight: 600, width: '30%', bgcolor: 'grey.50' }}
                >
                  {row.label}
                </TableCell>
                <TableCell>
                  {row.isChip ? (
                    <Chip label={row.value} color={row.color} size="small" />
                  ) : (
                    row.value
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
