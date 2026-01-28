import React from 'react';
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
  Chip,
  Collapse,
  IconButton,
  Stack,
} from '@mui/material';
import PublicIcon from '@mui/icons-material/Public';
import SecurityIcon from '@mui/icons-material/Security';
import BlockIcon from '@mui/icons-material/Block';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { getThreatLevelInfo, getNDRStatusInfo, formatExpireTime, isIPBlocked } from '../../types/incidentEntities';
import type { IncidentEntitiesTableProps } from '../../types/incidentEntities';

const getThreatColor = (level: number): 'info' | 'success' | 'warning' | 'error' => {
  const colorMap: Record<number, 'info' | 'success' | 'warning' | 'error'> = {
    0: 'info',
    1: 'success',
    2: 'warning',
    3: 'error',
  };
  return colorMap[level] || 'info';
};

export const IncidentEntitiesTable: React.FC<IncidentEntitiesTableProps> = ({
  entities,
  incidentId,
  onBlockIP,
}) => {
  const [expandedRow, setExpandedRow] = React.useState<string | null>(null);

  if (!entities || entities.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center', color: 'text.secondary' }}>
        <Typography variant="body2">该事件暂无外网IP实体记录</Typography>
      </Box>
    );
  }

  const handleToggleRow = (ip: string) => {
    setExpandedRow(expandedRow === ip ? null : ip);
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          🌐 事件外网IP实体
        </Typography>
        {incidentId && (
          <Typography variant="caption" color="text.secondary">
            事件ID: {incidentId}
          </Typography>
        )}
        <Typography variant="caption" color="text.secondary" display="block">
          找到 {entities.length} 个外网IP实体
        </Typography>
      </Box>

      {/* Table */}
      <TableContainer component={Paper} elevation={1}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>IP地址</TableCell>
              <TableCell>威胁等级</TableCell>
              <TableCell>地理位置</TableCell>
              <TableCell>情报标签</TableCell>
              <TableCell>处置状态</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {entities.map((entity, index) => {
              const threatInfo = getThreatLevelInfo(entity.threatLevel);
              const isBlocked = isIPBlocked(entity);
              const isExpanded = expandedRow === entity.ip;

              return (
                <React.Fragment key={entity.id || entity.ip || index}>
                  <TableRow
                    hover
                    sx={{
                      '&:last-child td, &:last-child th': { border: 0 },
                      backgroundColor: entity.threatLevel >= 2 && !isBlocked ? 'error.lighter' : 'inherit',
                    }}
                  >
                    <TableCell component="th" scope="row">
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Typography variant="body2" fontWeight="medium">
                          {entity.ip}
                        </Typography>
                        {entity.threatLevel >= 2 && !isBlocked && (
                          <Chip label="需要处置" color="error" size="small" />
                        )}
                      </Stack>
                      <Typography variant="caption" color="text.secondary">
                        端口: {entity.port || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={<SecurityIcon />}
                        label={`${threatInfo.emoji} ${threatInfo.label}`}
                        color={getThreatColor(entity.threatLevel)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <PublicIcon fontSize="small" color="action" />
                        <Typography variant="body2">
                          {entity.location || '-'}
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      {entity.intelligenceTag && entity.intelligenceTag.length > 0 ? (
                        <Stack direction="row" spacing={0.5} flexWrap="wrap">
                          {entity.intelligenceTag.map((tag, idx) => (
                            <Chip
                              key={idx}
                              label={tag}
                              size="small"
                              color="error"
                              variant="outlined"
                            />
                          ))}
                        </Stack>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          -
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {entity.ndrDealStatusInfo ? (
                          <>
                            {getNDRStatusInfo(entity.ndrDealStatusInfo.status).icon}{' '}
                            {getNDRStatusInfo(entity.ndrDealStatusInfo.status).label}
                          </>
                        ) : (
                          '暂无'
                        )}
                      </Typography>
                      {entity.ndrDealStatusInfo?.expireTime && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          {entity.ndrDealStatusInfo.isPermanent ? '永久' : formatExpireTime(entity.ndrDealStatusInfo.expireTime)}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1}>
                        <IconButton
                          size="small"
                          onClick={() => handleToggleRow(entity.ip)}
                        >
                          {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                        {onBlockIP && (
                          <Chip
                            icon={<BlockIcon />}
                            label={isBlocked ? '已封禁' : '封禁'}
                            color={isBlocked ? 'default' : 'error'}
                            size="small"
                            onClick={() => !isBlocked && onBlockIP(entity.ip)}
                            sx={{ cursor: isBlocked ? 'default' : 'pointer' }}
                          />
                        )}
                      </Stack>
                    </TableCell>
                  </TableRow>

                  {/* Expanded Row - Details */}
                  <TableRow>
                    <TableCell colSpan={6} sx={{ pb: 0, pt: 0 }}>
                      <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                        <Box sx={{ p: 2, bgcolor: 'action.hover' }}>
                          <Typography variant="subtitle2" gutterBottom>
                            详细信息
                          </Typography>

                          <Stack spacing={1}>
                            <Typography variant="caption" color="text.secondary">
                              运营商归属: {entity.asLabel || '-'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              测绘标签: {entity.mappingTag || '-'}
                            </Typography>
                            {entity.alertRole && (
                              <Typography variant="caption" color="text.secondary">
                                告警角色: {entity.alertRole}
                              </Typography>
                            )}
                            {entity.srcProcess && entity.srcProcess.length > 0 && (
                              <>
                                <Typography variant="caption" fontWeight="bold">
                                  关联进程:
                                </Typography>
                                {entity.srcProcess.map((process, idx) => (
                                  <Box key={idx} sx={{ ml: 2, p: 1, bgcolor: 'background.paper', borderRadius: 1 }}>
                                    <Typography variant="caption" display="block">
                                      {process.pName} (PID: {process.pid})
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary" fontFamily="monospace">
                                      MD5: {process.md5}
                                    </Typography>
                                  </Box>
                                ))}
                              </>
                            )}
                            {entity.dealSuggestion && (
                              <>
                                <Typography variant="caption" fontWeight="bold" display="block">
                                  处置建议:
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {entity.dealSuggestion}
                                </Typography>
                              </>
                            )}
                            {entity.businessAffection && (
                              <>
                                <Typography variant="caption" fontWeight="bold" display="block">
                                  业务影响:
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {entity.businessAffection}
                                </Typography>
                              </>
                            )}
                          </Stack>
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default IncidentEntitiesTable;
