import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Box,
} from '@mui/material';
import { connectivityApi } from '../../services/connectivity';

export const LoginForm = () => {
  const navigate = useNavigate();
  const [ipAddress, setIpAddress] = useState('');
  const [authCode, setAuthCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await connectivityApi.testSecurityIncidents({
        auth_code: authCode,
        base_url: ipAddress || undefined
      });

      if (response.success) {
        // 登录成功，保存认证信息到 localStorage
        const baseUrl = ipAddress || 'https://10.5.41.194';
        localStorage.setItem('flux_auth_code', authCode);
        localStorage.setItem('flux_base_url', baseUrl);
        // 跳转到Dashboard页面
        navigate('/dashboard');
      } else {
        setError(response.message);
      }
    } catch (err: any) {
      setError(err.message || '连接测试失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        登录
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        输入IP地址和联动码测试与安全平台的连通性
      </Typography>

      <TextField
        fullWidth
        label="IP地址"
        placeholder="https://10.5.41.194"
        value={ipAddress}
        onChange={(e) => setIpAddress(e.target.value)}
        sx={{ mb: 3 }}
        helperText="目标平台的IP地址(可选,默认使用内置地址)"
        disabled={false}
      />

      <TextField
        fullWidth
        label="联动码"
        type="password"
        value={authCode}
        onChange={(e) => setAuthCode(e.target.value)}
        required
        sx={{ mb: 3 }}
        placeholder="请输入联动码"
        helperText="从平台获取的联动码"
        disabled={loading}
      />

      {error && (
        <Alert severity="error" sx={{ mb: 3, mt: 1 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Button
        type="submit"
        variant="contained"
        fullWidth
        size="large"
        disabled={loading}
        startIcon={loading ? <CircularProgress size={20} /> : null}
        sx={{ mt: 2 }}
      >
        {loading ? '正在登录...' : '登录'}
      </Button>
    </Box>
  );
};
