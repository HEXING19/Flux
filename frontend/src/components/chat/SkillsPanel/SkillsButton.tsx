import React from 'react';
import { Button, Tooltip } from '@mui/material';
import { TipsAndUpdates } from '@mui/icons-material';

interface SkillsButtonProps {
  onClick: () => void;
}

export const SkillsButton: React.FC<SkillsButtonProps> = ({ onClick }) => {
  return (
    <Tooltip title="查看可用技能" arrow>
      <Button
        variant="outlined"
        onClick={onClick}
        startIcon={<TipsAndUpdates sx={{ fontSize: 18 }} />}
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
      >
        技能
      </Button>
    </Tooltip>
  );
};
