/**
 * Mode Toggle Button Component
 * Floating action button to switch between chat and cockpit modes
 */

import { Fab, Tooltip } from '@mui/material';
import { Dashboard } from '@mui/icons-material';
import type { ViewMode } from '../../types/cockpit';

interface ModeToggleButtonProps {
  currentMode: ViewMode;
  onToggle: () => void;
}

export function ModeToggleButton({ currentMode, onToggle }: ModeToggleButtonProps) {
  const isInChatMode = currentMode === 'chat';

  return (
    <Tooltip
      title={isInChatMode ? '切换到AI驾驶舱' : '切换到对话模式'}
      placement="left"
    >
      <Fab
        color="primary"
        onClick={onToggle}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1000,
          background: isInChatMode
            ? 'linear-gradient(135deg, #00bcd4 0%, #7c4dff 100%)'
            : 'linear-gradient(135deg, #7c4dff 0%, #00bcd4 100%)',
          '&:hover': {
            background: isInChatMode
              ? 'linear-gradient(135deg, #00acc1 0%, #651fff 100%)'
              : 'linear-gradient(135deg, #651fff 0%, #00acc1 100%)',
            boxShadow: '0 0 20px rgba(0, 188, 212, 0.6)',
          },
          transition: 'all 0.3s ease',
        }}
      >
        <Dashboard sx={{ fontSize: 28 }} />
      </Fab>
    </Tooltip>
  );
}
