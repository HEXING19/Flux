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
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  Add,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { AssetConfirmationDialog } from './AssetConfirmationDialog';
import { AssetSummaryTable } from './AssetSummaryTable';
import { IPBlockConfirmationDialog } from './IPBlockConfirmationDialog';
import { IPBlockStatusTable } from './IPBlockStatusTable';
import { IPBlockSummaryTable } from './IPBlockSummaryTable';
import { IncidentsListTable } from './IncidentsListTable';
import { IncidentProofTable } from './IncidentProofTable';
import { IncidentUpdateTable } from './IncidentUpdateTable';
import { IncidentEntitiesTable } from './IncidentEntitiesTable';
import { SkillsPanel } from './SkillsPanel';
import { ScenarioProgressDialog } from './ScenarioProgressDialog';
import type { AssetParams } from '../../types/asset';
import type { AssetSummary } from '../../types/asset';
import type { IPBlockParams, IPBlockStatus, IPBlockSummary } from '../../types/ipblock';
import type { IncidentsListData } from '../../types/incidents';
import type { IncidentProofData } from '../../types/incidentProof';
import type { IncidentUpdateData } from '../../types/incidentUpdate';
import type { IncidentEntitiesData } from '../../types/incidentEntities';
import type { LogCountData } from '../../types/logCount';
import type { ScenarioState } from '../../types/scenario';
import type { ViewMode } from '../../types/cockpit';
import { LogCountTable } from './LogCountTable';
import { parseErrorResponse, formatChatMessage, isStructuredError } from '../../utils/errorHelper';
import { SecurityCockpit } from '../cockpit/SecurityCockpit';
import { ModeToggleButton } from '../cockpit/ModeToggleButton';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'text' | 'asset_summary' | 'ipblock_status' | 'ipblock_summary' | 'incidents_list' | 'incident_proof' | 'incident_status_updated' | 'incident_entities' | 'log_count' | 'scenario_start' | 'scenario_completed';
  data?: AssetSummary | IPBlockStatus | IPBlockSummary | IncidentsListData | IncidentProofData | IncidentUpdateData | IncidentEntitiesData | LogCountData | any;
}

