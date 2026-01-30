/**
 * Scenario Cards Panel Component
 * Displays scenario cards in a vertical stack layout
 */

import { Box, Typography, Stack, Alert } from '@mui/material';
import { RocketLaunch } from '@mui/icons-material';
import { ScenarioCard } from '../cards/ScenarioCard';
import { SCENARIOS_CONFIG } from '../../../config/scenarios';

interface ScenarioCardsPanelProps {
  onScenarioStart: (scenarioId: string) => void;
  disabled?: boolean;
}

export function ScenarioCardsPanel({ onScenarioStart, disabled = false }: ScenarioCardsPanelProps) {
  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <RocketLaunch sx={{ color: 'primary.main', fontSize: '1.5rem' }} />
        <Typography variant="h6" component="h2">
          AI自动驾驶场景
        </Typography>
      </Box>

      {/* Vertical Stack of Scenario Cards */}
      <Stack spacing={2}>
        {SCENARIOS_CONFIG.map((scenario) => (
          <ScenarioCard
            key={scenario.id}
            scenario={scenario}
            onStart={onScenarioStart}
            disabled={disabled}
          />
        ))}
      </Stack>

      {/* Empty State (when no scenarios) */}
      {SCENARIOS_CONFIG.length === 0 && (
        <Alert severity="info">
          暂无可用场景，场景配置将在后续版本中提供
        </Alert>
      )}
    </Box>
  );
}
