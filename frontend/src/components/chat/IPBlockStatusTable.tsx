import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Collapse,
  IconButton,
  Chip,
  Alert,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import BlockIcon from '@mui/icons-material/Block';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import type { IPBlockStatus, IPBlockRule } from '../../types/ipblock';

interface IPBlockStatusTableProps {
  status: IPBlockStatus;
  ip: string;
}

interface RuleRowProps {
  rule: IPBlockRule;
}

const RuleRow: React.FC<RuleRowProps> = ({ rule }) => {
  const [open, setOpen] = useState(false);

  const getStatusColor = (status: string) => {
    if (status.includes('block success')) return 'success';
    if (status.includes('block failed')) return 'error';
    if (status.includes('unblocked')) return 'default';
    return 'warning';
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      'block success': '已封禁',
      'block failed': '封禁失败',
      'unblocked': '已解封',
      'part block success': '部分封禁成功',
      'part unblock success': '部分解封成功',
      'block ip in deal': '封禁中',
      'unblock ip in deal': '解封中',
    };
    return statusMap[status] || status;
  };

  const formatDate = (timestamp: number) => {
    if (!timestamp) return '-';
    return new Date(timestamp * 1000).toLocaleString('zh-CN');
  };

  return (
    <>
      <TableRow hover>
        <TableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
          {rule.name || '-'}
        </TableCell>
        <TableCell>
          <Chip label={getStatusText(rule.status)} color={getStatusColor(rule.status) as any} size="small" />
        </TableCell>
        <TableCell>{rule.blockIpMethod || '-'}</TableCell>
        <TableCell>{rule.blockIpTimeRange || '-'}</TableCell>
        <TableCell>{formatDate(rule.createTime)}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 2 }}>
              <Typography variant="h6" gutterBottom component="div">
                规则详情
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        基本信息
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        <strong>规则ID:</strong> {rule.id}
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        <strong>创建人:</strong> {rule.createUser || '-'}
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        <strong>备注:</strong> {rule.reason || '无'}
                      </Typography>
                      <Typography variant="body2">
                        <strong>更新时间:</strong> {formatDate(rule.updateTime)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        封禁对象
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        <strong>类型:</strong> {rule.blockIpRule?.type || '-'}
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        <strong>模式:</strong> {rule.blockIpRule?.mode || '-'}
                      </Typography>
                      <Typography variant="body2">
                        <strong>封禁内容:</strong>
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        {rule.blockIpRule?.view?.map((item, index) => (
                          <Chip
                            key={index}
                            label={item}
                            size="small"
                            sx={{ mr: 0.5, mb: 0.5 }}
                            color="error"
                          />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

export const IPBlockStatusTable: React.FC<IPBlockStatusTableProps> = ({ status, ip }) => {
  const { blocked, rules = [], devices = [], total_rules = 0 } = status;

  if (!blocked) {
    return (
      <Alert severity="info" icon={<CancelIcon />}>
        <Typography variant="body1">
          IP地址 <strong>{ip}</strong> 当前未被封禁
        </Typography>
      </Alert>
    );
  }

  return (
    <Box>
      <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 2 }}>
        <Typography variant="body1">
          IP地址 <strong>{ip}</strong> 已被封禁，共找到 {total_rules} 条封禁规则
        </Typography>
      </Alert>

      {/* 规则列表 */}
      <Paper sx={{ width: '100%', mb: 2, overflow: 'hidden' }}>
        <Typography variant="h6" sx={{ p: 2, backgroundColor: 'grey.100' }}>
          <BlockIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
          封禁规则列表
        </Typography>
        <TableContainer>
          <Table aria-label="block rules table" size="small">
            <TableHead>
              <TableRow>
                <TableCell />
                <TableCell><strong>规则名称</strong></TableCell>
                <TableCell><strong>状态</strong></TableCell>
                <TableCell><strong>封禁方式</strong></TableCell>
                <TableCell><strong>封禁时长</strong></TableCell>
                <TableCell><strong>创建时间</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rules.map((rule) => (
                <RuleRow key={rule.id} rule={rule} />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* 设备列表 */}
      {devices.length > 0 && (
        <Paper sx={{ width: '100%', overflow: 'hidden' }}>
          <Typography variant="h6" sx={{ p: 2, backgroundColor: 'grey.100' }}>
            联动设备列表
          </Typography>
          <TableContainer>
            <Table aria-label="devices table" size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>设备名称</strong></TableCell>
                  <TableCell><strong>设备类型</strong></TableCell>
                  <TableCell><strong>设备版本</strong></TableCell>
                  <TableCell><strong>设备IP</strong></TableCell>
                  <TableCell><strong>状态</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {devices.map((device, index) => (
                  <TableRow key={index} hover>
                    <TableCell>{device.deviceName || '-'}</TableCell>
                    <TableCell>{device.deviceType || '-'}</TableCell>
                    <TableCell>{device.devVersion || '-'}</TableCell>
                    <TableCell>{device.devIp || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={device.failMessage ? '失败' : '成功'}
                        color={device.failMessage ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  );
};
