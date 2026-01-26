import { Box, Container, Grid, Typography, AppBar, Toolbar, Card, CardContent, Stack } from '@mui/material';
import {
  Login as LoginIcon,
  Security,
  Speed,
  Cloud,
  Shield,
} from '@mui/icons-material';
import { LoginForm } from '../components/tool/LoginForm';

export const HomePage = () => {
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
        <Toolbar sx={{ width: '100%' }}>
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
            <Security sx={{ color: 'white', fontSize: 24 }} />
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 500, color: 'text.primary' }}>
            Flux
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Hero 区域 - 居中显示 */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: { xs: 6, md: 8 },
          bgcolor: 'white',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            {/* 左侧：标题和描述 */}
            <Grid item xs={12} md={6}>
              <Typography
                variant="h2"
                sx={{
                  mb: 3,
                  fontWeight: 400,
                  fontSize: { xs: '2rem', md: '3rem' },
                  color: 'text.primary',
                  lineHeight: 1.2,
                }}
              >
                AI 驱动的<br />
                <Box component="span" sx={{ color: 'primary.main', fontWeight: 500 }}>
                  安全配置工具
                </Box>
              </Typography>

              <Typography
                variant="h6"
                color="text.secondary"
                sx={{
                  mb: 4,
                  fontWeight: 400,
                  fontSize: { xs: '1.1rem', md: '1.25rem' },
                  lineHeight: 1.6,
                }}
              >
                使用人工智能技术,实现安全平台的智能配置与联动
              </Typography>

              {/* 特性卡片 */}
              <Stack spacing={2} sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 2,
                      bgcolor: 'primary.light',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2,
                    }}
                  >
                    <Speed sx={{ color: 'primary.main', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 500, color: 'text.primary' }}>
                      快速连通性测试
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      实时验证安全平台连接状态
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 2,
                      bgcolor: 'success.light',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2,
                    }}
                  >
                    <Shield sx={{ color: 'success.main', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 500, color: 'text.primary' }}>
                      安全事件检测
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      智能分析和响应安全威胁
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 2,
                      bgcolor: 'info.light',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2,
                    }}
                  >
                    <Cloud sx={{ color: 'info.main', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 500, color: 'text.primary' }}>
                      云平台集成
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      无缝对接主流安全平台
                    </Typography>
                  </Box>
                </Box>
              </Stack>
            </Grid>

            {/* 右侧：登录表单 */}
            <Grid item xs={12} md={6}>
              <Card
                elevation={0}
                sx={{
                  borderRadius: 3,
                  border: '1px solid',
                  borderColor: 'divider',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                }}
              >
                <CardContent sx={{ p: { xs: 3, md: 4 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        bgcolor: 'primary.main',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 2,
                      }}
                    >
                      <LoginIcon sx={{ color: 'white', fontSize: 28 }} />
                    </Box>
                    <Box>
                      <Typography variant="h5" sx={{ fontWeight: 500 }}>
                        欢迎使用
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        登录以开始使用
                      </Typography>
                    </Box>
                  </Box>
                  <LoginForm />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* 底部信息栏 */}
      <Box
        sx={{
          bgcolor: 'white',
          borderTop: '1px solid',
          borderColor: 'divider',
          py: 3,
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" color="text.secondary" align="center">
            © 2024 Flux. 智能安全配置平台
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};
