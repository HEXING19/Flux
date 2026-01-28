import React from 'react';
import { Chip, Tooltip } from '@mui/material';
import type { ExamplePrompt } from '../../../types/skill';

interface ExamplePromptChipProps {
  prompt: ExamplePrompt;
  skillColor: string;
  onSelect: (promptText: string) => void;
}

export const ExamplePromptChip: React.FC<ExamplePromptChipProps> = ({
  prompt,
  skillColor,
  onSelect,
}) => {
  const handleClick = () => {
    onSelect(prompt.chinese);
  };

  return (
    <Tooltip title={prompt.english || prompt.chinese} arrow>
      <Chip
        label={prompt.chinese}
        onClick={handleClick}
        sx={{
          m: 0.5,
          cursor: 'pointer',
          fontSize: '0.875rem',
          height: 32,
          backgroundColor: `${skillColor}12`,
          border: `1px solid ${skillColor}40`,
          color: 'text.primary',
          transition: 'all 0.2s',
          '&:hover': {
            backgroundColor: `${skillColor}24`,
            borderColor: skillColor,
            transform: 'translateY(-1px)',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          },
        }}
      />
    </Tooltip>
  );
};
