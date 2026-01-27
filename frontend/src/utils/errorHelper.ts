/**
 * Error Helper Utility for Frontend
 * Handles error parsing, display formatting, and user guidance
 */

// Error type definitions
export interface ErrorInfo {
  success: false;
  status_code?: number;
  error_type: string;
  friendly_message: string;
  raw_message: string;
  suggestion: string;
  actions: string[];
  raw_code?: string;
}

export interface ParsedError {
  title: string;
  message: string;
  suggestion: string;
  actions: ErrorAction[];
  canRetry: boolean;
  severity: 'info' | 'warning' | 'error';
}

export interface ErrorAction {
  label: string;
  type: 'retry' | 'modify' | 'contact' | 'close';
  primary?: boolean;
}

// Error type icons mapping
export const ERROR_TYPE_ICONS: Record<string, string> = {
  permission_error: '🔒',
  auth_error: '🔐',
  validation_error: '📝',
  not_found_error: '🔍',
  rate_limit_error: '⏱️',
  network_error: '🌐',
  service_error: '⚠️',
  system_error: '💥',
  unknown_error: '❓',
};

/**
 * Check if response is a structured error
 */
export function isStructuredError(data: unknown): data is ErrorInfo {
  return (
    typeof data === 'object' &&
    data !== null &&
    'success' in data &&
    data.success === false &&
    'error_type' in data &&
    'friendly_message' in data
  );
}

/**
 * Parse error from API response
 */
export function parseErrorResponse(data: unknown): ParsedError {
  // Handle structured error from backend
  if (isStructuredError(data)) {
    const errorType = data.error_type || 'unknown_error';
    const icon = ERROR_TYPE_ICONS[errorType] || '❌';

    return {
      title: `${icon} ${data.friendly_message}`,
      message: data.raw_message || '未知错误',
      suggestion: data.suggestion || '请稍后重试',
      actions: data.actions.map((action, index) => ({
        label: action,
        type: getActionType(action),
        primary: index === 0,
      })),
      canRetry: isRetryableError(errorType),
      severity: getErrorSeverity(errorType),
    };
  }

  // Handle legacy error format (string message)
  if (typeof data === 'string') {
    return {
      title: '❌ 请求失败',
      message: decodeUnicode(data),
      suggestion: '请稍后重试或检查输入参数',
      actions: [{ label: '重试', type: 'retry', primary: true }],
      canRetry: true,
      severity: 'error',
    };
  }

  // Handle generic error object
  if (typeof data === 'object' && data !== null) {
    const message = 'message' in data ? String(data.message) : '未知错误';
    return {
      title: '❌ 请求失败',
      message: decodeUnicode(message),
      suggestion: '请稍后重试',
      actions: [{ label: '关闭', type: 'close', primary: true }],
      canRetry: true,
      severity: 'error',
    };
  }

  // Fallback
  return {
    title: '❌ 未知错误',
    message: '发生未知错误，请稍后重试',
    suggestion: '如果问题持续，请联系管理员',
    actions: [
      { label: '重试', type: 'retry', primary: true },
      { label: '联系管理员', type: 'contact' },
    ],
    canRetry: true,
    severity: 'error',
  };
}

/**
 * Decode UNICODE escape sequences to Chinese characters
 * Handles both \uXXXX format and JSON unicode
 */
export function decodeUnicode(text: string): string {
  try {
    // Handle JSON unicode escape
    const decoded = text.replace(/\\u([0-9a-fA-F]{4})/g, (_, hex) =>
      String.fromCharCode(parseInt(hex, 16))
    );
    return decoded;
  } catch {
    return text;
  }
}

/**
 * Determine error action type from label
 */
function getActionType(label: string): ErrorAction['type'] {
  const actionMap: Record<string, ErrorAction['type']> = {
    重试: 'retry',
    修改: 'modify',
    检查: 'modify',
    配置: 'modify',
    联系: 'contact',
    关闭: 'close',
  };

  for (const [key, type] of Object.entries(actionMap)) {
    if (label.includes(key)) {
      return type;
    }
  }

  return 'close';
}

/**
 * Check if error type is retryable
 */
function isRetryableError(errorType: string): boolean {
  const retryableTypes = new Set([
    'rate_limit_error',
    'service_error',
    'network_error',
    'unknown_error',
  ]);
  return retryableTypes.has(errorType);
}

/**
 * Get error severity for UI display
 */
function getErrorSeverity(errorType: string): 'info' | 'warning' | 'error' {
  if (['validation_error', 'auth_error'].includes(errorType)) {
    return 'warning';
  }
  if (['network_error', 'service_error'].includes(errorType)) {
    return 'info';
  }
  return 'error';
}

/**
 * Format error for display in chat message
 */
export function formatChatMessage(error: ParsedError): string {
  const lines = [
    error.title,
    '',
    `详情: ${error.message}`,
    '',
    `💡 建议: ${error.suggestion}`,
  ];

  if (error.actions.length > 0) {
    lines.push('', `可操作: ${error.actions.map(a => a.label).join(' • ')}`);
  }

  return lines.join('\n');
}
