import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  AppBar,
  Toolbar,
  Button,
  Card,
  CardContent,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Stack,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ArrowBack,
  CheckCircle,
  Settings as SettingsIcon,
  CloudDone,
  Http,
  VpnKey,
  Speed,
} from '@mui/icons-material';

interface LLMConfig {
  provider: string;
  apiKey: string;
  baseUrl: string;
}

const providers = [
  { value: 'zhipu', label: '智谱AI', model: 'GLM-4.7', icon: '🤖', color: '#1976d2' },
  { value: 'openai', label: 'OpenAI', model: 'GPT-4', icon: '🧠', color: '#00a67e' },
  { value: 'azure', label: 'Azure OpenAI', model: 'GPT-4', icon: '☁️', color: '#0078d4' },
  { value: 'deepseek', label: 'DeepSeek', model: 'DeepSeek', icon: '🔍', color: '#6366f1' },
  { value: 'custom', label: '自定义', model: '自定义', icon: '⚙️', color: '#64748b' },
];

export const SettingsPage = () => {
  const navigate = useNavigate();
  const [llmConfig, setLlmConfig] = useState<LLMConfig>({
    provider: 'zhipu',
    apiKey: '',
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4/',
  });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const selectedProvider = providers.find(p => p.value === llmConfig.provider);

  const handleBack = () => {
    navigate('/dashboard');
  };

  const handleTestConnection = async () => {
    if (!llmConfig.apiKey) {
      setTestResult({
        success: false,
        message: '请先输入API Key',
      });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/llm/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: llmConfig.provider,
          api_key: llmConfig.apiKey,
          base_url: llmConfig.baseUrl,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setTestResult({
          success: true,
          message: `连接成功! ${data.message || '大模型服务可用'}`,
        });
      } else {
        setTestResult({
          success: false,
          message: data.message || '连接失败',
        });
      }
    } catch (error: any) {
      setTestResult({
        success: false,
        message: `连接失败: ${error.message}`,
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = () => {
    localStorage.setItem('llmConfig', JSON.stringify(llmConfig));
    setTestResult({
      success: true,
      message: '✓ 配置已保存',
    });
  };

  const handleProviderChange = (event: any) => {
    const newProvider = event.target.value;
    const provider = providers.find(p => p.value === newProvider);

    let defaultBaseUrl = llmConfig.baseUrl;
    if (provider) {
      switch (provider.value) {
        case 'zhipu':
          defaultBaseUrl = 'https://open.bigmodel.cn/api/paas/v4/';
          break;
        case 'openai':
          defaultBaseUrl = 'https://api.openai.com/v1/';
          break;
        case 'azure':
          defaultBaseUrl = 'https://{your-resource-name}.openai.azure.com/';
          break;
        case 'deepseek':
          defaultBaseUrl = 'https://api.deepseek.com/v1/';
          break;
      }
    }

    setLlmConfig({
      ...llmConfig,
      provider: newProvider,
      baseUrl: defaultBaseUrl,
    });
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
        <Toolbar sx={{ width: '100%' }}>
          <Tooltip title="返回Dashboard">
            <IconButton
              edge="start"
              onClick={handleBack}
              sx={{ mr: 2, color: 'text.primary' }}
            >
              <ArrowBack />
            </IconButton>
          </Tooltip>
          <SettingsIcon sx={{ mr: 2, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ fontWeight: 500, flex: 1 }}>
            大模型配置
          </Typography>
        </Toolbar>
      </AppBar>

      {/* 主内容区域 */}
      <Box sx={{ flex: 1, py: 4 }}>
        <Container maxWidth="lg">
          {/* 页面标题和描述 */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 400, color: 'text.primary' }}>
              AI 模型配置
            </Typography>
            <Typography variant="body1" color="text.secondary">
              配置您的大语言模型 API 密钥以启用 AI 功能
            </Typography>
          </Box>

          <Stack spacing={3}>
            {/* 模型提供商选择卡片 */}
            <Card
              elevation={0}
              sx={{
                borderRadius: 3,
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: 2,
                      bgcolor: selectedProvider?.color || 'primary.main',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2,
                    }}
                  >
                    <Typography variant="h5">{selectedProvider?.icon}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 500 }}>
                      模型提供商
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedProvider?.label} - {selectedProvider?.model}
                    </Typography>
                  </Box>
                </Box>

                <TextField
                  fullWidth
                  select
                  value={llmConfig.provider}
                  onChange={handleProviderChange}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    },
                  }}
                >
                  {providers.map((provider) => (
                    <MenuItem key={provider.value} value={provider.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        <Typography sx={{ mr: 1 }}>{provider.icon}</Typography>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {provider.label}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {provider.model}
                          </Typography>
                        </Box>
                      </Box>
                    </MenuItem>
                  ))}
                </TextField>
              </CardContent>
            </Card>

            {/* API 配置卡片 */}
            <Card
              elevation={0}
              sx={{
                borderRadius: 3,
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 500, mb: 3 }}>
                  API 配置
                </Typography>

                <Stack spacing={3}>
                  {/* Base URL */}
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Http sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="subtitle2" sx={{ fontWeight: 500, color: 'text.secondary' }}>
                        API Base URL
                      </Typography>
                    </Box>
                    <TextField
                      fullWidth
                      value={llmConfig.baseUrl}
                      onChange={(e) =>
                        setLlmConfig({ ...llmConfig, baseUrl: e.target.value })
                      }
                      placeholder="https://api.example.com/v1/"
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                        },
                      }}
                      helperText="输入您的 API 端点地址"
                    />
                  </Box>

                  <Divider />

                  {/* API Key */}
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <VpnKey sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="subtitle2" sx={{ fontWeight: 500, color: 'text.secondary' }}>
                        API Key
                      </Typography>
                    </Box>
                    <TextField
                      fullWidth
                      type="password"
                      value={llmConfig.apiKey}
                      onChange={(e) =>
                        setLlmConfig({ ...llmConfig, apiKey: e.target.value })
                      }
                      placeholder="输入您的 API 密钥"
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                        },
                      }}
                      helperText="您的 API 密钥将安全保存"
                    />
                  </Box>
                </Stack>
              </CardContent>
            </Card>

            {/* 测试结果提示 */}
            {testResult && (
              <Alert
                severity={testResult.success ? 'success' : 'error'}
                variant="filled"
                sx={{
                  borderRadius: 2,
                  '& .MuiAlert-icon': {
                    fontSize: 28,
                  },
                }}
              >
                {testResult.message}
              </Alert>
            )}

            {/* 操作按钮 */}
            <Card
              elevation={0}
              sx={{
                borderRadius: 3,
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Stack direction="row" spacing={2}>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={handleTestConnection}
                    disabled={testing}
                    startIcon={testing ? <CircularProgress size={20} /> : <Speed />}
                    sx={{
                      borderRadius: 2,
                      px: 3,
                      textTransform: 'none',
                    }}
                  >
                    {testing ? '测试中...' : '测试连通性'}
                  </Button>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleSave}
                    disabled={!llmConfig.apiKey}
                    startIcon={<CloudDone />}
                    sx={{
                      borderRadius: 2,
                      px: 3,
                      textTransform: 'none',
                    }}
                  >
                    保存配置
                  </Button>
                </Stack>
              </CardContent>
            </Card>

            {/* 使用提示 */}
            <Card
              elevation={0}
              sx={{
                borderRadius: 3,
                border: '1px solid',
                borderColor: 'divider',
                bgcolor: 'info.50',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CheckCircle sx={{ mr: 1, color: 'info.main' }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 500, color: 'info.main' }}>
                    配置步骤
                  </Typography>
                </Box>
                <Stack spacing={1}>
                  <Typography variant="body2" color="text.secondary">
                    1. 从下拉菜单中选择您的大模型提供商
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    2. 输入您的 API Base URL 和 API Key
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    3. 点击"测试连通性"验证配置是否正确
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    4. 测试成功后,点击"保存配置"完成设置
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
};
