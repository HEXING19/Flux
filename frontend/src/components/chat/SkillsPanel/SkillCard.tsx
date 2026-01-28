import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  Collapse,
  IconButton,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import type { SkillMetadata } from '../../../types/skill';
import { ExamplePromptChip } from './ExamplePromptChip';

interface SkillCardProps {
  skill: SkillMetadata;
  onPromptSelect: (prompt: string) => void;
}

export const SkillCard: React.FC<SkillCardProps> = ({ skill, onPromptSelect }) => {
  const [expanded, setExpanded] = useState(false);

  const handleToggleExpand = () => {
    setExpanded(!expanded);
  };

  return (
    <Paper
      elevation={0}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid',
        borderColor: 'divider',
        borderLeft: `4px solid ${skill.color}`,
        borderRadius: 2,
        transition: 'all 0.2s',
        cursor: 'pointer',
        '&:hover': {
          elevation: 2,
          borderColor: `${skill.color}40`,
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        },
      }}
      onClick={handleToggleExpand}
    >
      {/* Header */}
      <Box sx={{ p: 2 }}>
        {/* Icon and Name */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Typography
            sx={{
              fontSize: '1.5rem',
              lineHeight: 1,
            }}
          >
            {skill.icon}
          </Typography>
          <Typography
            variant="subtitle1"
            sx={{
              fontWeight: 600,
              flex: 1,
            }}
          >
            {skill.name}
          </Typography>
        </Box>

        {/* Description */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            fontSize: '0.875rem',
            lineHeight: 1.5,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {skill.description}
        </Typography>

        {/* Expand/Collapse Button */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleToggleExpand();
            }}
            sx={{ color: skill.color }}
          >
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
      </Box>

      {/* Expandable Section */}
      <Collapse in={expanded}>
        <Divider />
        <Box sx={{ p: 2 }}>
          {/* Capabilities */}
          {skill.capabilities && skill.capabilities.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: 0.5,
                  mb: 1,
                  display: 'block',
                }}
              >
                能力边界
              </Typography>
              {skill.capabilities.map((capability, index) => (
                <Box
                  key={index}
                  sx={{
                    mb: index < skill.capabilities!.length - 1 ? 1 : 0,
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 500,
                      fontSize: '0.875rem',
                      color: skill.color,
                    }}
                  >
                    • {capability.title}
                  </Typography>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ fontSize: '0.75rem' }}
                  >
                    {capability.description}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}

          {/* Example Prompts */}
          {skill.examplePrompts && skill.examplePrompts.length > 0 && (
            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: 0.5,
                  mb: 1,
                  display: 'block',
                }}
              >
                常见提示词
              </Typography>
              <Box
                onClick={(e) => e.stopPropagation()}
              >
                {skill.examplePrompts.map((prompt, index) => (
                  <ExamplePromptChip
                    key={index}
                    prompt={prompt}
                    skillColor={skill.color}
                    onSelect={onPromptSelect}
                  />
                ))}
              </Box>
            </Box>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};