export const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '您好!我是Flux-你的智能配置助手。我可以帮助您进行产品的安全配置、联动处置等任务。请问有什么可以帮您的吗?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>(Date.now().toString());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // View mode state
  const [viewMode, setViewMode] = useState<ViewMode>('chat');

  // 资产确认对话框状态
  const [confirmationOpen, setConfirmationOpen] = useState(false);
  const [pendingParams, setPendingParams] = useState<AssetParams | null>(null);
  const [confirming, setConfirming] = useState(false);

  // IP封禁确认对话框状态
  const [ipBlockConfirmationOpen, setIPBlockConfirmationOpen] = useState(false);
  const [pendingIPBlockParams, setPendingIPBlockParams] = useState<IPBlockParams | null>(null);
  const [confirmingIPBlock, setConfirmingIPBlock] = useState(false);
  const [ipBlockError, setIPBlockError] = useState<string | null>(null);

  // 场景任务状态
  const [scenarioState, setScenarioState] = useState<ScenarioState>({
    open: false,
    scenarioId: null,
    currentStep: 0,
    step1Status: 'idle',
    step2Status: 'idle',
    step3Status: 'idle',
    step1Data: null,
    step2Data: null,
    step3Data: null,
    incidentId: null,
    incidentIds: [],
    ipsToBlock: [],
    error: null,
  });
  const [confirmingScenario, setConfirmingScenario] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 清理SSE连接
  useEffect(() => {
    return () => {
      const eventSource = (window as any).scenarioEventSource;
      if (eventSource) {
        eventSource.close();
      }
    };
  }, []);

  const handleNewChat = () => {
    const newConversationId = Date.now().toString();
    setConversationId(newConversationId);
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: '您好!我是Flux-你的智能配置助手。我可以帮助您进行产品的安全配置、联动处置等任务。请问有什么可以帮您的吗?',
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
      } else if (data.type === 'incident_entities' && data.entities_data) {
        // DEBUG LOG
        console.log('DEBUG: Received incident_entities response', {
          type: data.type,
          has_entities_data: !!data.entities_data,
          entities_data_keys: data.entities_data ? Object.keys(data.entities_data) : null,
          entities_data: data.entities_data
        });

        // 显示IP实体列表
        const entitiesMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '事件外网IP实体',
          timestamp: new Date(),
          type: 'incident_entities',
          data: data.entities_data,
        };
        setMessages((prev) => [...prev, entitiesMessage]);
      } else if (data.type === 'log_count' && data.log_count_data) {
        // 显示日志统计结果
        const logCountMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '日志统计结果',
          timestamp: new Date(),
          type: 'log_count',
          data: data.log_count_data,
        };
        setMessages((prev) => [...prev, logCountMessage]);
      } else if (data.type === 'scenario_start' && data.scenario_data) {
        // 渐进式展示步骤进度
        // 先显示对话框，所有步骤为loading状态
        setScenarioState({
          open: true,
          scenarioId: 'daily-high-risk-closure',
          currentStep: 0,
          step1Status: 'loading',
          step2Status: 'loading',
          step3Status: 'loading',
          step1Data: null,
          step2Data: null,
          step3Data: null,
          incidentId: data.scenario_data.incident_ids?.[0] || null,
          incidentIds: data.scenario_data.incident_ids || [],
          ipsToBlock: data.scenario_data.ips_to_block,
          error: null,
        });

        // 保存步骤数据
        const step1Data = data.scenario_data.step1;
        const step2Data = data.scenario_data.step2;
        const step3Data = data.scenario_data.step3;

        // 步骤1完成（500ms后）
        setTimeout(() => {
          setScenarioState(prev => ({
            ...prev,
            currentStep: 1,
            step1Status: 'completed',
            step1Data: step1Data,
          }));
        }, 500);

        // 步骤2完成（1500ms后）
        setTimeout(() => {
          setScenarioState(prev => ({
            ...prev,
            currentStep: 2,
            step2Status: 'completed',
            step2Data: step2Data,
          }));
        }, 1500);

        // 步骤3完成（2500ms后）
        setTimeout(() => {
          setScenarioState(prev => ({
            ...prev,
            currentStep: 3,
            step3Status: 'completed',
            step3Data: step3Data,
          }));
        }, 2500);

        // 添加临时消息
        const tempMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '场景已启动，正在分析...',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, tempMessage]);
      } else if (data.type === 'scenario_completed' && data.scenario_result) {
        // 显示场景执行结果
        const resultMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || '场景执行完成',
          timestamp: new Date(),
          type: 'scenario_completed',
          data: data.scenario_result,
        };
        setMessages((prev) => [...prev, resultMessage]);
      } else {
        // DEBUG LOG - Check what type we received
        console.log('DEBUG: Falling through to else block', {
          data_type: data.type,
          has_entities_data: !!data.entities_data,
          data_keys: Object.keys(data),
          full_data: data
        });

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

  // 处理场景启动
  const handleScenarioStart = async (scenarioId: string) => {
    console.log('handleScenarioStart called with scenarioId:', scenarioId);
    try {
      // 直接启动场景，跳过确认对话框
      await handleScenarioStartConfirm();
      console.log('handleScenarioStartConfirm completed');
    } catch (error) {
      console.error('Error in handleScenarioStart:', error);
    }
  };

  // 处理场景启动确认
  const handleScenarioStartConfirm = async () => {
    console.log('handleScenarioStartConfirm called');

    // 1. 立即显示场景进度对话框（所有步骤loading状态）
    const newState = {
      open: true,
      scenarioId: 'daily-high-risk-closure',
      currentStep: 0,
      step1Status: 'loading',
      step2Status: 'loading',
      step3Status: 'loading',
      step1Data: null,
      step2Data: null,
      step3Data: null,
      incidentId: null,
      incidentIds: [],
      ipsToBlock: [],
      error: null,
    };
    console.log('Setting scenarioState to:', newState);
    setScenarioState(newState);
    console.log('scenarioState updated, open should be true now');

    // 2. 添加用户消息到聊天界面
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: '执行每日高危事件闭环场景',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      // 3. 从localStorage获取配置
      const llmConfigStr = localStorage.getItem('llmConfig');
      if (!llmConfigStr) {
        throw new Error('请先在设置页面配置大模型API');
      }
      const llmConfig = JSON.parse(llmConfigStr);
      const fluxAuthCode = localStorage.getItem('flux_auth_code');
      const fluxBaseUrl = localStorage.getItem('flux_base_url');

      // 4. 构建查询参数
      const params = new URLSearchParams({
        auth_code: fluxAuthCode || '',
        flux_base_url: fluxBaseUrl || '',
        provider: llmConfig.provider || '',
        api_key: llmConfig.apiKey || '',
        llm_base_url: llmConfig.baseUrl || '',
      });

      // 5. 建立SSE连接
      console.log('About to establish SSE connection');
      const eventSource = new EventSource(
        `http://localhost:8000/api/v1/llm/scenario/stream?${params.toString()}`
      );
      console.log('EventSource created:', eventSource);

      // 添加open事件监听器
      eventSource.addEventListener('open', () => {
        console.log('SSE connection opened successfully');
      });

      // 6. 监听step_complete事件
      eventSource.addEventListener('step_complete', (event: any) => {
        try {
          const data = JSON.parse(event.data);
          const step = data.step;
          const stepData = data.data;

          if (step === 1) {
            // Step 1完成
            const incidentCount = stepData.incidents?.length || 0;

            setScenarioState(prev => ({
              ...prev,
              currentStep: 1,
              step1Status: 'completed',
              step1Data: stepData,
              incidentIds: stepData.incidents?.map((i: any) => i.uuId) || [],
            }));

            // 如果没有事件，立即完成步骤2和步骤3，以便显示步骤4
            if (incidentCount === 0) {
              setTimeout(() => {
                setScenarioState(prev => ({
                  ...prev,
                  currentStep: 3,
                  step2Status: 'completed',
                  step2Data: { incident_details: [] },
                  step3Status: 'completed',
                  step3Data: {
                    ips_to_block: [],
                    ip_details: [],
                    ai_summary: '今日暂无未处置的严重、高危事件，无需处置'
                  },
                  ipsToBlock: []
                }));
              }, 500);
            }
          } else if (step === 2) {
            // Step 2完成
            setScenarioState(prev => ({
              ...prev,
              currentStep: 2,
              step2Status: 'completed',
              step2Data: stepData,
            }));
          } else if (step === 3) {
            // Step 3完成
            setScenarioState(prev => ({
              ...prev,
              currentStep: 3,
              step3Status: 'completed',
              step3Data: stepData,
              ipsToBlock: stepData.ips_to_block || [],
            }));
          }
        } catch (error) {
          console.error('Error parsing step_complete event:', error);
        }
      });

      // 7. 监听complete事件
      eventSource.addEventListener('complete', (event: any) => {
        try {
          const data = JSON.parse(event.data);
          eventSource.close();
          setLoading(false);

          // 添加完成消息
          const tempMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: '场景分析完成，请确认执行操作',
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, tempMessage]);
        } catch (error) {
          console.error('Error parsing complete event:', error);
        }
      });

      // 8. 监听error事件
      eventSource.addEventListener('error', (event: any) => {
        eventSource.close();
        setLoading(false);

        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `❌ 场景执行失败：${event.data?.error || '未知错误'}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);

        setScenarioState(prev => ({
          ...prev,
          step1Status: 'error',
          error: '场景执行失败',
        }));
      });

      // 9. 保存eventSource引用以便清理
      (window as any).scenarioEventSource = eventSource;

    } catch (error: any) {
      setLoading(false);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ 场景启动失败：${error.message}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  // 处理场景确认
  const handleScenarioConfirm = async () => {
    // 如果没有事件，直接关闭对话框并显示提示消息
    if (!scenarioState.incidentIds || scenarioState.incidentIds.length === 0) {
      setScenarioState({
        open: false,
        scenarioId: null,
        currentStep: 0,
        step1Status: 'idle',
        step2Status: 'idle',
        step3Status: 'idle',
        step1Data: null,
        step2Data: null,
        step3Data: null,
        incidentId: null,
        incidentIds: [],
        ipsToBlock: [],
        error: null,
      });

      const infoMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '✅ 今日暂无未处置的严重、高危事件，无需执行处置操作',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, infoMessage]);
      return;
    }

    setConfirmingScenario(true);

    try {
      const fluxAuthCode = localStorage.getItem('flux_auth_code');
      const fluxBaseUrl = localStorage.getItem('flux_base_url');

      if (!fluxAuthCode || !fluxBaseUrl) {
        throw new Error('缺少 Flux 认证信息');
      }

      // 构造确认消息
      const confirmMessage = `确认执行场景处置：事件ID ${scenarioState.incidentIds.join(', ')}，封禁IP ${scenarioState.ipsToBlock.join(', ')}`;

      const userMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'user',
        content: confirmMessage,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);

      const llmConfigStr = localStorage.getItem('llmConfig');
      if (!llmConfigStr) {
        throw new Error('请先在设置页面配置大模型API');
      }

      const llmConfig = JSON.parse(llmConfigStr);

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
          auth_code: fluxAuthCode,
          flux_base_url: fluxBaseUrl,
        }),
      });

      if (!response.ok) {
        throw new Error('API请求失败');
      }

      const data = await response.json();

      // 关闭场景对话框
      setScenarioState({
        open: false,
        scenarioId: null,
        currentStep: 0,
        step1Status: 'idle',
        step2Status: 'idle',
        step3Status: 'idle',
        step1Data: null,
        step2Data: null,
        step3Data: null,
        incidentId: null,
        incidentIds: [],
        ipsToBlock: [],
        error: null,
      });

      // 添加结果消息
      const resultMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: data.message || '场景执行完成',
        timestamp: new Date(),
        type: data.type || 'text',
        data: data.scenario_result,
      };

      setMessages((prev) => [...prev, resultMessage]);

    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: `❌ 场景执行失败：${error.message}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);

      // 关闭场景对话框
      setScenarioState(prev => ({ ...prev, open: false }));
    } finally {
      setConfirmingScenario(false);
    }
  };

  // 处理场景取消
  const handleScenarioCancel = () => {
    setScenarioState({
      open: false,
      scenarioId: null,
      currentStep: 0,
      step1Status: 'idle',
      step2Status: 'idle',
      step3Status: 'idle',
      step1Data: null,
      step2Data: null,
      step3Data: null,
      incidentId: null,
      incidentIds: [],
      ipsToBlock: [],
      error: null,
    });

    // 添加取消消息
    const cancelMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '已取消场景任务。',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, cancelMessage]);
  };

  // Toggle view mode function
  const toggleViewMode = () => {
    setViewMode((prev) => (prev === 'chat' ? 'cockpit' : 'chat'));
  };

  // Render cockpit mode
  if (viewMode === 'cockpit') {
    return (
      <>
        <SecurityCockpit
          onScenarioStart={handleScenarioStart}
          onModeChange={toggleViewMode}
        />
        <ModeToggleButton currentMode={viewMode} onToggle={toggleViewMode} />

        {/* 场景任务进度对话框 */}
        <ScenarioProgressDialog
          open={scenarioState.open}
          state={scenarioState}
          onConfirm={handleScenarioConfirm}
          onCancel={handleScenarioCancel}
          confirming={confirmingScenario}
        />
      </>
    );
  }

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
                      minWidth: message.type === 'asset_summary' || message.type === 'ipblock_status' || message.type === 'ipblock_summary' || message.type === 'incidents_list' || message.type === 'incident_proof' || message.type === 'incident_status_updated' || message.type === 'incident_entities' ? '400px' : 'auto',
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
                    ) : message.type === 'incident_entities' && message.data ? (
                      <IncidentEntitiesTable
                        entities={(message.data as IncidentEntitiesData).item || []}
                        incidentId={message.content}
                      />
                    ) : message.type === 'log_count' && message.data ? (
                      <LogCountTable data={message.data as LogCountData} />
                    ) : message.type === 'scenario_completed' && message.data ? (
                      <Box sx={{ width: '100%' }}>
                        <Alert
                          severity={
                            (message.data as any).partial_success ? 'warning' :
                            (message.data as any).ip_block?.success === (message.data as any).ip_block?.total ? 'success' : 'error'
                          }
                          sx={{ mb: 2 }}
                        >
                          <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                            {message.content}
                          </Typography>
                        </Alert>

                        <Divider sx={{ my: 2 }} />

                        <Typography variant="subtitle2" gutterBottom>
                          执行结果：
                        </Typography>
                        <List dense>
                          {(message.data as any).ip_block?.total > 0 && (
                            <ListItem>
                              {(message.data as any).ip_block?.success === (message.data as any).ip_block?.total ? (
                                <CheckCircle color="success" sx={{ mr: 1 }} />
                              ) : (
                                <Error color="error" sx={{ mr: 1 }} />
                              )}
                              <ListItemText
                                primary={`IP封禁: ${(message.data as any).ip_block?.success}/${(message.data as any).ip_block?.total} 成功`}
                                secondary={(message.data as any).ip_block?.details?.map((d: any) =>
                                  `${d.ip}: ${d.success ? '✓' : '✗'}${d.error ? ` (${d.error})` : ''}`
                                ).join(' | ')}
                              />
                            </ListItem>
                          )}
                          <ListItem>
                            {(message.data as any).incident_update?.success ? (
                              <CheckCircle color="success" sx={{ mr: 1 }} />
                            ) : (
                              <Error color="error" sx={{ mr: 1 }} />
                            )}
                            <ListItemText
                              primary={`事件处置: ${(message.data as any).incident_update?.success ? '成功' : '失败'}`}
                              secondary={(message.data as any).incident_update?.message}
                            />
                          </ListItem>
                        </List>
                      </Box>
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
        {/* 输入框和按钮 */}
        <Box sx={{ px: 2, py: 2 }}>
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

            {/* Skills Panel */}
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <SkillsPanel onPromptSelect={setInput} />
            </Box>

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

      {/* 场景任务进度对话框 */}
      <ScenarioProgressDialog
        open={scenarioState.open}
        state={scenarioState}
        onConfirm={handleScenarioConfirm}
        onCancel={handleScenarioCancel}
        confirming={confirmingScenario}
      />

      {/* 场景启动确认对话框 */}
      {/* Mode Toggle Button - Only show in chat mode */}
      <ModeToggleButton currentMode={viewMode} onToggle={toggleViewMode} />
    </Box>
  );
};
