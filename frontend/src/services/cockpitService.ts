/**
 * AI Security Operations Cockpit Service
 * Handles API calls for dashboard statistics and monitoring data
 */

import type {
  DashboardStatistics,
  DashboardStatisticsResponse,
  MonitoringData,
  MonitoringDataResponse,
} from '../types/cockpit';

/**
 * Fetch dashboard statistics from the backend
 *
 * @param timeRange - Time range for statistics ('week' | 'month')
 * @param authCode - Flux authentication code
 * @param baseUrl - Flux API base URL
 * @returns Dashboard statistics data
 */
export async function fetchDashboardStatistics(
  timeRange: 'week' | 'month' = 'week',
  authCode?: string,
  baseUrl?: string
): Promise<DashboardStatistics> {
  try {
    // Get auth info from localStorage if not provided
    const effectiveAuthCode = authCode || localStorage.getItem('flux_auth_code');
    const effectiveBaseUrl = baseUrl || localStorage.getItem('flux_base_url');

    if (!effectiveAuthCode || !effectiveBaseUrl) {
      throw new Error('缺少 Flux 认证信息，请先登录');
    }

    // Build query params
    const params = new URLSearchParams({
      time_range: timeRange,
    });

    // Call backend API
    const response = await fetch(`http://localhost:8000/api/v1/dashboard/statistics?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'x-auth-code': effectiveAuthCode,
        'x-base-url': effectiveBaseUrl,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: '未知错误' }));
      throw new Error(errorData.message || `API错误: ${response.status}`);
    }

    const result: DashboardStatisticsResponse = await response.json();

    if (!result.success || !result.data) {
      throw new Error(result.message || '获取统计数据失败');
    }

    return result.data;
  } catch (error) {
    console.error('Failed to fetch dashboard statistics:', error);
    throw error;
  }
}

/**
 * Fetch real-time monitoring data from the backend
 *
 * @param authCode - Flux authentication code
 * @param baseUrl - Flux API base URL
 * @returns Real-time monitoring data
 */
export async function fetchMonitoringStatus(
  authCode?: string,
  baseUrl?: string
): Promise<MonitoringData> {
  try {
    // Get auth info from localStorage if not provided
    const effectiveAuthCode = authCode || localStorage.getItem('flux_auth_code');
    const effectiveBaseUrl = baseUrl || localStorage.getItem('flux_base_url');

    if (!effectiveAuthCode || !effectiveBaseUrl) {
      throw new Error('缺少 Flux 认证信息，请先登录');
    }

    // Call backend API
    const response = await fetch('http://localhost:8000/api/v1/dashboard/monitoring', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'x-auth-code': effectiveAuthCode,
        'x-base-url': effectiveBaseUrl,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: '未知错误' }));
      throw new Error(errorData.message || `API错误: ${response.status}`);
    }

    const result: MonitoringDataResponse = await response.json();

    if (!result.success || !result.data) {
      throw new Error(result.message || '获取监控数据失败');
    }

    return result.data;
  } catch (error) {
    console.error('Failed to fetch monitoring status:', error);
    throw error;
  }
}

/**
 * Fetch both statistics and monitoring data in parallel
 *
 * @param timeRange - Time range for statistics ('week' | 'month')
 * @param authCode - Flux authentication code
 * @param baseUrl - Flux API base URL
 * @returns Object containing both statistics and monitoring data
 */
export async function fetchCockpitData(
  timeRange: 'week' | 'month' = 'week',
  authCode?: string,
  baseUrl?: string
): Promise<{
  statistics: DashboardStatistics;
  monitoring: MonitoringData;
}> {
  try {
    const [statistics, monitoring] = await Promise.all([
      fetchDashboardStatistics(timeRange, authCode, baseUrl),
      fetchMonitoringStatus(authCode, baseUrl),
    ]);

    return { statistics, monitoring };
  } catch (error) {
    console.error('Failed to fetch cockpit data:', error);
    throw error;
  }
}
