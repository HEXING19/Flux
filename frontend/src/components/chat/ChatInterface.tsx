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
import { AssetConfirmationDialog } from './AssetConfirmationDialog';
import { AssetSummaryTable } from './AssetSummaryTable';
import { IPBlockConfirmationDialog } from './IPBlockConfirmationDialog';
import { IPBlockStatusTable } from './IPBlockStatusTable';
import { IPBlockSummaryTable } from './IPBlockSummaryTable';
import { IncidentsListTable } from './IncidentsListTable';
import { IncidentProofTable } from './IncidentProofTable';
import { IncidentUpdateTable } from './IncidentUpdateTable';
import type { AssetParams } from '../../types/asset';
import type { AssetSummary } from '../../types/asset';
import type { IPBlockParams, IPBlockStatus, IPBlockSummary } from '../../types/ipblock';
import type { IncidentsListData } from '../../types/incidents';
import type { IncidentProofData } from '../../types/incidentProof';
import type { IncidentUpdateData } from '../../types/incidentUpdate';
import { parseErrorResponse, formatChatMessage, isStructuredError } from '../../utils/errorHelper';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'text' | 'asset_summary' | 'ipblock_status' | 'ipblock_summary' | 'incidents_list' | 'incident_proof' | 'incident_status_updated';
  data?: AssetSummary | IPBlockStatus | IPBlockSummary | IncidentsListData | IncidentProofData | IncidentUpdateData;
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

  // 资产确认对话框状态
  const [confirmationOpen, setConfirmationOpen] = useState(false);
  const [pendingParams, setPendingParams] = useState<AssetParams | null>(null);
  const [confirming, setConfirming] = useState(false);

  // IP封禁确认对话框状态
  const [ipBlockConfirmationOpen, setIPBlockConfirmationOpen] = useState(false);
  const [pendingIPBlockParams, setPendingIPBlockParams] = useState<IPBlockParams | null>(null);
  const [confirmingIPBlock, setConfirmingIPBlock] = useState(false);
  const [ipBlockError, setIPBlockError] = useState<string | null>(null);

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

      // 获取Flux认证信息
      const fluxAuthCode = localStorage.getItem('flux_auth_code');
      const fluxBaseUrl = localStorage.getItem('flux_base_url');

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
          auth_code: fluxAuthCode,  // 新增：Flux认证码
          flux_base_url: fluxBaseUrl,  // 新增：Flux API地址
        }),
      });

      if (!response.ok) {
        throw new Error('API请求失败');
      }

      const data = await response.json();

      // 检查响应类型
      if (data.type === 'asset_confirmation' && data.asset_params) {
        // 打开确认对话框
        setPendingParams(data.asset_params);
        setConfirmationOpen(true);

        // 添加临时消息
        const tempMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '请确认资产信息',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, tempMessage]);
      } else if (data.type === 'ipblock_confirmation' && data.block_params) {
        // 打开IP封禁确认对话框
        setPendingIPBlockParams(data.block_params);
        setIPBlockConfirmationOpen(true);
        setIPBlockError(null);

        // 添加临时消息
        const tempMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '请确认IP封禁信息',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, tempMessage]);
      } else if (data.type === 'ipblock_status' && data.status) {
        // 显示IP封禁状态
        const statusMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || 'IP封禁状态查询结果',
          timestamp: new Date(),
          type: 'ipblock_status',
          data: data.status,
        };
        setMessages((prev) => [...prev, statusMessage]);
      } else if (data.type === 'incidents_list' && data.incidents_data) {
        // 显示安全事件列表
        const incidentsMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '安全事件查询结果',
          timestamp: new Date(),
          type: 'incidents_list',
          data: data.incidents_data,
        };
        setMessages((prev) => [...prev, incidentsMessage]);
      } else if (data.type === 'incident_proof' && data.proof_data) {
        // 显示事件详情
        const proofMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '事件详情',
          timestamp: new Date(),
          type: 'incident_proof',
          data: data.proof_data,
        };
        setMessages((prev) => [...prev, proofMessage]);
      } else if (data.type === 'incident_status_updated' && data.update_result) {
        // 显示更新结果
        const updateResult: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '事件状态更新结果',
          timestamp: new Date(),
          type: 'incident_status_updated',
          data: {
            total: data.update_result.total || 0,
            succeededNum: data.update_result.succeededNum || 0,
            failedNum: (data.update_result.failedNum !== undefined ? data.update_result.failedNum : (data.update_result.total || 0) - (data.update_result.succeededNum || 0)),
            statusName: data.update_result.statusName || '已处置',
            statusValue: data.update_result.statusValue !== undefined ? data.update_result.statusValue : 40,
          },
        };
        setMessages((prev) => [...prev, updateResult]);
      } else {
        // 普通消息
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '抱歉,我现在无法回复。',
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      }
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

  // 处理资产确认
  const handleAssetConfirm = async (updatedParams: AssetParams) => {
    setConfirming(true);

    try {
      const fluxAuthCode = localStorage.getItem('flux_auth_code');
      const fluxBaseUrl = localStorage.getItem('flux_base_url');

      if (!fluxAuthCode || !fluxBaseUrl) {
        throw new Error('缺少 Flux 认证信息，请先登录');
      }

      const response = await fetch('http://localhost:8000/api/v1/llm/confirm-asset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          params: updatedParams,
          auth_code: fluxAuthCode,
          flux_base_url: fluxBaseUrl,
        }),
      });

      if (!response.ok) {
        throw new Error('API请求失败');
      }

      const result = await response.json();

      // 添加结果消息
      let resultMessage: Message;

      if (result.success) {
        // 成功添加资产
        resultMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '✅ 资产添加成功！',
          timestamp: new Date(),
          type: 'asset_summary',
          data: result.asset_data,
        };
      } else {
        // 处理错误 - 使用结构化错误信息
        const parsedError = parseErrorResponse(result);
        const errorMessage = formatChatMessage(parsedError);

        resultMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: errorMessage,
          timestamp: new Date(),
          type: 'text',
        };
      }

      setMessages((prev) => [...prev, resultMessage]);
      setConfirmationOpen(false);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ 添加失败：${error.message}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setConfirming(false);
    }
  };

  // 处理取消
  const handleAssetCancel = () => {
    setConfirmationOpen(false);
    setPendingParams(null);

    // 添加取消消息
    const cancelMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '已取消添加资产。',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, cancelMessage]);
  };

  // 处理IP封禁确认
  const handleIPBlockConfirm = async () => {
    if (!pendingIPBlockParams) return;

    setConfirmingIPBlock(true);
    setIPBlockError(null);

    try {
      const fluxAuthCode = localStorage.getItem('flux_auth_code');
      const fluxBaseUrl = localStorage.getItem('flux_base_url');

      if (!fluxAuthCode || !fluxBaseUrl) {
        throw new Error('缺少 Flux 认证信息，请先登录');
      }

      const response = await fetch('http://localhost:8000/api/v1/ipblock/confirm-block', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...pendingIPBlockParams,
          auth_code: fluxAuthCode,
          flux_base_url: fluxBaseUrl,
        }),
      });

      if (!response.ok) {
        throw new Error('API请求失败');
      }

      const result = await response.json();

      // 添加结果消息
      let resultMessage: Message;

      if (result.success) {
        // 成功封禁 - 创建摘要数据
        const summaryData: IPBlockSummary = {
          ip: pendingIPBlockParams.ip,
          device_name: pendingIPBlockParams.device_name,
          device_type: pendingIPBlockParams.device_type,
          block_type: pendingIPBlockParams.block_type,
          time_type: pendingIPBlockParams.time_type,
          time_value: pendingIPBlockParams.time_value,
          time_unit: pendingIPBlockParams.time_unit,
          reason: pendingIPBlockParams.reason,
          rule_count: result.data?.rule_count || 0,
          timestamp: Date.now(),
        };

        resultMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: pendingIPBlockParams.ip,
          timestamp: new Date(),
          type: 'ipblock_summary',
          data: summaryData,
        };
      } else {
        // 处理错误
        const errorMessage = result.error_info?.friendly_message || result.message || '封禁失败';
        setIPBlockError(errorMessage);

        resultMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `❌ 封禁失败：${errorMessage}`,
          timestamp: new Date(),
          type: 'text',
        };
      }

      setMessages((prev) => [...prev, resultMessage]);
      setIPBlockConfirmationOpen(false);
      setPendingIPBlockParams(null);
    } catch (error: any) {
      setIPBlockError(error.message);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ 封禁失败：${error.message}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setConfirmingIPBlock(false);
    }
  };

  // 处理IP封禁取消
  const handleIPBlockCancel = () => {
    setIPBlockConfirmationOpen(false);
    setPendingIPBlockParams(null);
    setIPBlockError(null);

    // 添加取消消息
    const cancelMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '已取消IP封禁操作。',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, cancelMessage]);
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
                      p: message.type === 'asset_summary' || message.type === 'ipblock_status' || message.type === 'ipblock_summary' ? 2 : 2,
                      borderRadius: 2,
                      bgcolor: message.role === 'user' ? 'primary.main' : 'grey.100',
                      color: message.role === 'user' ? 'white' : 'text.primary',
                      minWidth: message.type === 'asset_summary' || message.type === 'ipblock_status' || message.type === 'ipblock_summary' || message.type === 'incidents_list' || message.type === 'incident_proof' || message.type === 'incident_status_updated' ? '400px' : 'auto',
                    }}
                  >
                    {message.type === 'asset_summary' && message.data ? (
                      <AssetSummaryTable data={message.data as AssetSummary} />
                    ) : message.type === 'ipblock_status' && message.data ? (
                      <IPBlockStatusTable status={message.data as IPBlockStatus} ip={message.content} />
                    ) : message.type === 'ipblock_summary' && message.data ? (
                      <IPBlockSummaryTable data={message.data as IPBlockSummary} />
                    ) : message.type === 'incidents_list' && message.data ? (
                      <IncidentsListTable incidents={(message.data as IncidentsListData).items} total={(message.data as IncidentsListData).total} />
                    ) : message.type === 'incident_proof' && message.data ? (
                      <IncidentProofTable data={message.data as IncidentProofData} />
                    ) : message.type === 'incident_status_updated' && message.data ? (
                      <IncidentUpdateTable data={message.data as IncidentUpdateData} />
                    ) : (
                      <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                        {message.content}
                      </Typography>
                    )}
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

      {/* 资产确认对话框 */}
      <AssetConfirmationDialog
        open={confirmationOpen}
        params={pendingParams}
        onConfirm={handleAssetConfirm}
        onCancel={handleAssetCancel}
        loading={confirming}
      />

      {/* IP封禁确认对话框 */}
      <IPBlockConfirmationDialog
        open={ipBlockConfirmationOpen}
        params={pendingIPBlockParams}
        onConfirm={handleIPBlockConfirm}
        onCancel={handleIPBlockCancel}
        loading={confirmingIPBlock}
        error={ipBlockError}
      />
    </Box>
  );
};
