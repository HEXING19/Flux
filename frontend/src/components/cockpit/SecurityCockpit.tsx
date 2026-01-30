/**
 * AI Security Operations Cockpit - Main Container
 * Main component for the AI-powered security operations dashboard
 */

import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Fab,
  Toolbar,
} from '@mui/material';
import { Chat as ChatIcon } from '@mui/icons-material';
import { ScenarioCardsPanel } from './panels/ScenarioCardsPanel';
import { StatisticsPanel } from './panels/StatisticsPanel';
import { MonitoringPanel } from './panels/MonitoringPanel';
import { fetchCockpitData } from '../../services/cockpitService';
import type { DashboardStatistics, MonitoringData } from '../../types/cockpit';
import { cockpitTheme } from '../../theme';

interface SecurityCockpitProps {
  onScenarioStart: (scenarioId: string) => void;
  onModeChange: () => void;
}

const REFRESH_INTERVAL = 30000; // 30 seconds

export function SecurityCockpit({ onScenarioStart, onModeChange }: SecurityCockpitProps) {
  const [statistics, setStatistics] = useState<DashboardStatistics | null>(null);
  const [monitoring, setMonitoring] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch cockpit data
  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const data = await fetchCockpitData('week');
      setStatistics(data.statistics);
      setMonitoring(data.monitoring);
    } catch (err) {
      console.error('Failed to fetch cockpit data:', err);
      setError(err instanceof Error ? err.message : '加载数据失败');
      // Set default values on error
      setStatistics({
        weeklyHandled: 0,
        monthlyHandled: 0,
        blockedIPs: 0,
        pendingIncidents: 0,
        successRate: 100.0,
        trend: [],
        distribution: undefined,
      });
      setMonitoring({
        systemStatus: 'offline',
        activeAlerts: 0,
        lastUpdate: Math.floor(Date.now() / 1000),
        recentIncidents: [],
        performanceMetrics: {
          apiLatency: 0,
          successRate: 0,
          errorRate: 0,
        },
      });
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh data
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, [fetchData]);

  // Handle scenario start
  const handleScenarioStart = (scenarioId: string) => {
    onScenarioStart(scenarioId);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
      }}
    >
      {/* Top Toolbar - Material Design */}
      <Box
        sx={{
          position: 'sticky',
          top: 0,
          zIndex: 1000,
          bgcolor: 'background.paper',
          elevation: 4,
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar disableGutters>
          <Container maxWidth="xl" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            {/* Title */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography
                variant="h5"
                sx={{
                  color: 'primary.main',
                  fontWeight: 400,
                }}
              >
                🤖 AI安全运营驾驶舱
              </Typography>
            </Box>

            {/* Switch to Chat Mode Button */}
            <Button
              variant="outlined"
              startIcon={<ChatIcon />}
              onClick={onModeChange}
            >
              切换到对话模式
            </Button>
          </Container>
        </Toolbar>
      </Box>

      {/* Main Content - Left-Right Layout */}
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              py: 12,
              gap: 2,
            }}
          >
            <CircularProgress size={60} />
            <Typography variant="h6">
              初始化驾驶舱...
            </Typography>
          </Box>
        )}

        {/* Dashboard Content - Left-Right Layout */}
        {!loading && (
          <Grid container spacing={3}>
            {/* Left Panel: Scenario Cards (40%) */}
            <Grid item xs={12} lg={5}>
              <ScenarioCardsPanel
                onScenarioStart={handleScenarioStart}
                disabled={loading}
              />
            </Grid>

            {/* Right Panel: Statistics + Monitoring (60%) */}
            <Grid item xs={12} lg={7}>
              <Grid container spacing={3} direction="column">
                {/* Statistics Panel */}
                <Grid item>
                  <StatisticsPanel
                    statistics={statistics}
                    loading={loading}
                  />
                </Grid>

                {/* Monitoring Panel */}
                <Grid item>
                  <MonitoringPanel
                    monitoring={monitoring}
                    loading={loading}
                  />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        )}

        {/* Footer Info */}
        {!loading && (
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              数据每30秒自动刷新 • 最后更新: {monitoring?.lastUpdate
                ? new Date(monitoring.lastUpdate * 1000).toLocaleString('zh-CN')
                : '-'}
            </Typography>
          </Box>
        )}
      </Container>
    </Box>
  );
}
