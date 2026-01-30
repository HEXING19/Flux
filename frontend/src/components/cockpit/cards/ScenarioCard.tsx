/**
 * Scenario Card Component
 * Displays a single scenario card with Material Design style
 */

import { Card, CardContent, Typography, Chip, Button, Box, Stack } from '@mui/material';
import { PlayArrow, Schedule, TaskAlt } from '@mui/icons-material';
import type { ScenarioConfig } from '../../../types/scenario';

interface ScenarioCardProps {
  scenario: ScenarioConfig;
  onStart: (scenarioId: string) => void;
  disabled?: boolean;
}

export function ScenarioCard({ scenario, onStart, disabled = false }: ScenarioCardProps) {
  return (
    <Card
      elevation={2}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'box-shadow 150ms ease-in-out',
        '&:hover': {
          elevation: 4,
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1, p: 2 }}>
        {/* Icon and Title */}
        <Box sx={{ mb: 2 }}>
          <Typography
            variant="h3"
            sx={{
              fontSize: '2rem',
              mb: 1,
            }}
          >
            {scenario.icon}
          </Typography>
          <Typography
            variant="h6"
            gutterBottom
            sx={{
              fontWeight: 400,
            }}
          >
            {scenario.name}
          </Typography>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              lineHeight: 1.5,
            }}
          >
            {scenario.description}
          </Typography>
        </Box>

        {/* Stats Chips */}
        <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
          <Chip
            icon={<TaskAlt sx={{ fontSize: 16 }} />}
            label={`${scenario.steps}步`}
            size="small"
            variant="outlined"
            color="primary"
          />
          <Chip
            icon={<Schedule sx={{ fontSize: 16 }} />}
            label={scenario.estimatedTime}
            size="small"
            variant="outlined"
            color="secondary"
          />
        </Stack>

        {/* Start Button */}
        <Button
          variant="contained"
          fullWidth
          startIcon={<PlayArrow />}
          onClick={() => onStart(scenario.id)}
          disabled={disabled}
          sx={{ mt: 1 }}
        >
          启动自动驾驶
        </Button>
      </CardContent>
    </Card>
  );
}
