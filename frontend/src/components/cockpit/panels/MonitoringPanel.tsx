/**
 * Monitoring Panel Component
 * Displays real-time system monitoring data with Material Design style
 */

import { Box, Typography, Paper, Grid, List, ListItem, ListItemText, Chip } from '@mui/material';
import { Speed, NotificationImportant, AccessTime } from '@mui/icons-material';
import { StatusIndicator } from '../cards/StatusIndicator';
import { StatCard } from '../cards/StatCard';
import type { MonitoringData } from '../../../types/cockpit';

interface MonitoringPanelProps {
  monitoring: MonitoringData | null;
  loading?: boolean;
}

export function MonitoringPanel({ monitoring, loading = false }: MonitoringPanelProps) {
  // Format timestamp to relative time
  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get severity color (MD3 colors)
  const getSeverityColor = (severity: number) => {
    if (severity >= 4) return 'error';    // 严重 - Red
    if (severity >= 3) return 'warning';  // 高危 - Orange
    if (severity >= 2) return 'info';     // 中危 - Blue
    return 'success';                     // 低危 - Green
  };

  // Get severity label
  const getSeverityLabel = (severity: number) => {
    const labels = ['未知', '低危', '中危', '高危', '严重'];
    return labels[severity] || '未知';
  };

  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        borderRadius: 4, // 16px
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Speed color="primary" />
          <Typography variant="h6" component="h2">
            实时监控
          </Typography>
        </Box>

        {/* System Status */}
        {!loading && monitoring && (
          <StatusIndicator
            status={monitoring.systemStatus}
            lastUpdate={monitoring.lastUpdate}
          />
        )}
      </Box>

      {loading ? (
        <Box sx={{ textAlign: 'center', py: 4, flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            加载监控数据...
          </Typography>
        </Box>
      ) : monitoring ? (
        <>
          {/* Stats Grid */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {/* Active Alerts */}
            <Grid item xs={12} sm={6}>
              <StatCard
                title="活跃告警"
                value={monitoring.activeAlerts}
                unit="个"
                icon={<NotificationImportant />}
                color="error"
              />
            </Grid>

            {/* API Latency */}
            {monitoring.performanceMetrics && (
              <Grid item xs={12} sm={6}>
                <StatCard
                  title="API延迟"
                  value={monitoring.performanceMetrics.apiLatency}
                  unit="ms"
                  icon={<Speed />}
                  color="primary"
                />
              </Grid>
            )}
          </Grid>

          {/* Recent Incidents */}
          {monitoring.recentIncidents && monitoring.recentIncidents.length > 0 && (
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AccessTime color="action" />
                <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
                  最近事件
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                  最近24小时
                </Typography>
              </Box>

              <List
                sx={{
                  bgcolor: 'background.paper',
                  borderRadius: 2,
                  border: 1,
                  borderColor: 'divider',
                  overflow: 'auto',
                  maxHeight: 240,
                  flexGrow: 1,
                }}
              >
                {monitoring.recentIncidents.map((incident) => (
                  <ListItem
                    key={incident.id}
                    sx={{
                      borderBottom: '1px solid',
                      borderColor: 'divider',
                      '&:last-child': { borderBottom: 'none' },
                      '&:hover': {
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    {/* Severity Chip */}
                    <Chip
                      label={getSeverityLabel(incident.severity)}
                      size="small"
                      color={getSeverityColor(incident.severity)}
                      sx={{ mr: 2, minWidth: 60 }}
                    />

                    <ListItemText
                      primary={incident.message}
                      secondary={formatTimestamp(incident.timestamp)}
                      primaryTypographyProps={{
                        variant: 'body2',
                        fontWeight: 500,
                      }}
                      secondaryTypographyProps={{
                        variant: 'caption',
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Performance Metrics */}
          {monitoring.performanceMetrics && (
            <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                性能指标
              </Typography>
              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Typography variant="caption" color="text.secondary">
                    成功率:
                  </Typography>
                  <Typography variant="body2" color="success.main" sx={{ fontWeight: 600 }}>
                    {monitoring.performanceMetrics.successRate}%
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Typography variant="caption" color="text.secondary">
                    错误率:
                  </Typography>
                  <Typography variant="body2" color="error.main" sx={{ fontWeight: 600 }}>
                    {monitoring.performanceMetrics.errorRate}%
                  </Typography>
                </Box>
              </Box>
            </Box>
          )}
        </>
      ) : (
        <Box sx={{ textAlign: 'center', py: 4, flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            无监控数据
          </Typography>
        </Box>
      )}
    </Paper>
  );
}
