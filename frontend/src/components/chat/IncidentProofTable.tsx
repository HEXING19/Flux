import React, { useState } from 'react';
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
  Card,
  CardContent,
  IconButton,
  Collapse,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import type { IncidentProofTableProps } from '../../types/incidentProof';

const getSeverityInfo = (severity: number) => {
  const severityMap: Record<number, { label: string; color: 'info' | 'success' | 'warning' | 'error' | 'default'; icon: string }> = {
    0: { label: '信息', color: 'info', icon: '🔵' },
    1: { label: '低危', color: 'success', icon: '🟢' },
    2: { label: '中危', color: 'warning', icon: '🟡' },
    3: { label: '高危', color: 'warning', icon: '🟠' },
    4: { label: '严重', color: 'error', icon: '🔴' },
  };
  return severityMap[severity] || { label: '未知', color: 'default', icon: '⚪' };
};

const getDealStatusInfo = (
  status: number,
  dealAction?: string
): { label: string; color: 'default' | 'info' | 'success' | 'warning' } => {
  const statusMap: Record<number, { label: string; color: 'default' | 'info' | 'success' | 'warning' }> = {
    0: { label: '待处置', color: 'default' },
    10: { label: '处置中', color: 'info' },
    30: { label: '已遏制', color: 'success' },
    40: { label: '已处置', color: 'success' },
    50: { label: '已挂起', color: 'default' },
    60: { label: '接受风险', color: 'warning' },
    // Backward compatibility for historical data
    70: { label: '已遏制', color: 'success' },
  };
  if (statusMap[status]) {
    return statusMap[status];
  }
  if (dealAction) {
    return { label: dealAction, color: 'default' };
  }
  return { label: `未知(${status})`, color: 'default' };
};

const getStageInfo = (stage: number) => {
  const stageMap: Record<number, string> = {
    10: '侦察探测',
    20: '武器构建',
    30: '投递载荷',
    40: '利用漏洞',
    50: '安装后门',
    60: '命令控制',
    70: '执行目标',
    80: '窃取数据',
  };
  return stageMap[stage] || '未知阶段';
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

interface AlertCardProps {
  alert: any;
  index: number;
}

const AlertCard: React.FC<AlertCardProps> = ({ alert, index }) => {
  const [expanded, setExpanded] = useState(false);

  const severityInfo = getSeverityInfo(alert.severity);
  const stageInfo = getStageInfo(alert.stage);

  return (
    <Card sx={{ mb: 1 }} elevation={0}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          p: 1.5,
          cursor: 'pointer',
          '&:hover': { bgcolor: 'grey.50' },
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <IconButton size="small" sx={{ mr: 1 }}>
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
        <Typography variant="body2" sx={{ flexGrow: 1 }}>
          {index + 1}. {alert.name}
        </Typography>
        <Chip
          label={severityInfo.label}
          color={severityInfo.color}
          size="small"
          sx={{ mr: 1 }}
        />
        <Typography variant="caption" color="text.secondary">
          {alert.severity}分
        </Typography>
      </Box>
      <Collapse in={expanded}>
        <CardContent sx={{ pt: 0, pl: 5 }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
            <Typography variant="caption" color="text.secondary">
              告警ID: {alert.alertId}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              分类: {alert.threatSubTypeDesc}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              阶段: {stageInfo}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              时间: {formatTimestamp(alert.lastTime)}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ gridColumn: '1 / -1' }}>
              来源: {alert.devSourceNames?.join(', ') || '未知'}
            </Typography>
          </Box>
        </CardContent>
      </Collapse>
    </Card>
  );
};

export const IncidentProofTable: React.FC<IncidentProofTableProps> = ({ data }) => {
  const dealStatusInfo = getDealStatusInfo(data.dealStatus ?? -1, data.dealAction);
  const severityInfo = getSeverityInfo(data.severity);

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <WarningIcon color="error" fontSize="small" />
        <Typography variant="subtitle2" color="text.primary" fontWeight={600}>
          事件详情
        </Typography>
      </Box>

      {/* Summary Table */}
      <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider', mb: 2 }}>
        <Table size="small">
          <TableBody>
            <TableRow>
              <TableCell sx={{ fontWeight: 600, width: '30%' }}>事件名称</TableCell>
              <TableCell>{data.name}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell sx={{ fontWeight: 600 }}>事件ID</TableCell>
              <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                {data.uuId}
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell sx={{ fontWeight: 600 }}>严重等级</TableCell>
              <TableCell>
                <Chip
                  label={`${severityInfo.icon} ${severityInfo.label}`}
                  color={severityInfo.color}
                  size="small"
                />
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell sx={{ fontWeight: 600 }}>发生时间</TableCell>
              <TableCell>{formatTimestamp(data.endTime)}</TableCell>
            </TableRow>
            {data.eventThreatDefine && data.eventThreatDefine.length > 0 && (
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>威胁定性</TableCell>
                <TableCell>
                  {data.eventThreatDefine.map((tag, idx) => (
                    <Chip key={idx} label={tag} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                  ))}
                </TableCell>
              </TableRow>
            )}
            {data.dataSource && data.dataSource.length > 0 && (
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>数据源</TableCell>
                <TableCell>{data.dataSource.join(', ')}</TableCell>
              </TableRow>
            )}
            {data.riskTag && data.riskTag.length > 0 && (
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>标签</TableCell>
                <TableCell>
                  {data.riskTag.map((tag, idx) => (
                    <Chip
                      key={idx}
                      label={tag}
                      variant="outlined"
                      size="small"
                      sx={{ mr: 0.5, mb: 0.5 }}
                    />
                  ))}
                </TableCell>
              </TableRow>
            )}
            <TableRow>
              <TableCell sx={{ fontWeight: 600 }}>处置状态</TableCell>
              <TableCell>
                <Chip
                  label={dealStatusInfo.label}
                  color={dealStatusInfo.color}
                  size="small"
                  variant="outlined"
                />
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>

      {/* Timeline Section */}
      {data.alertTimeLine && data.alertTimeLine.length > 0 && (
        <Box>
          <Typography variant="subtitle2" color="text.primary" fontWeight={600} sx={{ mb: 1 }}>
            告警时间线（共{data.alertTimeLine.length}个告警）
          </Typography>
          {data.alertTimeLine.map((alert, index) => (
            <AlertCard key={alert.alertId} alert={alert} index={index} />
          ))}
        </Box>
      )}
    </Box>
  );
};
