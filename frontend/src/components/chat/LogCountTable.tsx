import React from 'react';
import {
  Box,
  Card,
  Typography,
  Chip,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning
} from '@mui/icons-material';
import type { LogCountData } from '../../types/logCount';

interface LogCountTableProps {
  data: LogCountData;
}

export const LogCountTable: React.FC<LogCountTableProps> = ({ data }) => {
  return (
    <Card>
      <Box p={3}>
        {/* Title */}
        <Typography variant="h6" gutterBottom display="flex" alignItems="center">
          📊 日志统计结果
        </Typography>

        {/* Total Count */}
        <Box my={2} textAlign="center">
          <Typography variant="h3" color="primary" fontWeight="bold">
            {data.total.toLocaleString()}
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            日志总数
          </Typography>
        </Box>

        {/* Comparison Data */}
        {data.comparisons && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              趋势对比
            </Typography>
            <Box display="flex" gap={2}>
              <Box flex={1}>
                <ComparisonCard
                  title="环比上周"
                  count={data.comparisons.last_week.count}
                  change={data.comparisons.last_week.change_percent}
                />
              </Box>
              <Box flex={1}>
                <ComparisonCard
                  title="环比上月"
                  count={data.comparisons.last_month.count}
                  change={data.comparisons.last_month.change_percent}
                />
              </Box>
            </Box>
          </>
        )}

        {/* Distribution Statistics */}
        {data.distributions && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              分布分析
            </Typography>
            {data.distributions.severity && (
              <DistributionChart
                title="严重程度分布"
                data={data.distributions.severity}
              />
            )}
            {data.distributions.access_direction && (
              <DistributionChart
                title="访问方向分布"
                data={data.distributions.access_direction}
              />
            )}
            {data.distributions.product_type && (
              <DistributionChart
                title="产品类型分布"
                data={data.distributions.product_type}
              />
            )}
          </>
        )}

        {/* Trend Chart */}
        {data.trend && data.trend.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              趋势分析（按天）
            </Typography>
            <TrendChart data={data.trend} />
          </>
        )}

        {/* Anomaly Alerts */}
        {data.anomalies && data.anomalies.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              ⚠️ 异常提醒
            </Typography>
            {data.anomalies.map((anomaly, index) => (
              <Box
                key={index}
                display="flex"
                alignItems="center"
                p={1}
                bgcolor={anomaly.type === 'warning' ? 'warning.light' : 'info.light'}
                borderRadius={1}
                mb={1}
              >
                <Warning fontSize="small" sx={{ mr: 1 }} />
                <Typography variant="body2">{anomaly.message}</Typography>
              </Box>
            ))}
          </>
        )}

        {/* Filter Conditions */}
        {data.filters && Object.keys(data.filters).length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              查询条件
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {Object.entries(data.filters).map(([key, value]) => {
                if (value && Array.isArray(value) && value.length > 0) {
                  return <FilterChip key={key} label={key} value={value} />;
                }
                return null;
              })}
            </Box>
          </>
        )}
      </Box>
    </Card>
  );
};

// Comparison Card Component
const ComparisonCard: React.FC<{
  title: string;
  count: number;
  change: number;
}> = ({ title, count, change }) => (
  <Box textAlign="center" p={2} bgcolor="grey.50" borderRadius={1}>
    <Typography variant="caption" color="textSecondary">
      {title}
    </Typography>
    <Typography variant="h6">{count.toLocaleString()}</Typography>
    <Box display="flex" alignItems="center" justifyContent="center">
      {change >= 0 ? (
        <TrendingUp color="error" fontSize="small" />
      ) : (
        <TrendingDown color="success" fontSize="small" />
      )}
      <Typography
        variant="body2"
        color={change >= 0 ? 'error.main' : 'success.main'}
        fontWeight="bold"
      >
        {change >= 0 ? '+' : ''}{change.toFixed(1)}%
      </Typography>
    </Box>
  </Box>
);

// Distribution Chart Component
const DistributionChart: React.FC<{
  title: string;
  data: Record<string, number>;
}> = ({ title, data }) => {
  const total = Object.values(data).reduce((a, b) => a + b, 0);

  return (
    <Box my={1}>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        {title}
      </Typography>
      {Object.entries(data).map(([label, count]) => {
        const percent = total > 0 ? (count / total * 100) : 0;
        return (
          <Box key={label} display="flex" alignItems="center" mb={0.5}>
            <Typography variant="caption" sx={{ width: 100 }}>
              {label}
            </Typography>
            <Box
              sx={{
                width: `${Math.max(percent, 1)}%`,
                bgcolor: 'primary.main',
                height: 20,
                borderRadius: 1,
                mr: 1,
                minWidth: 20
              }}
            />
            <Typography variant="caption">
              {count.toLocaleString()} ({percent.toFixed(1)}%)
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
};

// Trend Chart Component
const TrendChart: React.FC<{ data: Array<{ date: string; count: number }> }> = ({ data }) => {
  const maxCount = Math.max(...data.map(d => d.count));

  return (
    <Box>
      {data.map((day, index) => {
        const height = maxCount > 0 ? (day.count / maxCount * 100) : 0;
        return (
          <Box key={index} display="flex" alignItems="center" mb={0.5}>
            <Typography variant="caption" sx={{ width: 100 }}>
              {day.date}
            </Typography>
            <Box
              sx={{
                width: `${Math.max(height, 1)}%`,
                bgcolor: 'primary.main',
                height: 16,
                borderRadius: 1,
                mr: 1,
                minWidth: 20
              }}
            />
            <Typography variant="caption">
              {day.count.toLocaleString()}
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
};

// Filter Chip Component
const FilterChip: React.FC<{ label: string; value: any }> = ({ label, value }) => {
  // Format label for display
  const displayLabel: Record<string, string> = {
    'startTimestamp': '起始时间',
    'endTimestamp': '结束时间',
    'productTypes': '产品类型',
    'accessDirections': '访问方向',
    'threatClasses': '威胁分类',
    'srcIps': '源IP',
    'dstIps': '目的IP',
    'attackStates': '攻击状态',
    'severities': '严重等级'
  };

  const displayValue = Array.isArray(value) ? value.join(', ') : String(value);
  const labelText = displayLabel[label] || label;

  return (
    <Chip
      label={`${labelText}: ${displayValue}`}
      size="small"
      variant="outlined"
    />
  );
};
