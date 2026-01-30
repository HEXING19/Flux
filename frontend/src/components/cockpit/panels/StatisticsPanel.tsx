/**
 * Statistics Panel Component
 * Displays dashboard statistics with Material Design style
 */

import { Box, Typography, Grid, Paper } from '@mui/material';
import { Security, Block, EventAvailable, TrendingUp } from '@mui/icons-material';
import { StatCard } from '../cards/StatCard';
import type { DashboardStatistics } from '../../../types/cockpit';

interface StatisticsPanelProps {
  statistics: DashboardStatistics | null;
  loading?: boolean;
}

export function StatisticsPanel({ statistics, loading = false }: StatisticsPanelProps) {
  // Mock trend data (can be replaced with real trend calculation)
  const weeklyTrend = 12.5;   // +12.5% vs last week
  const monthlyTrend = 8.3;   // +8.3% vs last month
  const ipTrend = -2.1;       // -2.1% (decrease is good for pending incidents)
  const successTrend = 5.7;   // +5.7% improvement

  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        borderRadius: 4, // 16px
        height: '100%',
      }}
    >
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <TrendingUp color="primary" />
        <Typography variant="h6" component="h2">
          数据统计
        </Typography>
      </Box>

      {/* Stat Cards Grid */}
      <Grid container spacing={2}>
        {/* Weekly Handled */}
        <Grid item xs={12} sm={6}>
          <StatCard
            title="本周处置"
            value={statistics?.weeklyHandled ?? 0}
            unit="个事件"
            icon={<Security />}
            trend={weeklyTrend}
            color="primary"
            loading={loading}
          />
        </Grid>

        {/* Monthly Handled */}
        <Grid item xs={12} sm={6}>
          <StatCard
            title="本月处置"
            value={statistics?.monthlyHandled ?? 0}
            unit="个事件"
            icon={<EventAvailable />}
            trend={monthlyTrend}
            color="secondary"
            loading={loading}
          />
        </Grid>

        {/* Blocked IPs */}
        <Grid item xs={12} sm={6}>
          <StatCard
            title="封禁IP"
            value={statistics?.blockedIPs ?? 0}
            unit="个"
            icon={<Block />}
            trend={undefined}
            color="warning"
            loading={loading}
          />
        </Grid>

        {/* Success Rate */}
        <Grid item xs={12} sm={6}>
          <StatCard
            title="成功率"
            value={statistics?.successRate ?? 0}
            unit="%"
            icon={<TrendingUp />}
            trend={successTrend}
            color="success"
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* Pending Incidents (Full Width) */}
      <Box sx={{ mt: 2 }}>
        <StatCard
          title="待处理事件"
          value={statistics?.pendingIncidents ?? 0}
          unit="个"
          icon={<Security />}
          trend={ipTrend}
          color="error"
          loading={loading}
        />
      </Box>

      {/* Distribution Info (Optional) */}
      {statistics?.distribution && (
        <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
            事件分布
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {Object.entries(statistics.distribution.severity || {}).map(([key, value]) => (
              <Box key={key} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  {key}:
                </Typography>
                <Typography variant="caption" color="primary" sx={{ fontWeight: 600 }}>
                  {value as number}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </Paper>
  );
}
