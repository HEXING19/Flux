import React from 'react';
import {
  IconButton,
  Tooltip,
  Badge,
} from '@mui/material';
import {
  AutoAwesome,
} from '@mui/icons-material';
import { SCENARIOS_CONFIG } from '../../config/scenarios';

interface ScenarioButtonProps {
  onScenarioStart: (scenarioId: string) => void;
  disabled?: boolean;
}

export const ScenarioButton: React.FC<ScenarioButtonProps> = ({
  onScenarioStart,
  disabled = false,
}) => {
  const handleClick = () => {
    // Start the first (and currently only) scenario
    const scenario = SCENARIOS_CONFIG[0];
    if (scenario) {
      onScenarioStart(scenario.id);
    }
  };

  const scenario = SCENARIOS_CONFIG[0];

  return (
    <Tooltip
      title={scenario ? `${scenario.name}\n${scenario.description}\n预计用时: ${scenario.estimatedTime}` : '场景任务'}
      arrow
    >
      <Badge
        badgeContent={scenario?.steps}
        color="secondary"
        overlap="circular"
        sx={{
          '& .MuiBadge-badge': {
            fontSize: '0.6rem',
            height: 16,
            minWidth: 16,
          },
        }}
      >
        <IconButton
          onClick={handleClick}
          disabled={disabled}
          sx={{
            bgcolor: 'secondary.main',
            color: 'white',
            '&:hover': {
              bgcolor: 'secondary.dark',
            },
            '&:disabled': {
              bgcolor: 'action.disabledBackground',
              color: 'text.disabled',
            },
          }}
        >
          <AutoAwesome />
        </IconButton>
      </Badge>
    </Tooltip>
  );
};
