import { useEffect, useState, useRef } from 'react';

interface TestResult {
  protocol: string;
  status: string;
  status_code?: number;
  latency?: number;
  response_preview?: string;
  error?: string;
}

interface WebSocketMessage {
  type: 'test_start' | 'test_progress' | 'test_complete';
  task_id: string;
  message?: string;
  result?: TestResult;
}

interface UseWebSocketReturn {
  results: TestResult[];
  status: 'connecting' | 'connected' | 'disconnected';
  messages: string[];
  isComplete: boolean;
}

export const useWebSocket = (taskId: string | null): UseWebSocketReturn => {
  const [results, setResults] = useState<TestResult[]>([]);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const [messages, setMessages] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!taskId) return;

    const wsUrl = `ws://localhost:8000/api/v1/connectivity/ws/test/${taskId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);

        if (data.type === 'test_start' && data.message) {
          setMessages((prev) => [...prev, data.message!]);
        } else if (data.type === 'test_progress' && data.result) {
          setResults((prev) => [...prev, data.result!]);
        } else if (data.type === 'test_complete' && data.message) {
          setMessages((prev) => [...prev, data.message!]);
          setIsComplete(true);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = () => {
      setStatus('disconnected');
    };

    ws.onclose = () => {
      setStatus('disconnected');
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [taskId]);

  return { results, status, messages, isComplete };
};
