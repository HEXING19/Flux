import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Alert,
  CircularProgress,
  Chip,
  Stack,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
  CheckCircle,
  Error,
  Warning,
} from '@mui/icons-material';
import type { ScenarioState } from '../../types/scenario';
import {
  THREAT_LEVELS,
} from '../../types/scenario';

interface ScenarioProgressDialogProps {
  open: boolean;
  state: ScenarioState;
  onConfirm: () => void;
  onCancel: () => void;
  onClose?: () => void;  // 新增：关闭按钮回调
  confirming?: boolean;
}

export const ScenarioProgressDialog: React.FC<ScenarioProgressDialogProps> = ({
  open,
  state,
  onConfirm,
  onCancel,
  onClose,
  confirming = false,
}) => {
  // 添加调试日志
  console.log('ScenarioProgressDialog render, open:', open, 'state:', state);

  // 管理每个步骤的展开/收起状态
  const [expandedSteps, setExpandedSteps] = useState<Record<number, boolean>>({
    0: true,  // Step1 默认展开
    1: true,  // Step2 默认展开
    2: true,  // Step3 默认展开
    3: true,  // Step4 默认展开
  });

  // 当步骤状态完成时，自动展开该步骤
  React.useEffect(() => {
    if (state.step1Status === 'completed') {
      setExpandedSteps(prev => ({ ...prev, 0: true }));
    }
    if (state.step2Status === 'completed') {
      setExpandedSteps(prev => ({ ...prev, 1: true }));
    }
    if (state.step3Status === 'completed') {
      setExpandedSteps(prev => ({ ...prev, 2: true }));
    }
  }, [state.step1Status, state.step2Status, state.step3Status]);

  const toggleStep = (stepIndex: number) => {
    setExpandedSteps(prev => ({
      ...prev,
      [stepIndex]: !prev[stepIndex],
    }));
  };

  const renderStep1 = () => (
    <Step completed={state.step1Status === 'completed'} expanded={expandedSteps[0]}>
      <StepLabel
        error={state.step1Status === 'error'}
        onClick={() => state.step1Status !== 'loading' && toggleStep(0)}
        sx={{ cursor: state.step1Status !== 'loading' ? 'pointer' : 'default' }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          查询今日严重、高危事件
          {state.step1Status !== 'loading' && (
            <IconButton size="small" onClick={(e) => { e.stopPropagation(); toggleStep(0); }}>
              {expandedSteps[0] ? <ExpandMoreIcon /> : <ChevronRightIcon />}
            </IconButton>
          )}
        </Box>
      </StepLabel>
      <StepContent>
        <Collapse in={expandedSteps[0]} timeout="auto" unmountOnExit>
          {state.step1Status === 'loading' && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
              <CircularProgress size={20} />
              <Typography variant="body2">正在查询今日未处置的严重、高危事件...</Typography>
            </Box>
          )}
          {state.step1Status === 'completed' && state.step1Data && (
            <Box sx={{ mt: 1 }}>
              <Alert severity="success" sx={{ mb: 1 }}>
                查询到 {state.step1Data.total || 0} 条未处置的严重、高危事件
              </Alert>
              {state.step1Data.incidents && state.step1Data.incidents.length > 0 && (
                <Box sx={{ bgcolor: 'background.paper', borderRadius: 1, p: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    事件列表（前5条）：
                  </Typography>
                  <List dense>
                    {state.step1Data.incidents.slice(0, 5).map((incident, i) => (
                      <ListItem key={i} divider sx={{ py: 0.5 }}>
                        <ListItemText
                          primary={incident.name}
                          secondary={`ID: ${incident.uuId} | 主机: ${incident.hostIp || '未知'}`}
                        />
                      </ListItem>
                    ))}
                    {state.step1Data.incidents.length > 5 && (
                      <Typography variant="caption" color="text.secondary" sx={{ pl: 2 }}>
                        ...还有 {state.step1Data.incidents.length - 5} 条事件
                      </Typography>
                    )}
                  </List>
                </Box>
              )}
            </Box>
          )}
          {state.step1Status === 'error' && (
            <Alert severity="error">查询失败</Alert>
          )}
        </Collapse>
      </StepContent>
    </Step>
  );

  const renderStep2 = () => (
    <Step completed={state.step2Status === 'completed'} expanded={expandedSteps[1]}>
      <StepLabel
        error={state.step2Status === 'error'}
        onClick={() => state.step2Status !== 'loading' && toggleStep(1)}
        sx={{ cursor: state.step2Status !== 'loading' ? 'pointer' : 'default' }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          分析Top 10事件
          {state.step2Status !== 'loading' && (
            <IconButton size="small" onClick={(e) => { e.stopPropagation(); toggleStep(1); }}>
              {expandedSteps[1] ? <ExpandMoreIcon /> : <ChevronRightIcon />}
            </IconButton>
          )}
        </Box>
      </StepLabel>
      <StepContent>
        <Collapse in={expandedSteps[1]} timeout="auto" unmountOnExit>
          {state.step2Status === 'loading' && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
              <CircularProgress size={20} />
              <Typography variant="body2">正在分析Top 10事件详情和IP实体...</Typography>
            </Box>
          )}
          {state.step2Status === 'completed' && state.step2Data && (
            <Box sx={{ mt: 1 }}>
              {/* Top 10场景：显示事件汇总 */}
              {state.step2Data.incident_details && (
                <Box>
                  <Alert severity="info" sx={{ mb: 1 }}>
                    已分析 {state.step2Data.incident_details.filter(d => d.success).length}/{state.step2Data.incident_details.length} 个事件
                  </Alert>
                  <Box sx={{ bgcolor: 'background.paper', borderRadius: 1, p: 1, maxHeight: 300, overflow: 'auto' }}>
                    <List dense>
                      {state.step2Data.incident_details.map((detail, i) => (
                        <ListItem key={i} divider sx={{ py: 1 }}>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                                <Typography variant="subtitle2">
                                  {detail.incident.name}
                                </Typography>
                                {detail.success && detail.risk_assessment ? (
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                    <Chip
                                      size="small"
                                      label={THREAT_LEVELS[detail.risk_assessment.risk_level] || '未知'}
                                      color={
                                        detail.risk_assessment.risk_level >= 3 ? 'error' :
                                        detail.risk_assessment.risk_level >= 2 ? 'warning' : 'default'
                                      }
                                    />
                                    {detail.risk_assessment.risk_reasoning && (
                                      <Typography variant="caption" color="text.secondary">
                                        {detail.risk_assessment.risk_reasoning}
                                      </Typography>
                                    )}
                                  </Box>
                                ) : detail.success ? (
                                  <Chip size="small" label="已分析" color="info" />
                                ) : (
                                  <Chip size="small" label="分析失败" color="error" />
                                )}
                              </Box>
                            }
                            secondary={`ID: ${detail.incident.uuId} | 主机: ${detail.incident.hostIp || '未知'}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                </Box>
              )}
              {/* 单事件场景：向后兼容 */}
              {state.step2Data.proof && !state.step2Data.incident_details && (
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {state.step2Data.proof.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      ID: {state.incidentId}
                    </Typography>
                    {state.step2Data.proof.hostIp && (
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        主机IP: {state.step2Data.proof.hostIp}
                      </Typography>
                    )}
                    {state.step2Data.proof.incidentTimeLines && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" color="text.secondary">
                          攻击时间线（最近3条）:
                        </Typography>
                        {state.step2Data.proof.incidentTimeLines.slice(0, 3).map((timeline, i) => (
                          <Box key={i} sx={{ mt: 1 }}>
                            <Typography variant="body2" component="div">
                              {timeline.stage}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {timeline.time}
                              {timeline.score !== undefined && ` • ${timeline.score}分`}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              )}
            </Box>
          )}
        </Collapse>
      </StepContent>
    </Step>
  );

  const renderStep3 = () => (
    <Step completed={state.step3Status === 'completed'} expanded={expandedSteps[2]}>
      <StepLabel
        error={state.step3Status === 'error'}
        onClick={() => state.step3Status !== 'loading' && toggleStep(2)}
        sx={{ cursor: state.step3Status !== 'loading' ? 'pointer' : 'default' }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          查看IP威胁情报
          {state.step3Status !== 'loading' && (
            <IconButton size="small" onClick={(e) => { e.stopPropagation(); toggleStep(2); }}>
              {expandedSteps[2] ? <ExpandMoreIcon /> : <ChevronRightIcon />}
            </IconButton>
          )}
        </Box>
      </StepLabel>
      <StepContent>
        <Collapse in={expandedSteps[2]} timeout="auto" unmountOnExit>
          {state.step3Status === 'loading' && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
              <CircularProgress size={20} />
              <Typography variant="body2">正在提取威胁IP并分析威胁情报...</Typography>
            </Box>
          )}
          {state.step3Status === 'completed' && state.step3Data?.ip_details && (
            <Box sx={{ mt: 1 }}>
              {state.step3Data.ip_details.length > 0 ? (
                state.step3Data.ip_details.map((entity, i) => (
                  <Card key={i} sx={{ mb: 1 }}>
                    <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                      <Stack direction="row" alignItems="center" spacing={1} mb={0.5}>
                        <Typography variant="subtitle2">
                          {entity.ip}
                        </Typography>
                        <Chip
                          size="small"
                          label={THREAT_LEVELS[entity.threat_level] || '未知'}
                          color={
                            entity.threat_level >= 3 ? 'error' :
                            entity.threat_level >= 2 ? 'warning' : 'default'
                          }
                        />
                      </Stack>
                      <Typography variant="body2" color="text.secondary">
                        位置: {entity.location}
                      </Typography>
                      {entity.tags.length > 0 && (
                        <Typography variant="caption" color="error">
                          标签: {entity.tags.join(', ')}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Alert severity="info">
                  该事件无外网IP实体
                </Alert>
              )}
            </Box>
          )}
        </Collapse>
      </StepContent>
    </Step>
  );

  const renderStep4 = () => {
    const isExecuting = state.executionStatus === 'executing';
    const isCompleted = ['success', 'partial_success', 'error'].includes(state.executionStatus);

    return (
      <Step expanded={expandedSteps[3]} completed={isCompleted}>
        <StepLabel
          onClick={() => state.step3Status === 'completed' && toggleStep(3)}
          sx={{ cursor: state.step3Status === 'completed' ? 'pointer' : 'default' }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            确认并执行处置
            {state.step3Status === 'completed' && (
              <IconButton size="small" onClick={(e) => { e.stopPropagation(); toggleStep(3); }}>
                {expandedSteps[3] ? <ExpandMoreIcon /> : <ChevronRightIcon />}
              </IconButton>
            )}
          </Box>
        </StepLabel>
        <StepContent>
          <Collapse in={expandedSteps[3]} timeout="auto" unmountOnExit>
            {/* 执行前：显示将要执行的操作 */}
            {state.step3Status === 'completed' && state.executionStatus === 'idle' && state.step3Data && (
              <Box sx={{ mt: 1 }}>
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    {state.step3Data.ai_summary}
                  </Typography>
                </Alert>

                <Typography variant="subtitle2" gutterBottom>
                  将要执行的操作：
                </Typography>
                <List dense>
                  {state.ipsToBlock.length > 0 && (
                    <ListItem>
                      <ListItemText
                        primary="IP封禁"
                        secondary={`IP: ${state.ipsToBlock.join(', ')} | 设备: 物联网安全网关 | 时长: 7天`}
                      />
                    </ListItem>
                  )}
                  <ListItem>
                    <ListItemText
                      primary="事件处置"
                      secondary={
                        state.ipsToBlock.length > 0
                          ? "状态: 已处置 | 备注: AI自动化闭环 - IP已封禁"
                          : "状态: 已处置 | 备注: AI自动化闭环"
                      }
                    />
                  </ListItem>
                </List>
              </Box>
            )}

            {/* 执行中：显示loading */}
            {isExecuting && (
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <CircularProgress size={24} />
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    正在执行处置操作...
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {state.ipsToBlock.length > 0
                      ? `正在封禁 ${state.ipsToBlock.length} 个IP并更新事件状态`
                      : '正在更新事件状态'}
                  </Typography>
                </Box>
              </Box>
            )}

            {/* 执行完成：显示结果 */}
            {isCompleted && state.executionResult && (
              <Box sx={{ mt: 2 }}>
                {/* 调试日志 */}
                {console.log('🐛 Debug - executionResult:', state.executionResult)}
                {console.log('🐛 Debug - executionResult.results:', state.executionResult.results)}
                {console.log('🐛 Debug - ip_block:', state.executionResult.results?.ip_block)}
                {console.log('🐛 Debug - incident_updates:', state.executionResult.results?.incident_updates)}

                {/* 整体状态Alert */}
                <Alert
                  severity={
                    state.executionStatus === 'success' ? 'success' :
                    state.executionStatus === 'partial_success' ? 'warning' : 'error'
                  }
                  sx={{ mb: 2 }}
                >
                  <Typography variant="subtitle2" gutterBottom>
                    {state.executionStatus === 'success' ? '✅ 处置成功' :
                     state.executionStatus === 'partial_success' ? '⚠️ 部分成功' :
                     '❌ 执行失败'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {state.executionStatus === 'success'
                      ? '所有操作均已成功完成'
                      : state.executionStatus === 'partial_success'
                      ? '部分操作成功完成，请查看详细信息'
                      : state.executionError || '执行过程中发生错误'}
                  </Typography>
                </Alert>

                {/* 详细结果列表 */}
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  执行详情：
                </Typography>
                <List dense>
                  {/* IP封禁结果 */}
                  {state.executionResult.results?.ip_block && (
                    <ListItem
                      divider
                      sx={{
                        bgcolor: 'background.paper',
                        borderRadius: 1,
                        mb: 1,
                        flexDirection: 'column',
                        alignItems: 'flex-start'
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 1 }}>
                        {state.executionResult.results.ip_block.success === state.executionResult.results.ip_block.total ? (
                          <CheckCircle color="success" sx={{ mr: 1 }} />
                        ) : (
                          <Error color="error" sx={{ mr: 1 }} />
                        )}
                        <Typography variant="subtitle2">
                          IP封禁: {state.executionResult.results.ip_block.success}/{state.executionResult.results.ip_block.total} 成功
                        </Typography>
                      </Box>

                      {/* 显示每个IP的封禁结果 */}
                      {state.executionResult.results.ip_block.details.map((detail, idx) => (
                        <Box key={idx} sx={{ pl: 4, py: 0.5, width: '100%' }}>
                          <Typography variant="body2" color="text.secondary">
                            {detail.ip}: {detail.success ? '✓ 成功' : '✗ 失败'}
                            {detail.error && (
                              <Typography component="span" color="error">
                                {' '}({detail.error})
                              </Typography>
                            )}
                          </Typography>
                        </Box>
                      ))}
                    </ListItem>
                  )}

                  {/* 事件处置结果 */}
                  {state.executionResult.results?.incident_updates && (
                    <ListItem
                      sx={{
                        bgcolor: 'background.paper',
                        borderRadius: 1,
                        flexDirection: 'column',
                        alignItems: 'flex-start'
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 1 }}>
                        {state.executionResult.results.incident_updates.failed === 0 ? (
                          <CheckCircle color="success" sx={{ mr: 1 }} />
                        ) : (
                          <Error color="error" sx={{ mr: 1 }} />
                        )}
                        <Typography variant="subtitle2">
                          事件处置: {state.executionResult.results.incident_updates.failed === 0 ? '成功' : '部分失败'}
                        </Typography>
                      </Box>

                      <Typography variant="body2" color="text.secondary" sx={{ pl: 4 }}>
                        总计: {state.executionResult.results.incident_updates.total} 条 |
                        成功: {state.executionResult.results.incident_updates.success} 条 |
                        失败: {state.executionResult.results.incident_updates.failed} 条
                      </Typography>

                      {/* 显示每个事件的更新结果 */}
                      {state.executionResult.results.incident_updates.details.map((detail, idx) => (
                        <Box key={idx} sx={{ pl: 4, py: 0.5, width: '100%' }}>
                          <Typography variant="body2" color="text.secondary">
                            事件 {idx + 1}: {detail.success ? '✓ 成功' : '✗ 失败'}
                            {detail.message && (
                              <Typography component="span" color="text.secondary">
                                {' '}{detail.message}
                              </Typography>
                            )}
                          </Typography>
                        </Box>
                      ))}
                    </ListItem>
                  )}
                </List>
              </Box>
            )}
          </Collapse>
        </StepContent>
      </Step>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onCancel}
      maxWidth="md"
      fullWidth
      slotProps={{
        paper: {
          sx: { minHeight: 600 }
        }
      }}
    >
      <DialogTitle>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Typography variant="h6" component="span">
            每日高危事件闭环
          </Typography>
        </Stack>
      </DialogTitle>

      <DialogContent>
        <Stepper activeStep={state.currentStep} orientation="vertical">
          {renderStep1()}
          {renderStep2()}
          {renderStep3()}
          {renderStep4()}
        </Stepper>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        {/* 执行前：显示 取消 和 确认 按钮 */}
        {state.executionStatus === 'idle' && (
          <>
            <Button onClick={onCancel} color="inherit" disabled={confirming}>
              取消
            </Button>
            <Button
              onClick={onConfirm}
              variant="contained"
              color="primary"
              disabled={state.currentStep !== 3 || confirming}
            >
              {confirming ? '执行中...' :
               state.ipsToBlock.length > 0 ? '确认封禁并关闭事件' :
               '调整事件处置状态'}
            </Button>
          </>
        )}

        {/* 执行中：禁用所有按钮 */}
        {state.executionStatus === 'executing' && (
          <Button disabled variant="contained">
            执行中...
          </Button>
        )}

        {/* 执行完成：显示 关闭 按钮 */}
        {['success', 'partial_success', 'error'].includes(state.executionStatus) && (
          <Button
            onClick={onClose}
            variant="contained"
            color={state.executionStatus === 'success' ? 'success' : 'primary'}
            startIcon={
              state.executionStatus === 'success' ? <CheckCircle /> :
              state.executionStatus === 'partial_success' ? <Warning /> : <Error />
            }
          >
            关闭
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};
