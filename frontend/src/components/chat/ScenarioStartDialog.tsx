import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Alert,
  Stack,
} from '@mui/material';
import {
  AutoAwesome,
  Schedule,
  PlayArrow,
} from '@mui/icons-material';

interface ScenarioStartDialogProps {
  open: boolean;
  scenarioId: string;
  onStart: () => void;
  onCancel: () => void;
}

export const ScenarioStartDialog: React.FC<ScenarioStartDialogProps> = ({
  open,
  scenarioId,
  onStart,
  onCancel,
}) => {
  return (
    <Dialog
      open={open}
      onClose={onCancel}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { minHeight: 400 }
      }}
    >
      <DialogTitle>
        <Stack direction="row" alignItems="center" spacing={1}>
          <AutoAwesome color="secondary" />
          <Typography variant="h6" component="span">
            每日高危事件闭环
          </Typography>
        </Stack>
      </DialogTitle>

      <DialogContent>
        {/* 场景描述 */}
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            自动查询今日未处置的严重、高危事件，分析Top 10事件，提供一键封禁和处置建议
          </Typography>
        </Alert>

        {/* 步骤概览 */}
        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
          执行步骤：
        </Typography>
        <List dense>
          <ListItem>
            <ListItemText
              primary="步骤1: 查询今日严重、高危事件"
              secondary="查询今天所有未处置的严重及高危事件"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="步骤2: 分析Top 10事件"
              secondary="使用AI分析事件详情、风险评估和IP实体信息"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="步骤3: 查看IP威胁情报"
              secondary="分析IP威胁等级和情报标签"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="步骤4: 确认并执行处置"
              secondary="并行执行IP封禁和事件状态更新"
            />
          </ListItem>
        </List>

        {/* 预计用时 */}
        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Schedule color="action" fontSize="small" />
          <Typography variant="caption" color="text.secondary">
            预计用时: 2-3分钟
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onCancel} color="inherit">
          取消
        </Button>
        <Button
          onClick={onStart}
          variant="contained"
          color="primary"
          startIcon={<PlayArrow />}
        >
          启动场景
        </Button>
      </DialogActions>
    </Dialog>
  );
};
