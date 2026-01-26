import { useState } from 'react';
import { Box, Container, Grid, Typography, AppBar, Toolbar, Button } from '@mui/material';
import { Home } from '@mui/icons-material';
import { LoginForm } from '../components/tool/LoginForm';
import { ConnectivityTest } from '../components/tool/ConnectivityTest';

export const ToolPage = () => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [authCode, setAuthCode] = useState('');
  const [targetUrl, setTargetUrl] = useState('');

  const handleTestStart = (newTaskId: string, code: string, url: string) => {
    setTaskId(newTaskId);
    setAuthCode(code);
    setTargetUrl(url);
  };

  const handleReset = () => {
    setTaskId(null);
    setAuthCode('');
    setTargetUrl('');
  };

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Flux 工具
          </Typography>
          <Button color="inherit" startIcon={<Home />} href="/">
            返回首页
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h4" gutterBottom>
          连通性测试工具
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          使用联动码登录并测试目标平台的连通性
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            {!taskId ? (
              <LoginForm onTestStart={handleTestStart} />
            ) : (
              <ConnectivityTest
                taskId={taskId}
                authCode={authCode}
                targetUrl={targetUrl}
                onReset={handleReset}
              />
            )}
          </Grid>

          <Grid item xs={12} md={6}>
            <Box
              sx={{
                p: 3,
                bgcolor: 'background.paper',
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <Typography variant="h6" gutterBottom>
                使用说明
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                1. 从平台获取联动码
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                2. 输入联动码和目标 API 地址
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                3. 点击"登录并测试"按钮
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                4. 实时查看测试进度和结果
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};
