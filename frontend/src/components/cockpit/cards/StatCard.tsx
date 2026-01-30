/**
 * Stat Card Component
 * Displays a single statistic with Material Design style
 */

import { Paper, Box, Typography, CircularProgress } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import type { StatCardProps } from '../../../types/cockpit';

export function StatCard({
  title,
  value,
  unit,
  icon,
  trend,
  color = 'primary',
  loading = false,
}: StatCardProps) {
  return (
    <Paper
      elevation={1}
      sx={{
        p: 2.5,
        borderRadius: 3, // 12px
        height: '100%',
        transition: 'box-shadow 150ms ease-in-out',
        '&:hover': {
          elevation: 2,
        },
      }}
    >
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 3 }}>
          <CircularProgress size={32} />
        </Box>
      ) : (
        <>
          {/* Header with Icon and Title */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {icon && (
                <Box sx={{ color, fontSize: '1.25rem' }}>
                  {icon}
                </Box>
              )}
              <Typography variant="body2" color="text.secondary">
                {title}
              </Typography>
            </Box>

            {/* Trend Indicator */}
            {trend !== undefined && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  color: trend >= 0 ? 'success.main' : 'error.main',
                }}
              >
                {trend >= 0 ? (
                  <TrendingUp sx={{ fontSize: 18 }} />
                ) : (
                  <TrendingDown sx={{ fontSize: 18 }} />
                )}
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  {Math.abs(trend)}%
                </Typography>
              </Box>
            )}
          </Box>

          {/* Value Display */}
          <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5 }}>
            <Typography
              variant="h4"
              color={color}
              sx={{ fontWeight: 500 }}
            >
              {value}
            </Typography>
            {unit && (
              <Typography variant="body1" color="text.secondary" sx={{ ml: 0.5 }}>
                {unit}
              </Typography>
            )}
          </Box>
        </>
      )}
    </Paper>
  );
}
