import { Box, AppBar, Toolbar, Button, Stack, Typography } from '@mui/material';
import { Settings, Logout, Dashboard as DashboardIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ChatInterface } from '../components/chat/ChatInterface';

export const DashboardPage = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('isLoggedIn');
    window.location.href = '/';
  };

  const handleSettings = () => {
    navigate('/settings');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: '#f8f9fa',
      }}
    >
      {/* 顶部导航栏 - Material Design 3 风格 */}
      <AppBar
        position="static"
        elevation={0}
        sx={{
          bgcolor: 'white',
          color: 'text.primary',
          borderBottom: '1px solid',
          borderColor: 'divider',
          width: '100%',
        }}
      >
        <Toolbar sx={{ width: '100%', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                bgcolor: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2,
              }}
            >
              <DashboardIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 500, color: 'text.primary' }}>
                Flux AI
              </Typography>
              <Typography variant="caption" color="text.secondary">
                智能安全助手
              </Typography>
            </Box>
          </Box>

          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              startIcon={<Settings />}
              onClick={handleSettings}
              sx={{
                borderRadius: 2,
                textTransform: 'none',
                px: 3,
              }}
            >
              设置
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Logout />}
              onClick={handleLogout}
              sx={{
                borderRadius: 2,
                textTransform: 'none',
                px: 3,
              }}
            >
              退出登录
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* 聊天界面 */}
      <Box sx={{ bgcolor: 'white', height: 'calc(100vh - 64px)' }}>
        <ChatInterface />
      </Box>
    </Box>
  );
};
