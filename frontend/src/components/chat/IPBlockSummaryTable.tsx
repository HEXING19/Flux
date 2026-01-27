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
import type { IPBlockSummary } from '../../types/ipblock';

interface IPBlockSummaryTableProps {
  data: IPBlockSummary;
}

const getBlockTypeText = (blockType: string): string => {
  const typeMap: Record<string, string> = {
    SRC_IP: '源IP',
    DST_IP: '目的IP',
    URL: 'URL链接',
    DNS: '域名',
  };
  return typeMap[blockType] || blockType;
};

const getDurationText = (data: IPBlockSummary): string => {
  if (data.time_type === 'forever') {
    return '永久封禁';
  } else if (data.time_value) {
    const unitMap: Record<string, string> = {
      d: '天',
      h: '小时',
      m: '分钟',
    };
    return `${data.time_value} ${unitMap[data.time_unit] || data.time_unit}`;
  }
  return '永久封禁';
};

const formatTimestamp = (timestamp: number): string => {
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const IPBlockSummaryTable: React.FC<IPBlockSummaryTableProps> = ({ data }) => {
  const rows = [
    { label: 'IP 地址', value: data.ip },
    {
      label: '封禁设备',
      value: `${data.device_name} (${data.device_type})`,
    },
    { label: '封禁类型', value: getBlockTypeText(data.block_type) },
    {
      label: '封禁时长',
      value: getDurationText(data),
      isChip: true,
      color: data.time_type === 'forever' ? 'error' : 'default',
    },
    {
      label: '创建规则数',
      value: String(data.rule_count),
      isChip: true,
      color: 'success',
    },
    {
      label: '封禁时间',
      value: formatTimestamp(data.timestamp),
    },
    data.reason && { label: '封禁原因', value: data.reason },
  ].filter(Boolean);

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <CheckCircleIcon color="success" fontSize="small" />
        <Typography variant="subtitle2" color="success.main" fontWeight={600}>
          IP封禁成功
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
