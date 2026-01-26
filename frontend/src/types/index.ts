export interface TestResult {
  protocol: string;
  status: string;
  status_code?: number;
  latency?: number;
  response_preview?: string;
  error?: string;
}

export interface WebSocketMessage {
  type: 'test_start' | 'test_progress' | 'test_complete';
  task_id: string;
  message?: string;
  result?: TestResult;
}

// 确保类型被正确导出
export type { TestResult, WebSocketMessage };
