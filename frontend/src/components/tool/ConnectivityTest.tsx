import {
  Box,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Button,
  Divider,
  Paper,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Loop,
  Info,
} from '@mui/icons-material';
import { useWebSocket } from '../../hooks/useWebSocket';

interface TestResult {
  protocol: string;
  status: string;
  status_code?: number;
  latency?: number;
  response_preview?: string;
  error?: string;
}

interface ConnectivityTestProps {
  taskId: string;
  authCode: string;
  targetUrl: string;
  onReset: () => void;
}

export const ConnectivityTest = ({
  taskId,
  authCode,
  targetUrl,
  onReset,
}: ConnectivityTestProps) => {
  const { results, status, messages, isComplete } = useWebSocket(taskId);

  const getIcon = (result: TestResult) => {
    if (result.status === 'running') {
      return <Loop color="primary" />;
    } else if (result.status === 'success') {
      return <CheckCircle color="success" />;
    } else {
      return <Error color="error" />;
    }
  };

  const getChipColor = (status: string) => {
    if (status === 'success') return 'success';
    if (status === 'failed') return 'error';
    return 'primary';
  };

  const progress = results.length > 0 ? 100 : 0;

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        测试进行中
      </Typography>

      {/* 目标信息 */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          mb: 3,
          bgcolor: 'action.hover',
          borderRadius: 2,
        }}
      >
        <Typography variant="body2" color="text.secondary" gutterBottom>
          目标地址: {targetUrl}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          状态: {status === 'connected' ? '已连接' : status === 'connecting' ? '连接中...' : '已断开'}
        </Typography>
      </Paper>

      {/* 消息提示 */}
      {messages.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {messages.map((msg, idx) => (
            <Box key={idx} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Info color="info" sx={{ mr: 1, fontSize: '1.2rem' }} />
              <Typography variant="body2">{msg}</Typography>
            </Box>
          ))}
        </Box>
      )}

      {/* 进度条 */}
      {!isComplete && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress variant="indeterminate" />
        </Box>
      )}

      <Divider sx={{ my: 3 }} />

      {/* 测试结果 */}
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
        测试结果 ({results.length})
      </Typography>

      {results.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ py: 3, textAlign: 'center' }}>
          等待测试结果...
        </Typography>
      ) : (
        <List>
          {results.map((result, idx) => (
            <ListItem
              key={idx}
              divider={idx < results.length - 1}
              sx={{
                bgcolor: 'background.paper',
                mb: 1,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <ListItemIcon>{getIcon(result)}</ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {result.protocol}
                    </Typography>
                    <Chip
                      label={result.status}
                      color={getChipColor(result.status) as any}
                      size="small"
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    {result.status_code && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                        状态码: {result.status_code}
                      </Typography>
                    )}
                    {result.latency && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                        延迟: {result.latency}ms
                      </Typography>
                    )}
                    {result.error && (
                      <Typography variant="body2" color="error" sx={{ mb: 0.5 }}>
                        错误: {result.error}
                      </Typography>
                    )}
                    {result.response_preview && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          mt: 1,
                          p: 1.5,
                          bgcolor: 'action.hover',
                          borderRadius: 1,
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          wordBreak: 'break-all',
                          display: 'block',
                        }}
                      >
                        {result.response_preview}
                      </Typography>
                    )}
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      )}

      {/* 完成状态和操作按钮 */}
      {isComplete && (
        <Box sx={{ mt: 3 }}>
          <Typography
            variant="body1"
            color="success.main"
            sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center' }}
          >
            <CheckCircle sx={{ mr: 1 }} />
            测试完成
          </Typography>
          <Button variant="outlined" onClick={onReset} fullWidth>
            重新测试
          </Button>
        </Box>
      )}
    </Box>
  );
};
