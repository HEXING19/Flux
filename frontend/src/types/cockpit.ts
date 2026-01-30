/**
 * AI Security Operations Cockpit Types
 * Types for the AI-powered security operations dashboard
 */

/**
 * View mode for the application
 */
export type ViewMode = 'chat' | 'cockpit';

/**
 * System status for monitoring
 */
export type SystemStatus = 'online' | 'warning' | 'offline';

/**
 * Dashboard statistics data
 */
export interface DashboardStatistics {
  weeklyHandled: number;        // 本周处置事件数
  monthlyHandled: number;       // 本月处置事件数
  blockedIPs: number;           // 封禁IP总数
  pendingIncidents: number;     // 待处理事件数
  successRate: number;          // 成功率（百分比）
  trend?: TrendData[];          // 趋势数据（可选）
  distribution?: DistributionData; // 分布数据（可选）
}

/**
 * Trend data point for statistics
 */
export interface TrendData {
  date: string;   // 日期（如 "2024-01-29"）
  count: number;  // 数量
}

/**
 * Distribution data for incidents
 */
export interface DistributionData {
  severity: Record<string, number>;  // 严重等级分布 { "高危": 10, "严重": 5 }
  type: Record<string, number>;      // 类型分布
}

/**
 * Real-time monitoring data
 */
export interface MonitoringData {
  systemStatus: SystemStatus;   // 系统状态
  activeAlerts: number;         // 活跃告警数
  lastUpdate: number;           // 最后更新时间（时间戳）
  recentIncidents?: RecentIncident[];  // 最近事件（可选）
  performanceMetrics?: PerformanceMetrics;  // 性能指标（可选）
}

/**
 * Recent incident item for monitoring
 */
export interface RecentIncident {
  id: string;
  severity: number;      // 0-4: 未知、低危、中危、高危、严重
  message: string;
  timestamp: number;
}

/**
 * Performance metrics for monitoring
 */
export interface PerformanceMetrics {
  apiLatency: number;    // API延迟（毫秒）
  successRate: number;   // 成功率（百分比）
  errorRate: number;     // 错误率（百分比）
}

/**
 * Cockpit state interface
 */
export interface CockpitState {
  mode: ViewMode;                    // 当前视图模式
  statistics: DashboardStatistics | null;   // 统计数据
  monitoring: MonitoringData | null;        // 监控数据
  loading: boolean;                  // 加载状态
  error: string | null;              // 错误信息
}

/**
 * API response wrapper for dashboard statistics
 */
export interface DashboardStatisticsResponse {
  success: boolean;
  data: DashboardStatistics;
  message?: string;
}

/**
 * API response wrapper for monitoring data
 */
export interface MonitoringDataResponse {
  success: boolean;
  data: MonitoringData;
  message?: string;
}

/**
 * Stat card props for displaying individual statistics
 */
export interface StatCardProps {
  title: string;
  value: number | string;
  unit?: string;
  icon?: React.ReactNode;
  trend?: number;  // 趋势百分比（正数为增长，负数为下降）
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  loading?: boolean;
}

/**
 * Scenario card additional stats
 */
export interface ScenarioCardStats {
  totalIncidents: number;    // 总事件数
  avgProcessTime: string;    // 平均处理时间
  successRate: number;       // 成功率
}
