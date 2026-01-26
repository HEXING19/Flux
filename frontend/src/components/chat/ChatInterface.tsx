import { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Avatar,
  Stack,
  Tooltip,
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  Add,
  Security,
  Analytics,
  Settings,
} from '@mui/icons-material';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  prompt: string;
  color: string;
}

const quickActions: QuickAction[] = [
  {
    id: 'security',
    title: '安全配置',
    description: '进行安全平台配置和策略设置',
    icon: <Security />,
    prompt: '帮我进行安全配置',
    color: '#1976d2',
  },
  {
    id: 'threat',
    title: '威胁分析',
    description: '分析当前安全威胁和风险',
    icon: <Analytics />,
    prompt: '分析当前安全威胁',
    color: '#2e7d32',
  },
  {
    id: 'integration',
    title: '联动设置',
    description: '配置平台间的联动规则',
    icon: <Settings />,
    prompt: '如何配置平台联动?',
    color: '#ed6c02',
  },
];

export const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '您好!我是Flux AI助手。我可以帮助您进行安全配置、威胁分析等任务。请问有什么可以帮您的吗?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>(Date.now().toString());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleNewChat = () => {
    const newConversationId = Date.now().toString();
    setConversationId(newConversationId);
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: '您好!我是Flux AI助手。我可以帮助您进行安全配置、威胁分析等任务。请问有什么可以帮您的吗?',
        timestamp: new Date(),
      },
    ]);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // 从localStorage获取配置
      const llmConfigStr = localStorage.getItem('llmConfig');
      if (!llmConfigStr) {
        throw new Error('请先在设置页面配置大模型API');
      }

      const llmConfig = JSON.parse(llmConfigStr);

      // 调用后端API
      const response = await fetch('http://localhost:8000/api/v1/llm/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.content,
          })),
          provider: llmConfig.provider,
          api_key: llmConfig.apiKey,
          base_url: llmConfig.baseUrl,
        }),
      });

      if (!response.ok) {
        throw new Error('API请求失败');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message || '抱歉,我现在无法回复。',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `错误: ${error.message}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickAction = (prompt: string) => {
    setInput(prompt);
  };

  // 只有在第一轮对话时显示快捷操作
  const showQuickActions = messages.length <= 1;

  return (
    <Box
      sx={{
        height: 'calc(100vh - 120px)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* 消息列表区域 */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          py: 2,
        }}
      >
        <Stack spacing={2} sx={{ px: 2 }}>
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              <Box sx={{ display: 'flex', maxWidth: '70%', gap: 1 }}>
                {message.role === 'assistant' && (
                  <Avatar
                    sx={{
                      width: 36,
                      height: 36,
                      bgcolor: 'primary.main',
                    }}
                  >
                    <SmartToy fontSize="small" />
                  </Avatar>
                )}

                <Tooltip title={message.timestamp.toLocaleString()} arrow>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: message.role === 'user' ? 'primary.main' : 'grey.100',
                      color: message.role === 'user' ? 'white' : 'text.primary',
                    }}
                  >
                    <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                      {message.content}
                    </Typography>
                  </Paper>
                </Tooltip>

                {message.role === 'user' && (
                  <Avatar
                    sx={{
                      width: 36,
                      height: 36,
                      bgcolor: 'grey.400',
                    }}
                  >
                    <Person fontSize="small" />
                  </Avatar>
                )}
              </Box>
            </Box>
          ))}

          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Avatar
                  sx={{
                    width: 36,
                    height: 36,
                    bgcolor: 'primary.main',
                  }}
                >
                  <SmartToy fontSize="small" />
                </Avatar>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'grey.100',
                  }}
                >
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    正在思考...
                  </Typography>
                </Paper>
              </Box>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Stack>
      </Box>

      {/* 输入区域 */}
      <Box sx={{ borderTop: '1px solid', borderColor: 'divider' }}>
        {/* 快捷操作按钮 - 只在初始会话显示 */}
        {showQuickActions && !loading && (
          <Box sx={{ px: 2, pt: 1.5, pb: 1 }}>
            <Box sx={{ display: 'flex', gap: 0.75, flexWrap: 'wrap' }}>
              {quickActions.map((action) => (
                <Paper
                  key={action.id}
                  elevation={0}
                  onClick={() => handleQuickAction(action.prompt)}
                  sx={{
                    p: 0.75,
                    px: 1.25,
                    borderRadius: 1.5,
                    border: '1px solid',
                    borderColor: 'divider',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.5,
                    minWidth: 'fit-content',
                    '&:hover': {
                      borderColor: action.color,
                      bgcolor: `${action.color}08`,
                      transform: 'translateY(-1px)',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                    },
                  }}
                >
                  <Box sx={{ color: action.color, fontSize: 18 }}>
                    {action.icon}
                  </Box>
                  <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                    {action.title}
                  </Typography>
                </Paper>
              ))}
            </Box>
          </Box>
        )}

        {/* 输入框和按钮 */}
        <Box sx={{ pt: 2, px: 2, pb: 2 }}>
          <Stack direction="row" spacing={2} alignItems="flex-end">
            {/* 新会话按钮 */}
            <Button
              variant="outlined"
              onClick={handleNewChat}
              disabled={loading}
              sx={{
                borderRadius: 2,
                minWidth: 90,
                width: 90,
                height: 52,
                fontSize: '0.875rem',
                borderWidth: 2,
                px: 1,
                '&:hover': {
                  borderWidth: 2,
                },
              }}
              startIcon={<Add sx={{ fontSize: 18 }} />}
            >
              新会话
            </Button>

            <TextField
              fullWidth
              multiline
              maxRows={3}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入消息... (Enter发送, Shift+Enter换行)"
              disabled={loading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />

            <Button
              variant="contained"
              onClick={handleSend}
              disabled={loading || !input.trim()}
              sx={{
                borderRadius: 2,
                minWidth: 100,
                height: 52,
              }}
            >
              {loading ? '发送中' : (
                <>
                  发送 <Send sx={{ ml: 0.5, fontSize: 16 }} />
                </>
              )}
            </Button>
          </Stack>
        </Box>
      </Box>
    </Box>
  );
};
