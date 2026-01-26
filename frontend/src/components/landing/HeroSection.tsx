import { Box, Container, Typography, Button } from '@mui/material';

export const HeroSection = () => {
  return (
    <Box
      sx={{
        bgcolor: 'primary.main',
        color: 'white',
        py: 12,
        textAlign: 'center',
      }}
    >
      <Container maxWidth="md">
        <Typography variant="h1" gutterBottom>
          Flux
        </Typography>
        <Typography variant="h4" sx={{ mb: 4, fontWeight: 300 }}>
          AI 驱动的业务意图到技术配置自动转换
        </Typography>
        <Typography variant="body1" sx={{ mb: 6, fontSize: '1.2rem', opacity: 0.9 }}>
          一线交付人员不再输入复杂的 IP 和端口，直接说出意图
          <br />
          AI 直接生成配置，实时测试连通性，用户授权即可应用
        </Typography>
        <Button
          variant="contained"
          color="secondary"
          size="large"
          href="/tool"
          sx={{ px: 6, py: 2, fontSize: '1.1rem' }}
        >
          立即开始
        </Button>
      </Container>
    </Box>
  );
};
