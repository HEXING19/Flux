import api from './api';
import type { TestResult, WebSocketMessage } from '../types';

export interface LoginRequest {
  auth_code: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
}

export interface TestRequest {
  target_url: string;
  auth_code: string;
}

export interface TestResponse {
  task_id: string;
  status: string;
}

export interface SecurityIncidentsTestRequest {
  auth_code: string;
  base_url?: string;
}

export interface SecurityIncidentsTestResponse {
  success: boolean;
  message: string;
  latency_ms?: number;
  incident_count?: number;
  error_type?: string;
}

export const connectivityApi = {
  // 登录验证
  login: (data: LoginRequest) =>
    api.post<LoginResponse>('/api/v1/auth/login', data),

  // 启动连通性测试
  startTest: (data: TestRequest) =>
    api.post<TestResponse>('/api/v1/connectivity/test', data),

  // 测试安全事件API连通性
  testSecurityIncidents: (data: SecurityIncidentsTestRequest) =>
    api.post<SecurityIncidentsTestResponse>(
      '/api/v1/connectivity/test-security-incidents',
      data
    ),
};
