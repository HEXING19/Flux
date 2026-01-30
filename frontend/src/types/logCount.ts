/**
 * Log Count Data Types
 * TypeScript type definitions for network security log count statistics
 */

export interface LogCountData {
  total: number;
  filters: LogCountFilters;

  // Enhanced analysis data (optional)
  comparisons?: {
    last_week: ComparisonData;
    last_month: ComparisonData;
  };
  distributions?: {
    severity: Record<string, number>;
    access_direction: Record<string, number>;
    product_type: Record<string, number>;
  };
  trend?: Array<TrendDataPoint>;
  anomalies?: Array<AnomalyData>;
}

export interface LogCountFilters {
  startTimestamp?: number;
  endTimestamp?: number;
  productTypes?: string[];
  accessDirections?: number[];
  threatClasses?: string[];  // Only first-level classification
  srcIps?: string[];
  dstIps?: string[];
  attackStates?: number[];
  severities?: number[];
}

export interface ComparisonData {
  count: number;
  change_percent: number;
}

export interface TrendDataPoint {
  date: string;
  count: number;
}

export interface AnomalyData {
  type: 'info' | 'warning' | 'error';
  message: string;
}
